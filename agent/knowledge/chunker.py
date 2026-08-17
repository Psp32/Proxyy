from __future__ import annotations

import re
from pathlib import Path

from .models import DocumentChunk, SourceMetadata

FRONTMATTER_DELIM_PATTERN = re.compile(r"^---+[ \t]*\r?\n(.*?)\r?\n---+[ \t]*\r?\n", re.DOTALL)
HEADING_PATTERN = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    text_lstrip = text.lstrip()
    match = FRONTMATTER_DELIM_PATTERN.match(text_lstrip)
    if match:
        fm_raw = match.group(1)
        body = text_lstrip[match.end() :]
    else:
        # Check for key: value header lines before the first markdown heading
        lines = text_lstrip.splitlines()
        fm_lines: list[str] = []
        body_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("#"):
                body_start = i
                break
            if ":" in stripped and not stripped.startswith("-"):
                fm_lines.append(stripped)
            elif not stripped:
                continue
            else:
                body_start = i
                break
        else:
            body_start = len(lines)

        if fm_lines:
            fm_raw = "\n".join(fm_lines)
            body = "\n".join(lines[body_start:])
        else:
            return {}, text

    frontmatter: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, body


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not paragraphs:
        return []

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)

        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        start = 0
        while start < len(paragraph):
            end = min(start + chunk_size, len(paragraph))
            chunks.append(paragraph[start:end].strip())
            if end >= len(paragraph):
                break
            start = max(end - overlap, start + 1)
        current = ""

    if current:
        chunks.append(current)

    return chunks


def _infer_source_type(path: Path, sources_root: Path) -> str:
    relative = path.relative_to(sources_root)
    parts = relative.parts
    if path.name.lower() == "resume.md" or "resume" in path.stem.lower():
        return "resume"
    if (parts and parts[0] in ("github", "prs", "pull_requests")) or "github" in path.stem.lower() or "pr" in path.stem.lower():
        return "github"
    if parts and parts[0] == "projects":
        return "project"
    if parts and parts[0] == "side_projects":
        return "side_project"
    return "document"


_RESUME_SECTION_CATEGORIES: dict[str, str] = {
    "skills": "skills",
    "programming languages": "skills",
    "frontend": "skills",
    "backend": "skills",
    "databases": "skills",
    "libraries": "skills",
    "technical concepts": "skills",
    "tools": "skills",
    "leadership": "leadership",
    "activities": "leadership",
    "firefox": "leadership",
    "mozilla": "leadership",
    "microsoft": "leadership",
    "education": "education",
    "achievements": "achievements",
    "contact": "personal",
    "summary": "resume",
    "experience": "resume",
    "projects": "projects",
}


def _infer_category(source_type: str, section_title: str | None) -> str:
    """Map source_type + section heading to a retrieval category."""
    if source_type == "project":
        return "projects"
    if source_type == "side_project":
        return "side_projects"
    if source_type in ("github", "pull_request"):
        return "github"
    if source_type == "resume":
        if section_title is None:
            return "resume"
        key = section_title.lower().strip()
        for pattern, category in _RESUME_SECTION_CATEGORIES.items():
            if pattern in key:
                return category
        return "resume"
    return "resume"


def chunk_markdown_file(
    path: Path,
    sources_root: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    raw = path.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(raw)
    relative_path = str(path.relative_to(sources_root)).replace("\\", "/")

    # Path-based source_type takes priority for side_projects and prs
    path_source_type = _infer_source_type(path, sources_root)
    if path_source_type in ("side_project", "github"):
        source_type = path_source_type
    else:
        source_type = frontmatter.get("source_type") or path_source_type
    source_id = frontmatter.get("source_id") or path.stem
    title = frontmatter.get("title") or path.stem.replace("-", " ").title()
    url = frontmatter.get("url") or None

    sections: list[tuple[str | None, str]] = []
    current_section: str | None = None
    current_lines: list[str] = []

    for line in body.splitlines():
        heading_match = re.match(r"^#{1,3}\s+(.+)$", line.strip())
        if heading_match:
            if current_lines:
                sections.append((current_section, "\n".join(current_lines).strip()))
            current_section = heading_match.group(1).strip()
            current_lines = []
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_section, "\n".join(current_lines).strip()))

    if not sections:
        sections = [(None, body.strip())]

    chunks: list[DocumentChunk] = []
    chunk_index = 0

    for section_title, section_text in sections:
        if not section_text:
            continue

        category = frontmatter.get("category") or _infer_category(source_type, section_title)

        for piece in _split_long_text(section_text, chunk_size, chunk_overlap):
            metadata = SourceMetadata(
                source_id=source_id,
                source_type=source_type,
                title=title,
                file_path=relative_path,
                category=category,
                section=section_title,
                url=url,
                chunk_index=chunk_index,
            )
            chunk_id = f"{source_id}::{chunk_index}"
            chunk_header = f"## {title} — {section_title}" if section_title else f"## {title}"
            formatted_text = f"{chunk_header}\n\n{piece}"
            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    text=formatted_text,
                    metadata=metadata,
                )
            )
            chunk_index += 1

    return chunks


def chunk_sources_directory(
    sources_root: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    if not sources_root.exists():
        return []

    all_chunks: list[DocumentChunk] = []
    for path in sorted(sources_root.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        all_chunks.extend(
            chunk_markdown_file(
                path,
                sources_root=sources_root,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        )
    return all_chunks
