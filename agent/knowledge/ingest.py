from __future__ import annotations

import argparse
from pathlib import Path

from .retriever import INDEX_DIR, SOURCES_DIR, KnowledgeRetriever


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest knowledge sources into the vector index.")
    parser.add_argument(
        "--sources",
        type=Path,
        default=SOURCES_DIR,
        help="Directory containing markdown knowledge sources",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=INDEX_DIR,
        help="Directory where the vector index is stored",
    )
    args = parser.parse_args()

    if not args.sources.exists():
        raise SystemExit(f"Sources directory not found: {args.sources}")

    retriever = KnowledgeRetriever(index_dir=args.index)
    chunk_count = retriever.ingest_sources(args.sources)
    print(f"Ingested {chunk_count} chunks from {args.sources}")


if __name__ == "__main__":
    main()
