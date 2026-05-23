"""
Document Classifier
Classifies documents into: Invoice, Resume, Utility Bill, Other, Unclassifiable
Uses keyword heuristics as primary method + optional zero-shot HuggingFace model.
Keyword approach is fast, offline, and surprisingly accurate for structured docs.
"""

import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword rules — ordered by confidence
# ---------------------------------------------------------------------------
KEYWORD_RULES: Dict[str, list] = {
    "Invoice": [
        r"\binvoice\b", r"\binv[-\s]?\d+", r"\bbill to\b", r"\bpayment due\b",
        r"\btotal amount\b", r"\btotal due\b", r"\bamount due\b", r"\bsubtotal\b",
        r"\btax\b.*\btotal\b", r"\bpurchase order\b", r"\bline items?\b",
        r"\bremit\b", r"\bdue date\b.*\$", r"\bvendor\b.*\binvoice\b",
    ],
    "Resume": [
        r"\bresume\b", r"\bcurriculum vitae\b", r"\bcv\b",
        r"\bwork experience\b", r"\bprofessional experience\b",
        r"\beducation\b.*\bskills?\b", r"\bskills?\b.*\beducation\b",
        r"\bobjective\b.*\bexperience\b", r"\bcertification\b",
        r"\blinkedin\.com\b", r"\bgithub\.com\b",
        r"\bbach(?:elor)?(?:'s)?\b.*\b(?:science|arts|engineering)\b",
        r"\byears? of experience\b",
    ],
    "Utility Bill": [
        r"\butility\b", r"\belectric(?:ity)?\b.*\bbill\b",
        r"\bwater\s+bill\b", r"\bgas\s+bill\b", r"\bkwh\b", r"\bkilowatt\b",
        r"\baccount number\b.*\bdue\b", r"\bservice address\b",
        r"\bbilling period\b", r"\bmeter reading\b", r"\busage\b.*\bkwh\b",
        r"\belectric(?:al)? company\b", r"\benergy\b.*\bbill\b",
        r"\bwater services?\b", r"\bcustomer service\b.*\baccount\b",
        r"\bamount due\b.*\baccount\b", r"\bservice\b.*\baddress\b",
    ],
}

# Minimum keyword matches required to classify
MIN_MATCHES = 2


def _count_matches(text: str, patterns: list) -> int:
    text_lower = text.lower()
    return sum(1 for p in patterns if re.search(p, text_lower))


def classify_by_keywords(text: str) -> Tuple[str, float]:
    """
    Returns (label, confidence_score).
    confidence is the ratio of matched patterns to total patterns.
    """
    scores: Dict[str, int] = {}
    for label, patterns in KEYWORD_RULES.items():
        scores[label] = _count_matches(text, patterns)

    best_label = max(scores, key=lambda k: scores[k])
    best_count = scores[best_label]
    total_patterns = len(KEYWORD_RULES[best_label])

    if best_count < MIN_MATCHES:
        # Try with 1 match for short docs
        if best_count == 1 and len(text) < 500:
            return best_label, 0.4
        return "Other", 0.0

    confidence = min(best_count / total_patterns, 1.0)
    return best_label, round(confidence, 2)


def classify_document(text: str, use_ml: bool = False) -> Dict:
    """
    Main classification entry point.
    Returns dict with 'class' and 'confidence'.
    """
    if not text or len(text.strip()) < 30:
        return {"class": "Unclassifiable", "confidence": 0.0, "method": "rule"}

    # Detect binary/corrupted content — high ratio of non-alpha chars
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.35:
        return {"class": "Unclassifiable", "confidence": 0.0, "method": "rule"}

    label, confidence = classify_by_keywords(text)

    # Optional: boost with zero-shot ML model
    if use_ml and confidence < 0.6:
        try:
            ml_label, ml_conf = classify_with_zero_shot(text)
            if ml_conf > confidence:
                return {
                    "class": ml_label,
                    "confidence": ml_conf,
                    "method": "zero_shot_ml"
                }
        except Exception as e:
            logger.warning(f"ML classification failed: {e}")

    return {"class": label, "confidence": confidence, "method": "keyword_rule"}


def classify_with_zero_shot(text: str) -> Tuple[str, float]:
    """
    Uses HuggingFace zero-shot pipeline with a small local model.
    Downloads on first run, then cached offline.
    """
    from transformers import pipeline

    candidate_labels = ["invoice", "resume", "utility bill", "other document"]
    label_map = {
        "invoice": "Invoice",
        "resume": "Resume",
        "utility bill": "Utility Bill",
        "other document": "Other",
    }

    # Use a small, fast model
    classifier = pipeline(
        "zero-shot-classification",
        model="typeform/distilbart-mnli-12-3",
        device=-1  # CPU only
    )

    # Truncate to avoid token limits
    snippet = text[:1000]
    result = classifier(snippet, candidate_labels)

    top_label = result["labels"][0]
    top_score = result["scores"][0]

    return label_map.get(top_label, "Other"), round(top_score, 2)
