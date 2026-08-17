from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceMetadata:
    """Identifies where a chunk of knowledge came from."""

    source_id: str
    source_type: str  # resume | project | github
    title: str
    file_path: str
    category: str = ""  # projects | skills | leadership | education | achievements | github | resume
    section: str | None = None
    url: str | None = None
    chunk_index: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: SourceMetadata


@dataclass(frozen=True)
class RetrievalHit:
    chunk: DocumentChunk
    score: float

    @property
    def citation_label(self) -> str:
        meta = self.chunk.metadata
        parts = [meta.title]
        if meta.section:
            parts.append(meta.section)
        return " — ".join(parts)


@dataclass
class CitationPayload:
    """Structured citation data emitted to the frontend for future UI."""

    query: str
    sources: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"query": self.query, "sources": self.sources}
