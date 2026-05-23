"""
Document AI — Main Entry Point
CLI interface for document processing, classification, extraction, and search.

Usage:
    python main.py process --folder ./sample_docs
    python main.py search --query "invoices due in January"
    python main.py ask --question "What is the total amount on invoice INV-1234?"
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from processor import ingest_documents
from classifier import classify_document
from extractor import extract_fields
from retrieval import DocumentRetriever, LocalQA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

OUTPUT_FILE = "output/output.json"


def run_pipeline(folder: str, use_ml: bool = False) -> dict:
    """Full document processing pipeline."""
    os.makedirs("output", exist_ok=True)

    # 1. Ingest
    logger.info("=" * 50)
    logger.info("STEP 1: Ingesting documents...")
    documents = ingest_documents(folder)

    if not documents:
        logger.error("No documents found in the specified folder.")
        sys.exit(1)

    # 2. Classify + Extract
    logger.info("=" * 50)
    logger.info("STEP 2: Classifying and extracting fields...")
    results = {}

    for filename, text in documents.items():
        logger.info(f"  → {filename}")

        # Classify
        classification = classify_document(text, use_ml=use_ml)
        doc_class = classification["class"]

        # Extract fields
        fields = extract_fields(doc_class, text)

        # Build result entry
        entry = {"class": doc_class, **fields}
        results[filename] = entry

        logger.info(
            f"     Class: {doc_class} "
            f"(confidence={classification['confidence']}, method={classification['method']})"
        )

    # 3. Save output.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info("=" * 50)
    logger.info(f"✅ output.json saved → {OUTPUT_FILE}")
    print(json.dumps(results, indent=2))

    # 4. Build search index
    logger.info("=" * 50)
    logger.info("STEP 3: Building semantic search index...")
    retriever = DocumentRetriever()
    retriever.build_index(documents)
    logger.info("✅ Search index built.")

    return results


def run_search(query: str, top_k: int = 5):
    """Semantic search over indexed documents."""
    retriever = DocumentRetriever()
    loaded = retriever.load_index()

    if not loaded:
        logger.error(
            "No index found. Run 'python main.py process --folder ./sample_docs' first."
        )
        sys.exit(1)

    logger.info(f"\n🔍 Query: {query}\n")
    results = retriever.search(query, top_k=top_k)

    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r['filename']}  (score={r['score']})")
        print(f"    {r['snippet']}")


def run_qa(question: str):
    """Local QA over retrieved document context (bonus feature)."""
    retriever = DocumentRetriever()
    loaded = retriever.load_index()

    if not loaded:
        logger.error("No index found. Run the process step first.")
        sys.exit(1)

    qa = LocalQA(retriever)
    logger.info(f"\n❓ Question: {question}\n")
    result = qa.answer(question)

    print(f"\n💡 Answer: {result['answer']}")
    print(f"📄 Sources: {', '.join(result['sources'])}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Document AI — Local Ingestion, Classification, Extraction & Search"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # process
    proc_parser = subparsers.add_parser("process", help="Ingest and process documents")
    proc_parser.add_argument(
        "--folder", default="./sample_docs", help="Folder containing PDF/TXT files"
    )
    proc_parser.add_argument(
        "--use-ml", action="store_true",
        help="Enable ML-based zero-shot classification (downloads model on first run)"
    )

    # search
    search_parser = subparsers.add_parser("search", help="Semantic search over documents")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--top-k", type=int, default=5, help="Number of results")

    # ask (bonus)
    qa_parser = subparsers.add_parser("ask", help="Ask a question (bonus QA feature)")
    qa_parser.add_argument("--question", required=True, help="Natural language question")

    args = parser.parse_args()

    if args.command == "process":
        run_pipeline(args.folder, use_ml=args.use_ml)
    elif args.command == "search":
        run_search(args.query, args.top_k)
    elif args.command == "ask":
        run_qa(args.question)


if __name__ == "__main__":
    main()
