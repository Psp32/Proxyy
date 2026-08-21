from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import chromadb

from .chunker import chunk_sources_directory
from .models import DocumentChunk, RetrievalHit

COLLECTION_NAME = "digital_twin_knowledge"


class KnowledgeStore:
    def __init__(self, index_dir: Path) -> None:
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(index_dir))
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def chunk_count(self) -> int:
        try:
            return self._collection.count()
        except Exception:
            try:
                self._collection = self._client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                return self._collection.count()
            except Exception:
                return 0

    def reset(self) -> None:
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[_metadata_to_chroma(chunk) for chunk in chunks],
        )

    def search(
        self,
        query: str,
        top_k: int = 4,
        where: dict | None = None,
        category: str | None = None,
    ) -> list[RetrievalHit]:
        if self.chunk_count == 0:
            return []

        query_kwargs: dict = {
            "query_texts": [query],
            "n_results": min(top_k, self.chunk_count),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_kwargs["where"] = where
        elif category:
            query_kwargs["where"] = {"category": category}

        result = self._collection.query(**query_kwargs)

        hits: list[RetrievalHit] = []
        ids = result["ids"][0] if result["ids"] else []
        documents = result["documents"][0] if result["documents"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []

        for chunk_id, document, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            chunk = _chunk_from_chroma(chunk_id, document, metadata)
            score = max(0.0, 1.0 - float(distance))
            hits.append(RetrievalHit(chunk=chunk, score=score))

        return hits

    def ingest_sources(self, sources_root: Path) -> int:
        chunks = chunk_sources_directory(sources_root)
        self.reset()
        self.upsert_chunks(chunks)
        return len(chunks)


def _metadata_to_chroma(chunk: DocumentChunk) -> dict[str, str | int]:
    meta = chunk.metadata
    payload: dict[str, str | int] = {
        "source_id": meta.source_id,
        "source_type": meta.source_type,
        "title": meta.title,
        "file_path": meta.file_path,
        "category": meta.category,
        "chunk_index": meta.chunk_index,
    }
    if meta.section:
        payload["section"] = meta.section
    if meta.url:
        payload["url"] = meta.url
    return payload


def _chunk_from_chroma(
    chunk_id: str,
    document: str,
    metadata: Mapping[str, Any],
) -> DocumentChunk:
    from .models import SourceMetadata

    return DocumentChunk(
        chunk_id=chunk_id,
        text=document,
        metadata=SourceMetadata(
            source_id=str(metadata["source_id"]),
            source_type=str(metadata["source_type"]),
            title=str(metadata["title"]),
            file_path=str(metadata["file_path"]),
            category=str(metadata.get("category", "")),
            section=str(metadata["section"]) if metadata.get("section") else None,
            url=str(metadata["url"]) if metadata.get("url") else None,
            chunk_index=int(metadata.get("chunk_index", 0)),
        ),
    )
