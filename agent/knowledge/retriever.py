from __future__ import annotations

import json
import logging
from pathlib import Path

from livekit import rtc

from .models import CitationPayload, RetrievalHit
from .store import KnowledgeStore

logger = logging.getLogger("knowledge")

def _find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "knowledge" / "sources").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return Path(__file__).resolve().parents[2]


PROJECT_ROOT = _find_project_root()
SOURCES_DIR = PROJECT_ROOT / "knowledge" / "sources"
INDEX_DIR = PROJECT_ROOT / "knowledge" / "index"
CITATIONS_TOPIC = "citations"


class KnowledgeRetriever:
    def __init__(self, index_dir: Path = INDEX_DIR) -> None:
        self._store = KnowledgeStore(index_dir)

    @property
    def is_ready(self) -> bool:
        return self._store.chunk_count > 0

    @property
    def chunk_count(self) -> int:
        return self._store.chunk_count

    def search(self, query: str, top_k: int = 5) -> list[RetrievalHit]:
        categories, source_id_hint = _classify_intent(query)

        fetch_k = max(top_k * 2, 12)

        if source_id_hint:
            # Named project query — retrieve the most informative chunks for this specific project
            all_hits = self._store.search(query, top_k=fetch_k)
            candidates = [
                h for h in all_hits
                if h.chunk.metadata.source_id == source_id_hint
                or source_id_hint in h.chunk.metadata.source_id
            ]
            # Fallback: if vector search missed some chunks, query directly with the project name
            if len(candidates) < top_k:
                name_hits = self._store.search(source_id_hint, top_k=fetch_k)
                for h in name_hits:
                    if (
                        h.chunk.metadata.source_id == source_id_hint
                        or source_id_hint in h.chunk.metadata.source_id
                    ):
                        if not any(c.chunk.chunk_id == h.chunk.chunk_id for c in candidates):
                            candidates.append(h)
            candidates.sort(key=_rank_chunk_score, reverse=True)
            return candidates[:top_k]

        elif categories == ["projects"]:
            # Broad project query: return 3 main projects (Voxel, Loopin, GrocerSpy) + 1-2 side projects
            proj_fetch_k = 16
            main_candidates = self._store.search(
                f"{query} Voxel Loopin GrocerSpy", top_k=proj_fetch_k, category="projects"
            )
            side_candidates = self._store.search(
                f"{query} OpenAgriNet College Mess Turtle Proxy", top_k=proj_fetch_k, category="side_projects"
            )
            main_hits = _diversity_dedup(
                main_candidates, top_k=3, target_sources=["voxel", "loopin", "grocerspy"]
            )
            side_hits = _diversity_dedup(
                side_candidates,
                top_k=2,
                target_sources=["college_mess_webapp", "openagrinet_training_pipeline", "turtle", "proxy"],
            )
            return main_hits + side_hits

        elif len(categories) == 1:
            candidates = self._store.search(query, top_k=fetch_k, category=categories[0])
            return _diversity_dedup(candidates, top_k)
        else:
            candidates = self._store.search(query, top_k=fetch_k)
            candidates.sort(key=_rank_chunk_score, reverse=True)
            return _diversity_dedup(candidates, top_k)

    def ingest_sources(self, sources_root: Path = SOURCES_DIR) -> int:
        return self._store.ingest_sources(sources_root)

    def format_context(self, hits: list[RetrievalHit]) -> str:
        if not hits:
            return ""

        blocks: list[str] = []
        for hit in hits:
            meta = hit.chunk.metadata
            header = (
                f"[source_id={meta.source_id} | type={meta.source_type} | "
                f"title={meta.title}"
            )
            if meta.section:
                header += f" | section={meta.section}"
            if meta.url:
                header += f" | url={meta.url}"
            header += f" | chunk={meta.chunk_index}]"

            blocks.append(f"{header}\n{hit.chunk.text}")

        return "\n\n".join(blocks)

    def _infer_target_source_types(self, query: str) -> set[str]:
        categories, _ = _classify_intent(query)
        type_map: dict[str, set[str]] = {
            "projects": {"project", "side_project"},
            "side_projects": {"side_project", "project"},
            "github": {"github", "github_pr"},
            "skills": {"resume"},
            "education": {"resume"},
            "leadership": {"resume"},
            "achievements": {"resume"},
            "resume": {"resume"},
            "personal": {"resume"},
        }
        allowed: set[str] = set()
        for cat in categories:
            allowed.update(type_map.get(cat, {"resume"}))
        return allowed

    def build_citation_payload(self, query: str, hits: list[RetrievalHit]) -> CitationPayload:
        if _is_chitchat(query) or not hits:
            return CitationPayload(query=query, sources=[])

        categories, source_id_hint = _classify_intent(query)
        allowed_source_types = self._infer_target_source_types(query)

        # Strictly restrict citations to sources belonging to the queried category
        filtered_hits = [
            hit for hit in hits if hit.chunk.metadata.source_type in allowed_source_types
        ]
        if not filtered_hits:
            return CitationPayload(query=query, sources=[])

        # Require a solid relevance score before citing a source card in the UI
        min_score = 0.20 if not source_id_hint else 0.05
        filtered_hits = [h for h in filtered_hits if h.score >= min_score]
        if not filtered_hits:
            return CitationPayload(query=query, sources=[])

        best_by_source: dict[str, dict[str, object]] = {}
        for hit in filtered_hits:
            meta = hit.chunk.metadata

            # Clean raw chunk text for the UI excerpt (strip markdown headers)
            clean_lines = []
            for line in hit.chunk.text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith("---"):
                    continue
                clean_lines.append(stripped.lstrip("* -").strip())
            excerpt = " ".join(clean_lines)[:200]

            payload = {
                "chunk_id": hit.chunk.chunk_id,
                "source_id": meta.source_id,
                "source_type": meta.source_type,
                "title": meta.title,
                "section": meta.section,
                "file_path": meta.file_path,
                "url": meta.url,
                "score": round(hit.score, 4),
                "excerpt": excerpt,
            }

            existing = best_by_source.get(meta.source_id)
            if existing is None or float(payload["score"]) > float(str(existing["score"])):
                best_by_source[meta.source_id] = payload

        sources = sorted(best_by_source.values(), key=lambda s: float(s["score"]), reverse=True)[:4]
        return CitationPayload(query=query, sources=sources)

    async def publish_citations(
        self,
        room: rtc.Room,
        query: str,
        hits: list[RetrievalHit],
    ) -> None:
        if not hits or room.local_participant is None:
            return

        payload = self.build_citation_payload(query, hits).to_dict()
        try:
            await room.local_participant.publish_data(
                json.dumps(payload).encode("utf-8"),
                topic=CITATIONS_TOPIC,
                reliable=True,
            )
        except Exception:
            logger.exception("failed to publish citation payload")


def get_default_retriever() -> KnowledgeRetriever:
    return KnowledgeRetriever(INDEX_DIR)


# ---------------------------------------------------------------------------
# Intent classification — pure keyword rules with word-boundary matching
# ---------------------------------------------------------------------------

import re

_CHITCHAT_PATTERNS = [
    r"^(hi|hello|hey|greetings|howdy|good morning|good afternoon|good evening)\b",
    r"^(thank you|thanks|thx|appreciate it)\b",
    r"^(bye|goodbye|see you|cya)\b",
    r"^(how are you|how's it going|what's up|how do you do)\b",
    r"^(okay|ok|cool|nice|great|awesome|got it|sounds good)\b",
]


def _is_chitchat(query: str) -> bool:
    """Return True if the query is conversational chitchat that shouldn't show citations."""
    cleaned = query.strip().lower()
    return any(bool(re.search(p, cleaned)) for p in _CHITCHAT_PATTERNS)


# Known project & PR source_ids mapped to (category, source_id)
_PROJECT_NAME_MAP: dict[str, tuple[str, str]] = {
    "voxel": ("projects", "voxel"),
    "loopin": ("projects", "loopin"),
    "grocerspy": ("projects", "grocerspy"),
    "grocer spy": ("projects", "grocerspy"),
    "grocer-spy": ("projects", "grocerspy"),
    "openagri": ("side_projects", "openagrinet_training_pipeline"),
    "openagrinet": ("side_projects", "openagrinet_training_pipeline"),
    "agrinet": ("side_projects", "openagrinet_training_pipeline"),
    "college mess": ("side_projects", "college_mess_webapp"),
    "mess webapp": ("side_projects", "college_mess_webapp"),
    "college_mess": ("side_projects", "college_mess_webapp"),
    "turtle": ("side_projects", "turtle"),
    "proxy": ("side_projects", "proxy"),
    "proxyy": ("side_projects", "proxy"),
    "digital twin": ("side_projects", "proxy"),
    "urcv": ("github", "pr-56-resume-export-features"),
    "urcv.ai": ("github", "pr-56-resume-export-features"),
    "sustaina": ("github", "pr-04-updated-landing-page-sustaina"),
    "layr": ("github", "pr-23-improve-error-messages"),
}

_CATEGORY_RULES: list[tuple[list[str], list[str]]] = [
    # (keywords, categories) — checked in order with word boundaries
    (["pull request", "pull requests", "pr", "prs", "merged pr", "open source", "contributions", "contribution"], ["github"]),
    (["project", "projects", "built", "build", "portfolio", "prototype", "app", "application", "made", "created", "developed"], ["projects"]),
    (["github", "repo", "repository", "commit", "commits", "merged"], ["github"]),
    (["skill", "skills", "tech stack", "technologies", "language", "languages", "framework", "frameworks", "tools", "know", "stack"], ["skills"]),
    (["education", "college", "university", "degree", "vit", "bhopal", "student", "semester", "study", "cgpa", "gpa", "btech", "b.tech"], ["resume"]),
    (["firefox", "mozilla", "microsoft", "club", "leadership", "lead", "team lead", "organize", "workshop", "hackathon organiz"], ["leadership"]),
    (["achievement", "achievements", "hackbyte", "smart india", "hackathon", "finalist", "won", "award", "top 15", "top 40"], ["achievements"]),
    (["contact", "email", "linkedin", "social", "reach", "location", "live", "where", "city"], ["personal", "resume"]),
    (["about yourself", "who are you", "tell me about you", "who is prem", "background", "bio"], ["resume"]),
    (["experience", "work", "job", "career", "intern", "internship", "company", "employer"], ["resume"]),
]


def _classify_intent(query: str) -> tuple[list[str], str | None]:
    """Return (categories, source_id_hint) from a plain-text query using word-boundary matching."""
    lowered = query.lower()

    # Check for a specific project or PR name first
    for name, (cat, sid) in _PROJECT_NAME_MAP.items():
        if re.search(r"\b" + re.escape(name) + r"\b", lowered):
            return [cat], sid

    # Match category rules in priority order
    matched: list[str] = []
    for keywords, categories in _CATEGORY_RULES:
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", lowered):
                for c in categories:
                    if c not in matched:
                        matched.append(c)
                break

    if matched:
        return matched, None

    # Fallback: broad — search all categories
    return ["projects", "side_projects", "skills", "leadership", "education", "achievements", "github", "resume"], None


_PREFERRED_SECTIONS = {
    "Overview",
    "Resume Facts",
    "Solution",
    "Tech Stack",
    "Key Features",
    "Summary",
    "Contribution Summary",
    "Impact",
    "Bugs Fixed",
    "Key Changes & Implementation",
    "Backend",
    "Frontend",
    "Programming Languages",
    "Databases and Tools",
    "Libraries",
    "Technical Concepts",
}

_PENALIZED_SECTIONS = {
    "Grounding Rules",
    "Important Limitations",
    "Installation",
    "Project Structure",
    "Your Notes",
    "Languages",
    "Compatibility",
    "Development",
    "Client",
    "Server",
    "Suggested Questions This Source Can Answer",
    "Evidence",
    "Related Work",
}


def _rank_chunk_score(hit: RetrievalHit) -> float:
    """Calculate an adjusted score prioritizing high-information sections."""
    sec = (hit.chunk.metadata.section or "").strip()
    score = hit.score
    if sec == "Overview":
        score += 0.35
    elif sec in {"Resume Facts", "Solution", "Key Features", "Tech Stack", "Summary", "Contribution Summary", "Impact"}:
        score += 0.25
    elif any(
        p in sec.lower()
        for p in ["backend", "frontend", "programming languages", "databases", "libraries", "key changes", "bugs fixed"]
    ):
        score += 0.20
    if sec in _PENALIZED_SECTIONS or any(
        pen.lower() in sec.lower() for pen in ["suggested questions", "evidence", "grounding rules", "limitations"]
    ):
        score -= 0.35
    return score


def _diversity_dedup(
    hits: list[RetrievalHit],
    top_k: int,
    target_sources: list[str] | None = None,
) -> list[RetrievalHit]:
    """Return up to top_k hits keeping at most 1 best chunk per source_id.

    If target_sources is provided, extracts the best chunk for each target source in order.
    Otherwise, picks the top-scoring chunk for each distinct source.
    """
    best_per_source: dict[str, tuple[float, RetrievalHit]] = {}
    for hit in hits:
        sid = hit.chunk.metadata.source_id
        adj_score = _rank_chunk_score(hit)
        if sid not in best_per_source or adj_score > best_per_source[sid][0]:
            best_per_source[sid] = (adj_score, hit)

    if target_sources:
        result: list[RetrievalHit] = []
        for sid in target_sources:
            if sid in best_per_source:
                result.append(best_per_source[sid][1])
            if len(result) >= top_k:
                break
        return result

    sorted_sources = sorted(best_per_source.values(), key=lambda t: t[0], reverse=True)
    result = [t[1] for t in sorted_sources[:top_k]]

    # Second pass: fill remaining slots with runner-up chunks if needed
    if len(result) < top_k:
        used_chunks = {h.chunk.chunk_id for h in result}
        sorted_hits = sorted(hits, key=_rank_chunk_score, reverse=True)
        for hit in sorted_hits:
            if len(result) >= top_k:
                break
            if hit.chunk.chunk_id not in used_chunks:
                result.append(hit)
                used_chunks.add(hit.chunk.chunk_id)

    return result
