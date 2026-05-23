"""
Retrieval System — Semantic Search
Uses SentenceTransformers for embeddings + FAISS for vector similarity search.
100% local, no API calls.
"""

import os
import json
import logging
import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

INDEX_PATH = "output/faiss_index.pkl"


class DocumentRetriever:
    def __init__(self):
        self.model = None
        self.index = None          # FAISS index
        self.doc_names: List[str] = []
        self.doc_texts: List[str] = []

    def _load_model(self):
        """Lazy-load embedding model."""
        if self.model is None:
            logger.info("Loading SentenceTransformer model (first run may download ~90MB)...")
            from sentence_transformers import SentenceTransformer
            # 'all-MiniLM-L6-v2' — tiny, fast, good quality
            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2",
                cache_folder="output/hf_cache",
            )
            logger.info("Model loaded.")

    def build_index(self, documents: Dict[str, str]):
        """
        Build FAISS index from {filename -> text} dict.
        Saves index to disk for reuse.
        """
        import faiss

        self._load_model()

        self.doc_names = list(documents.keys())
        self.doc_texts = list(documents.values())

        logger.info(f"Building embeddings for {len(self.doc_names)} documents...")

        # Chunk long docs to 512 tokens max (SentenceTransformer limit)
        snippets = [t[:2000] for t in self.doc_texts]
        embeddings = self.model.encode(snippets, show_progress_bar=True, batch_size=8)
        embeddings = np.array(embeddings, dtype="float32")

        # Build FAISS flat index (exact search — fast enough for <10k docs)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        # Persist
        os.makedirs("output", exist_ok=True)
        with open(INDEX_PATH, "wb") as f:
            pickle.dump({
                "doc_names": self.doc_names,
                "doc_texts": self.doc_texts,
                "embeddings": embeddings,
            }, f)

        logger.info(f"FAISS index built with {self.index.ntotal} vectors.")

    def load_index(self) -> bool:
        """Load pre-built index from disk if available."""
        import faiss

        if not Path(INDEX_PATH).exists():
            return False

        self._load_model()

        with open(INDEX_PATH, "rb") as f:
            data = pickle.load(f)

        self.doc_names = data["doc_names"]
        self.doc_texts = data["doc_texts"]
        embeddings = data["embeddings"].astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

        logger.info(f"Loaded FAISS index with {self.index.ntotal} documents.")
        return True

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Semantic search over indexed documents.
        Returns list of {filename, score, snippet}.
        """
        if self.index is None:
            raise RuntimeError("Index not built. Run build_index() first.")

        self._load_model()

        query_vec = self.model.encode([query], show_progress_bar=False)
        query_vec = np.array(query_vec, dtype="float32")

        distances, indices = self.index.search(query_vec, top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.doc_names):
                continue
            text = self.doc_texts[idx]
            snippet = text[:300].replace("\n", " ")
            results.append({
                "filename": self.doc_names[idx],
                "score": round(float(1 / (1 + dist)), 4),   # normalised similarity
                "snippet": snippet + "...",
            })

        return results


# ---------------------------------------------------------------------------
# Optional Bonus: Local QA with open-source LLM
# ---------------------------------------------------------------------------

class LocalQA:
    """
    Wraps a local HuggingFace seq2seq model for question answering
    over retrieved document context. Uses retriever to find relevant docs,
    then feeds them as context to a local LLM.

    Model: 'google/flan-t5-small' — instruction-tuned seq2seq model,
    small enough for CPU, handles Q&A prompts well.
    For better quality (but slower), use 'google/flan-t5-base'.
    """

    def __init__(self, retriever: DocumentRetriever, model_name: str = "google/flan-t5-small"):
        self.retriever = retriever
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.structured_data = None

    def _load_model(self):
        if self.model is None:
            logger.info(f"Loading QA model: {self.model_name} ...")
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            logger.info("QA model loaded.")

    def _generate(self, prompt: str) -> str:
        """Generate text from prompt using seq2seq model."""
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=128,
            num_beams=2,
            early_stopping=True,
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _load_structured_data(self) -> None:
        if self.structured_data is None:
            path = Path("output/output.json")
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        self.structured_data = json.load(f)
                except Exception:
                    self.structured_data = {}
            else:
                self.structured_data = {}

    def _answer_from_structured_data(self, question: str) -> Optional[Dict]:
        self._load_structured_data()
        q = question.lower()

        # Match INV-XXXX pattern
        invoice_match = re.search(r"\bINV[- ]?\d+\b", question, re.I)
        if invoice_match:
            invoice_id = invoice_match.group(0)
            for filename, record in self.structured_data.items():
                if record.get("invoice_number") and record["invoice_number"].lower() == invoice_id.lower():
                    if "amount" in q or "total" in q:
                        return {
                            "question": question,
                            "answer": f"The total amount on {invoice_id} is {record.get('total_amount')}",
                            "sources": [filename],
                        }
                    if "date" in q:
                        return {
                            "question": question,
                            "answer": f"The date on {invoice_id} is {record.get('date')}",
                            "sources": [filename],
                        }
                    if "company" in q or "who" in q:
                        return {
                            "question": question,
                            "answer": f"Invoice {invoice_id} is from {record.get('company')}",
                            "sources": [filename],
                        }
                    return {
                        "question": question,
                        "answer": f"Found invoice {invoice_id}: Number={record.get('invoice_number')}, "
                                  f"Date={record.get('date')}, Company={record.get('company')}, "
                                  f"Total={record.get('total_amount')}",
                        "sources": [filename],
                    }

        # Match other invoice number patterns (e.g., BSE-0099, AC-INV-8821)
        inv_pattern = re.search(r"\b([A-Z]{2,5}[-](?:INV[-]?)?\d{3,10})\b", question, re.I)
        if inv_pattern:
            inv_id = inv_pattern.group(1)
            for filename, record in self.structured_data.items():
                if record.get("invoice_number") and record["invoice_number"].lower() == inv_id.lower():
                    if "amount" in q or "total" in q:
                        return {
                            "question": question,
                            "answer": f"The total amount on {inv_id} is {record.get('total_amount')}",
                            "sources": [filename],
                        }
                    return {
                        "question": question,
                        "answer": f"Found invoice {inv_id}: Number={record.get('invoice_number')}, "
                                  f"Date={record.get('date')}, Company={record.get('company')}, "
                                  f"Total={record.get('total_amount')}",
                        "sources": [filename],
                    }

        # Resume queries by name
        for filename, record in self.structured_data.items():
            if record.get("class") == "Resume" and record.get("name"):
                name = record["name"].lower()
                if name in q:
                    if "experience" in q or "years" in q:
                        return {
                            "question": question,
                            "answer": f"{record['name']} has {record.get('experience_years')} years of experience.",
                            "sources": [filename],
                        }
                    if "email" in q:
                        return {
                            "question": question,
                            "answer": f"{record['name']}'s email is {record.get('email')}",
                            "sources": [filename],
                        }
                    if "phone" in q:
                        return {
                            "question": question,
                            "answer": f"{record['name']}'s phone number is {record.get('phone')}",
                            "sources": [filename],
                        }
                    return {
                        "question": question,
                        "answer": f"{record['name']}: Email={record.get('email')}, "
                                  f"Phone={record.get('phone')}, Experience={record.get('experience_years')} years",
                        "sources": [filename],
                    }

        return None

    def answer(self, question: str, top_k: int = 3) -> Dict:
        """
        Retrieve relevant docs, build context, and generate an answer.
        First tries structured data lookup for fast, accurate answers.
        Falls back to LLM-based generation over retrieved context.
        """
        # Fast structured lookup
        structured_answer = self._answer_from_structured_data(question)
        if structured_answer is not None:
            return structured_answer

        # LLM-based fallback
        self._load_model()

        results = self.retriever.search(question, top_k=top_k)
        if not results:
            return {"question": question, "answer": "No relevant documents found.", "sources": []}

        # Build context string
        context_parts = []
        for r in results:
            context_parts.append(f"[{r['filename']}]: {r['snippet']}")
        context = "\n\n".join(context_parts)

        prompt = (
            f"Answer the question based only on the provided document excerpts.\n\n"
            f"Documents:\n{context}\n\n"
            f"Question: {question}\n\nAnswer:"
        )

        answer_text = self._generate(prompt)

        return {
            "question": question,
            "answer": answer_text.strip(),
            "sources": [r["filename"] for r in results],
        }
