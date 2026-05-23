"""
Structured Data Extractor
Extracts fields from classified documents using regex + NLP heuristics.
No paid APIs used — all local pattern matching.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _search(pattern: str, text: str, group: int = 1, flags=re.IGNORECASE) -> Optional[str]:
    """Safe regex search returning first group or None."""
    m = re.search(pattern, text, flags)
    return m.group(group).strip() if m else None


def _clean_amount(raw: str) -> Optional[float]:
    """Convert '$1,234.56' or '1234.56' to float."""
    if not raw:
        return None
    cleaned = re.sub(r"[^\d.]", "", raw)
    try:
        return float(cleaned)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Per-type extractors
# ---------------------------------------------------------------------------

def extract_invoice_fields(text: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        "invoice_number": None,
        "date": None,
        "company": None,
        "total_amount": None,
    }

    # Invoice number
    fields["invoice_number"] = (
        _search(r"invoice\s*(?:number|no\.?|#)\s*[:\-]?\s*([A-Z0-9][A-Z0-9\-/]{2,20})", text)
        or _search(r"\bINV[-\s]?(\d{3,10})\b", text)
        or _search(r"Inv\s+No\.?\s*[:\-]?\s*([A-Z0-9\-]+)", text)
        or _search(r"\b([A-Z]{2,5}[-](?:INV|inv)?[-]?\d{3,10})\b", text)
    )

    # Date — multiple formats
    fields["date"] = (
        _search(r"(?:invoice\s+date|date)\s*[:\s]\s*(\d{1,2}[\-/\.]\w{3,9}[\-/\.]\d{2,4})", text)
        or _search(r"(?:invoice\s+date|date)\s*[:\s]\s*(\d{1,2}\s+\w+\s+\d{4})", text)
        or _search(r"(?:invoice\s+date|date)\s*[:\s]\s*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})", text)
        or _search(r"(?:invoice\s+date|date)\s*[:\s]+(\w+ \d{1,2},?\s*\d{4})", text)
        or _search(r"(?:date)\s*[:\s]\s*(\d{4}-\d{2}-\d{2})", text)
        or _search(r"(\d{4}-\d{2}-\d{2})", text)
        or _search(r"(\d{1,2}/\d{1,2}/\d{4})", text)
    )

    # Company — look for "Bill To" / "From" / first proper noun block
    raw_company = (
        _search(r"(?:from|vendor|company)[:\s]+([A-Z][A-Za-z0-9\s&,\.]{2,40}?)(?:\n|\|)", text)
        or _search(r"(?:bill\s+from|issued\s+by)[:\s]+([A-Z][A-Za-z0-9\s&,\.]{2,40}?)(?:\n|$)", text)
        or _search(r"(?:bill\s+to)[:\s]*\n([A-Z][A-Za-z0-9\s&,\.]{2,50}?)(?:\n)", text)
        or _search(r"^([A-Z][A-Za-z0-9\s&,\.]{5,50}(?:Ltd\.?|LLC|Inc\.?|Corp\.?|Co\.?|GROUP|SOLUTIONS|TECHNOLOGIES|CONSULTING|SUPPLIES|SERVICES|PRESS))[\s]*$", text, flags=re.MULTILINE | re.IGNORECASE)
    )
    fields["company"] = raw_company.split("\n")[0].strip() if raw_company else None

    # Total amount — handle Rs., AED, £, €, $ prefixes
    total_raw = (
        _search(r"(?:total\s+amount|amount\s+due|total\s+due|grand\s+total|balance\s+due)[:\s]*(?:Rs\.?|AED|USD|\$|£|€)?\s*([\d,]+\.?\d*)", text)
        or _search(r"(?:total)[:\s]*(?:Rs\.?|AED|USD|\$|£|€)\s*([\d,]+\.?\d*)", text)
        or _search(r"(?:Rs\.?|AED|USD|\$|£|€)\s*([\d,]+\.\d{2})\s*$", text, flags=re.MULTILINE)
    )
    fields["total_amount"] = _clean_amount(total_raw)

    return fields


def extract_resume_fields(text: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        "name": None,
        "email": None,
        "phone": None,
        "experience_years": None,
    }

    # Email
    fields["email"] = _search(
        r"([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})", text
    )

    # Phone — various formats
    fields["phone"] = (
        _search(r"(?:phone|tel|mobile|cell)[:\s]*(\+?[\d\s\(\)\-\.]{7,20})", text)
        or _search(r"(\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})", text)
        or _search(r"(\+\d{1,3}[\s\-]?\d{2,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})", text)
        or _search(r"(\+\d{1,3}[\s\-]?\d{3,14})", text)
        or _search(r"(\d{4}[\-]\d{7})", text)
    )
    if fields["phone"]:
        fields["phone"] = re.sub(r"\s+", "", fields["phone"]).strip()

    # Name — usually first non-empty line before contact info
    # Handle both Title Case and ALL CAPS names
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        # Skip lines that look like emails, URLs, phone numbers, or headers
        if "@" in line or "http" in line or "linkedin" in line or "github" in line:
            continue
        if re.match(r"^[\d\(\+]", line):
            continue
        # Match ALL CAPS names (e.g., SARA AHMED, MICHAEL OKONKWO, FATIMA AL-RASHIDI)
        if re.match(r"^[A-Z][A-Z\-\' ]+$", line) and 2 <= len(line.split()) <= 4:
            # Convert ALL CAPS to Title Case for clean output
            fields["name"] = line.title().replace("Al-", "Al-").strip()
            break
        # Match Title Case names (e.g., John Doe, Jane Smith)
        if re.match(r"^[A-Z][a-z]+(?:[\s\-][A-Z][a-z]+){1,3}$", line):
            fields["name"] = line
            break

    # Experience years — explicit mention
    exp_raw = (
        _search(r"(\d+)\+?\s+years?\s+(?:of\s+)?(?:professional\s+)?experience", text)
        or _search(r"experience[:\s]+(\d+)\s+years?", text)
    )
    if exp_raw:
        try:
            fields["experience_years"] = int(exp_raw)
        except ValueError:
            pass

    # Fallback: count year spans in work history
    if fields["experience_years"] is None:
        year_spans = re.findall(r"(\d{4})\s*[-–]\s*(\d{4}|present|current)", text, re.IGNORECASE)
        total = 0
        current_year = 2025
        for start, end in year_spans:
            try:
                s = int(start)
                e = current_year if end.lower() in ("present", "current") else int(end)
                total += max(0, e - s)
            except ValueError:
                pass
        if total > 0:
            fields["experience_years"] = total

    return fields


def extract_utility_bill_fields(text: str) -> Dict[str, Any]:
    fields: Dict[str, Any] = {
        "account_number": None,
        "date": None,
        "usage_kwh": None,
        "amount_due": None,
    }

    # Account number
    fields["account_number"] = (
        _search(r"account\s*(?:number|no\.?|#)[:\s]*([A-Z0-9\-]{4,20})", text)
        or _search(r"account[:\s]+(\d{6,20})", text)
    )

    # Date — try bill date, statement date, due date, then fallback
    fields["date"] = (
        _search(r"(?:bill\s+date|statement\s+date)[:\s]+(\d{1,2}\s+\w+\s+\d{4})", text)
        or _search(r"(?:bill\s+date|statement\s+date)[:\s]+(\d{1,2}[\s\/\-\.]\w+[\s\/\-\.]\d{2,4})", text)
        or _search(r"(?:bill(?:ing)?\s+date|due\s+date|statement\s+date)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})", text)
        or _search(r"(?:due\s+date)[:\s]+(\w+ \d{1,2},?\s*\d{4})", text)
        or _search(r"(?:issue\s+date|statement\s+date)[:\s]+(\d{4}-\d{2}-\d{2})", text)
        or _search(r"(\d{4}-\d{2}-\d{2})", text)
    )

    # Usage kWh — prefer labeled usage line, avoid raw meter readings
    kwh_raw = (
        _search(r"(?:usage|consumption|units?\s+consumed)[:\s]*([\d,]+\.?\d*)\s*kwh", text)
        or _search(r"([\d,]+\.?\d*)\s*kwh\b(?!\s*(?:equivalent|eq))", text)
    )
    if kwh_raw:
        try:
            fields["usage_kwh"] = float(kwh_raw.replace(",", ""))
        except ValueError:
            pass

    # Amount due — handle Rs., £, $, AED prefixes
    due_raw = (
        _search(r"(?:amount\s+due|total\s+(?:amount\s+)?due|please\s+pay)[:\s]*(?:Rs\.?|AED|USD|\$|£|€)?\s*([\d,]+\.?\d*)", text)
        or _search(r"(?:total)[:\s]*(?:Rs\.?|AED|USD|\$|£|€)\s*([\d,]+\.\d{2})", text)
    )
    fields["amount_due"] = _clean_amount(due_raw)

    return fields


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def extract_fields(doc_class: str, text: str) -> Dict[str, Any]:
    """
    Dispatch to the correct extractor based on document class.
    Returns empty dict for Other/Unclassifiable.
    """
    if doc_class == "Invoice":
        return extract_invoice_fields(text)
    elif doc_class == "Resume":
        return extract_resume_fields(text)
    elif doc_class == "Utility Bill":
        return extract_utility_bill_fields(text)
    else:
        return {}
