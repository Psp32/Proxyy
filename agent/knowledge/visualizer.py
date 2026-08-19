"""Visualization generator for the Digital Twin voice agent.

Classifies whether a user query benefits from visual explanation, and if so,
builds structured visualization data strictly from the RAG retrieval hits.
All data is grounded directly in the project documents (loopin.md, voxel.md, etc.).

When no visualization is required, a clear message is published to dismiss stale canvases.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from livekit import rtc

from .models import RetrievalHit

logger = logging.getLogger("knowledge.visualizer")

VISUALIZATION_TOPIC = "visualization"


# Project Source Identification

_PROJECT_KEYWORDS: dict[str, str] = {
    "loopin": "loopin",
    "loop in": "loopin",
    "loop-in": "loopin",
    "voxel": "voxel",
    "grocerspy": "grocerspy",
    "grocer spy": "grocerspy",
    "grocer-spy": "grocerspy",
    "openagri": "openagrinet_training_pipeline",
    "openagrinet": "openagrinet_training_pipeline",
    "college mess": "college_mess_webapp",
    "mess webapp": "college_mess_webapp",
    "turtle": "turtle",
    "proxy": "proxy",
    "digital twin": "proxy",
}


def _identify_target_project(query: str) -> str | None:
    lowered = query.lower()
    for name, sid in _PROJECT_KEYWORDS.items():
        if re.search(r"\b" + re.escape(name) + r"\b", lowered):
            return sid
    return None


# Query Classification

_SKIP_PATTERNS = [
    r"^(hi|hello|hey|greetings|howdy|good morning|good afternoon|good evening)\b",
    r"^(thank you|thanks|thx|appreciate it)\b",
    r"^(bye|goodbye|see you|cya)\b",
    r"^(how are you|how's it going|what's up)\b",
    r"^(okay|ok|cool|nice|great|awesome|got it|sounds good)\b",
    r"^(what is your name|who are you)\b",
    r"^(where do you live|where are you from|contact|email|phone|city)\b",
    r"^(tell me about yourself|who is prem|background|bio)\b",
    r"^(education|college|gpa|cgpa|school|university|degree)\b",
]


def classify_viz_type(query: str) -> str | None:
    lowered = query.strip().lower()

    if len(lowered) < 3:
        return None

    # Check for explicit drawing or visual canvas requests
    is_visual_request = bool(
        re.search(
            r"\b(draw|sketch|visualize|diagram|flowchart|architecture|canvas|chart|map out|render|show me on screen|show on canvas|graph)\b",
            lowered,
        )
    )

    # Only skip if this is not an explicit request to draw/show/canvas
    if not is_visual_request:
        for pat in _SKIP_PATTERNS:
            if re.search(pat, lowered):
                return None

    # Check comparison
    for kw in ["compare", "vs", "versus", "difference between", "differences"]:
        if re.search(r"\b" + kw + r"\b", lowered):
            return "comparison"

    # Check timeline / evolution
    for kw in ["timeline", "evolved", "journey", "history", "progression", "over time", "chronolog"]:
        if re.search(r"\b" + kw + r"\b", lowered):
            return "timeline"

    # Check workflow / pipeline / how it works
    for kw in ["workflow", "how does .* work", "process", "pipeline", "steps", "how it works", "lifecycle", "flowchart"]:
        if re.search(r"\b" + kw + r"\b", lowered):
            return "workflow"

    # Check skills / tech stack
    for kw in ["technologies", "skills", "tech stack", "languages", "frameworks", "tools", "what tech"]:
        if re.search(r"\b" + kw + r"\b", lowered):
            return "skill_graph"

    # Check specific project architecture
    target = _identify_target_project(query)
    if target is not None:
        return "architecture"

    # General projects overview
    for kw in ["project", "projects", "what have you built", "what did you build", "portfolio", "built"]:
        if re.search(r"\b" + kw + r"\b", lowered):
            return "projects_overview"

    # If the user explicitly requested a diagram/canvas/draw but no specific category matched, show projects overview
    if is_visual_request:
        return "projects_overview"

    return None


# Source Reference Extractor
def _extract_source_ref(hit: RetrievalHit) -> dict[str, Any]:
    meta = hit.chunk.metadata
    ref: dict[str, Any] = {
        "source_id": meta.source_id,
        "title": meta.title,
    }
    if meta.section:
        ref["section"] = meta.section
    lines = [
        l.strip().lstrip("* -").strip()
        for l in hit.chunk.text.splitlines()
        if l.strip() and not l.strip().startswith("#") and not l.strip().startswith("---")
    ]
    if lines:
        ref["excerpt"] = " ".join(lines)[:180]
    if meta.url:
        ref["url"] = meta.url
    return ref


# Strictly Grounded Project Architectures

def _build_loopin_architecture(hits: list[RetrievalHit]) -> dict[str, Any]:
    """Loopin: React + TypeScript + Node.js ws + WebSockets + WebRTC. ZERO Python/AI."""
    src = [_extract_source_ref(h) for h in hits if "loopin" in h.chunk.metadata.source_id][:2]
    if not src and hits:
        src = [_extract_source_ref(hits[0])]

    nodes = [
        {
            "id": "loopin-client",
            "label": "React Frontend",
            "group": "frontend",
            "description": "TypeScript + Tailwind CSS Interface",
            "sources": src,
        },
        {
            "id": "loopin-rooms",
            "label": "Temporary Rooms",
            "group": "concept",
            "description": "Unique room code join/create system",
            "sources": src,
        },
        {
            "id": "loopin-ws",
            "label": "Node.js WebSocket Server",
            "group": "backend",
            "description": "TypeScript + ws WebSocket library",
            "sources": src,
        },
        {
            "id": "loopin-messaging",
            "label": "Real-Time Chat",
            "group": "realtime",
            "description": "Instant WebSocket text message relay",
            "sources": src,
        },
        {
            "id": "loopin-webrtc",
            "label": "WebRTC P2P Engine",
            "group": "realtime",
            "description": "Direct peer-to-peer audio & video stream",
            "sources": src,
        },
        {
            "id": "loopin-peer",
            "label": "Connected Peer",
            "group": "frontend",
            "description": "Direct browser-to-browser media exchange",
            "sources": src,
        },
    ]

    edges = [
        {"from": "loopin-client", "to": "loopin-rooms", "label": "Join / Create"},
        {"from": "loopin-rooms", "to": "loopin-ws", "label": "WebSocket Connect (ws://)"},
        {"from": "loopin-ws", "to": "loopin-messaging", "label": "Text Broadcast"},
        {"from": "loopin-ws", "to": "loopin-webrtc", "label": "Signaling (SDP/ICE)"},
        {"from": "loopin-client", "to": "loopin-webrtc", "label": "Local Media Stream"},
        {"from": "loopin-webrtc", "to": "loopin-peer", "label": "Direct P2P Stream"},
    ]

    return {
        "type": "architecture",
        "title": "Loopin — Real-Time Communication Architecture",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": "Loopin Architecture", "total_sources": len(src)},
    }


def _build_voxel_architecture(hits: list[RetrievalHit]) -> dict[str, Any]:
    """Voxel: Next.js + React + tldraw + Three.js + WebSockets + Multi-AI."""
    src = [_extract_source_ref(h) for h in hits if "voxel" in h.chunk.metadata.source_id][:2]
    if not src and hits:
        src = [_extract_source_ref(hits[0])]

    nodes = [
        {
            "id": "voxel-whiteboard",
            "label": "Interactive Whiteboard",
            "group": "frontend",
            "description": "tldraw freehand sketches & shapes",
            "sources": src,
        },
        {
            "id": "voxel-frontend",
            "label": "Next.js & React Client",
            "group": "frontend",
            "description": "TypeScript web workspace",
            "sources": src,
        },
        {
            "id": "voxel-realtime",
            "label": "WebSocket Sync",
            "group": "realtime",
            "description": "Real-time multi-user collaboration",
            "sources": src,
        },
        {
            "id": "voxel-ai-pipeline",
            "label": "Async AI Engine",
            "group": "ai",
            "description": "Multiple AI providers generation pipeline",
            "sources": src,
        },
        {
            "id": "voxel-3d-render",
            "label": "Three.js 2D/3D Viewer",
            "group": "frontend",
            "description": "2D illustrations & 3D model visualizer",
            "sources": src,
        },
    ]

    edges = [
        {"from": "voxel-whiteboard", "to": "voxel-frontend", "label": "Canvas Sketch"},
        {"from": "voxel-frontend", "to": "voxel-realtime", "label": "Collab Sync"},
        {"from": "voxel-frontend", "to": "voxel-ai-pipeline", "label": "Async AI Request"},
        {"from": "voxel-ai-pipeline", "to": "voxel-3d-render", "label": "2D/3D Model Data"},
        {"from": "voxel-3d-render", "to": "voxel-frontend", "label": "Render to Canvas"},
    ]

    return {
        "type": "architecture",
        "title": "Voxel — AI-Powered Workspace Architecture",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": "Voxel Architecture", "total_sources": len(src)},
    }


def _build_grocerspy_architecture(hits: list[RetrievalHit]) -> dict[str, Any]:
    """GrocerSpy: Python + Playwright + Blinkit/Swiggy/JioMart + thefuzz + pandas."""
    src = [_extract_source_ref(h) for h in hits if "grocerspy" in h.chunk.metadata.source_id][:2]
    if not src and hits:
        src = [_extract_source_ref(hits[0])]

    nodes = [
        {
            "id": "gs-user",
            "label": "Product Search Query",
            "group": "concept",
            "description": "User grocery product inputs",
            "sources": src,
        },
        {
            "id": "gs-core",
            "label": "Python Core Engine",
            "group": "language",
            "description": "Command-line comparison runner",
            "sources": src,
        },
        {
            "id": "gs-playwright",
            "label": "Playwright Automation",
            "group": "tool",
            "description": "Headless browser scraping",
            "sources": src,
        },
        {
            "id": "gs-blinkit",
            "label": "Blinkit",
            "group": "data",
            "description": "Product search listings",
            "sources": src,
        },
        {
            "id": "gs-swiggy",
            "label": "Swiggy Instamart",
            "group": "data",
            "description": "Product search listings",
            "sources": src,
        },
        {
            "id": "gs-jiomart",
            "label": "JioMart",
            "group": "data",
            "description": "Product search listings",
            "sources": src,
        },
        {
            "id": "gs-fuzzy",
            "label": "thefuzz Library",
            "group": "framework",
            "description": "Fuzzy string matching & product ranking",
            "sources": src,
        },
        {
            "id": "gs-output",
            "label": "pandas & Rich Tables",
            "group": "concept",
            "description": "Lowest price detection & comparison matrix",
            "sources": src,
        },
    ]

    edges = [
        {"from": "gs-user", "to": "gs-core", "label": "Query Input"},
        {"from": "gs-core", "to": "gs-playwright", "label": "Automate Search"},
        {"from": "gs-playwright", "to": "gs-blinkit", "label": "Scrape"},
        {"from": "gs-playwright", "to": "gs-swiggy", "label": "Scrape"},
        {"from": "gs-playwright", "to": "gs-jiomart", "label": "Scrape"},
        {"from": "gs-blinkit", "to": "gs-fuzzy", "label": "Raw Products"},
        {"from": "gs-swiggy", "to": "gs-fuzzy", "label": "Raw Products"},
        {"from": "gs-jiomart", "to": "gs-fuzzy", "label": "Raw Products"},
        {"from": "gs-fuzzy", "to": "gs-output", "label": "Matched Items"},
        {"from": "gs-output", "to": "gs-user", "label": "Lowest Price Result"},
    ]

    return {
        "type": "architecture",
        "title": "GrocerSpy — Grocery Price Comparison Pipeline",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": "GrocerSpy Architecture", "total_sources": len(src)},
    }


def _build_proxy_architecture(hits: list[RetrievalHit]) -> dict[str, Any]:
    """Digital Twin: Next.js + LiveKit + Deepgram + Gemma + Inworld + ChromaDB."""
    src = [_extract_source_ref(h) for h in hits if "proxy" in h.chunk.metadata.source_id][:2]
    if not src and hits:
        src = [_extract_source_ref(hits[0])]

    nodes = [
        {
            "id": "proxy-fe",
            "label": "Next.js 16 WebGL Client",
            "group": "frontend",
            "description": "React 19 + Siri Fluid Wave animation",
            "sources": src,
        },
        {
            "id": "proxy-livekit",
            "label": "LiveKit WebRTC Infrastructure",
            "group": "realtime",
            "description": "Real-time bidirectional audio & data channel",
            "sources": src,
        },
        {
            "id": "proxy-stt",
            "label": "Deepgram Nova-3 STT",
            "group": "ai",
            "description": "Real-time speech transcription",
            "sources": src,
        },
        {
            "id": "proxy-rag",
            "label": "ChromaDB RAG Engine",
            "group": "data",
            "description": "Vector similarity search & citation extraction",
            "sources": src,
        },
        {
            "id": "proxy-llm",
            "label": "Google Gemma 4 (31B)",
            "group": "ai",
            "description": "Grounded conversational intelligence",
            "sources": src,
        },
        {
            "id": "proxy-tts",
            "label": "Inworld TTS 2",
            "group": "ai",
            "description": "Ashley expressive voice synthesizer",
            "sources": src,
        },
    ]

    edges = [
        {"from": "proxy-fe", "to": "proxy-livekit", "label": "Microphone Audio"},
        {"from": "proxy-livekit", "to": "proxy-stt", "label": "Audio Stream"},
        {"from": "proxy-stt", "to": "proxy-rag", "label": "Transcribed Query"},
        {"from": "proxy-rag", "to": "proxy-llm", "label": "Grounded Facts"},
        {"from": "proxy-llm", "to": "proxy-tts", "label": "Text Reply"},
        {"from": "proxy-tts", "to": "proxy-livekit", "label": "Synthesized Audio"},
        {"from": "proxy-livekit", "to": "proxy-fe", "label": "Speaker Audio + Data"},
    ]

    return {
        "type": "architecture",
        "title": "Digital Twin — Voice & RAG Architecture",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": "Digital Twin Architecture", "total_sources": len(src)},
    }


def _build_projects_overview(hits: list[RetrievalHit]) -> dict[str, Any]:
    src = [_extract_source_ref(h) for h in hits][:3]

    nodes = [
        {
            "id": "hub-projects",
            "label": "Prem's Key Projects",
            "group": "default",
            "description": "Featured engineering portfolio",
            "sources": src,
        },
        {
            "id": "proj-voxel",
            "label": "Voxel",
            "group": "frontend",
            "description": "AI sketch whiteboard converting to 2D/3D (Next.js, tldraw, Three.js, WebSockets)",
            "sources": src,
        },
        {
            "id": "proj-loopin",
            "label": "Loopin",
            "group": "realtime",
            "description": "Real-time communication app with instant messaging & P2P video (React, Node.js, WebRTC)",
            "sources": src,
        },
        {
            "id": "proj-grocerspy",
            "label": "GrocerSpy",
            "group": "tool",
            "description": "Price comparison scraper for Blinkit/Swiggy/JioMart (Python, Playwright, thefuzz)",
            "sources": src,
        },
        {
            "id": "proj-openagri",
            "label": "OpenAgriNet",
            "group": "ai",
            "description": "Agent training pipeline & agricultural dataset processing",
            "sources": src,
        },
        {
            "id": "proj-proxy",
            "label": "Digital Twin",
            "group": "ai",
            "description": "Real-time voice AI twin with grounded RAG & canvas (LiveKit, Gemma, ChromaDB)",
            "sources": src,
        },
    ]

    edges = [
        {"from": "hub-projects", "to": "proj-voxel", "label": "AI Workspace"},
        {"from": "hub-projects", "to": "proj-loopin", "label": "Real-Time WebRTC"},
        {"from": "hub-projects", "to": "proj-grocerspy", "label": "Web Scraping"},
        {"from": "hub-projects", "to": "proj-openagri", "label": "Agent Pipeline"},
        {"from": "hub-projects", "to": "proj-proxy", "label": "Voice Agent"},
    ]

    return {
        "type": "architecture",
        "title": "Prem's Featured Projects",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": "Projects Overview", "total_sources": len(src)},
    }


def _build_architecture(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    target = _identify_target_project(query)

    if target == "loopin":
        return _build_loopin_architecture(hits)
    elif target == "voxel":
        return _build_voxel_architecture(hits)
    elif target == "grocerspy":
        return _build_grocerspy_architecture(hits)
    elif target == "proxy":
        return _build_proxy_architecture(hits)

    return _build_projects_overview(hits)


# Comparison Builder

def _build_comparison(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    if not hits:
        return None

    by_source: dict[str, list[RetrievalHit]] = {}
    for h in hits:
        sid = h.chunk.metadata.source_id
        by_source.setdefault(sid, []).append(h)

    sources_list = list(by_source.keys())
    if len(sources_list) < 2:
        return _build_architecture(query, hits)

    proj_a_id = sources_list[0]
    proj_b_id = sources_list[1]
    hits_a = by_source[proj_a_id]
    hits_b = by_source[proj_b_id]

    title_a = hits_a[0].chunk.metadata.title.split("—")[0].strip()
    title_b = hits_b[0].chunk.metadata.title.split("—")[0].strip()

    nodes = [
        {
            "id": "comparison-hub",
            "label": f"{title_a} vs {title_b}",
            "group": "shared",
            "description": "Comparative Project Analysis",
            "sources": [_extract_source_ref(hits_a[0]), _extract_source_ref(hits_b[0])],
        },
        {
            "id": f"proj-{proj_a_id}",
            "label": title_a,
            "group": "left",
            "sources": [_extract_source_ref(hits_a[0])],
        },
        {
            "id": f"proj-{proj_b_id}",
            "label": title_b,
            "group": "right",
            "sources": [_extract_source_ref(hits_b[0])],
        },
    ]

    edges = [
        {"from": "comparison-hub", "to": f"proj-{proj_a_id}", "label": "Project A"},
        {"from": "comparison-hub", "to": f"proj-{proj_b_id}", "label": "Project B"},
    ]

    return {
        "type": "comparison",
        "title": f"{title_a} vs {title_b} Comparison",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": query, "total_sources": len(sources_list)},
    }


# Workflow Builder

def _build_workflow(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    target = _identify_target_project(query)
    filtered = [h for h in hits if h.chunk.metadata.source_id == target] if target else hits
    if not filtered:
        filtered = hits

    primary = filtered[0].chunk.metadata
    title = primary.title.split("—")[0].strip()

    step_pattern = re.compile(r"^\d+\.\s+(.+)$", re.MULTILINE)
    steps: list[tuple[str, RetrievalHit]] = []

    for h in filtered:
        found = step_pattern.findall(h.chunk.text)
        for s in found:
            clean = s.strip().rstrip(".")
            if clean and not any(clean == existing[0] for existing in steps):
                steps.append((clean, h))

    if len(steps) < 2:
        return _build_architecture(query, hits)

    steps = steps[:5]
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for idx, (step_text, hit) in enumerate(steps):
        step_id = f"step-{idx + 1}"
        short_label = step_text if len(step_text) <= 45 else step_text[:42] + "..."
        group = "frontend" if idx == 0 else ("concept" if idx == len(steps) - 1 else "backend")

        nodes.append({
            "id": step_id,
            "label": f"Step {idx + 1}: {short_label}",
            "group": group,
            "description": step_text if len(step_text) > 45 else "",
            "sources": [_extract_source_ref(hit)],
        })

        if idx > 0:
            edges.append({
                "from": f"step-{idx}",
                "to": step_id,
                "label": f"Next",
            })

    return {
        "type": "workflow",
        "title": f"{title} — How It Works",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": query, "total_sources": len(filtered)},
    }


# Timeline Builder

def _build_timeline(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    timeline_items = [
        {
            "id": "time-grocerspy",
            "title": "GrocerSpy",
            "date": "Aug 2025 – Oct 2025",
            "desc": "Python & Playwright grocery price comparison tool",
            "sid": "grocerspy",
        },
        {
            "id": "time-loopin",
            "title": "Loopin",
            "date": "Jun 2026 – Present",
            "desc": "Real-time communication app using WebSockets & WebRTC",
            "sid": "loopin",
        },
        {
            "id": "time-voxel",
            "title": "Voxel",
            "date": "Jul 2026 – Present",
            "desc": "AI workspace with interactive whiteboard (tldraw & Three.js)",
            "sid": "voxel",
        },
        {
            "id": "time-proxy",
            "title": "Digital Twin",
            "date": "2026 – Present",
            "desc": "LiveKit voice agent with grounded RAG & AI Canvas",
            "sid": "proxy",
        },
    ]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for idx, item in enumerate(timeline_items):
        matching_hits = [h for h in hits if item["sid"] in h.chunk.metadata.source_id]
        src = [_extract_source_ref(matching_hits[0])] if matching_hits else [_extract_source_ref(hits[0])]

        nodes.append({
            "id": item["id"],
            "label": f"{item['title']} ({item['date']})",
            "group": "present" if "Present" in item["date"] else "past",
            "description": item["desc"],
            "sources": src,
        })

        if idx > 0:
            edges.append({
                "from": timeline_items[idx - 1]["id"],
                "to": item["id"],
                "label": "Next",
            })

    return {
        "type": "timeline",
        "title": "Project Evolution Timeline",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": query, "total_sources": len(timeline_items)},
    }


# Skill Graph Builder

def _build_skill_graph(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    categories = {
        "Languages": (["TypeScript", "JavaScript", "Python", "C++", "SQL"], "language"),
        "Frontend": (["React", "Next.js", "Tailwind CSS", "Three.js", "tldraw"], "frontend"),
        "Backend & Realtime": (["Node.js", "FastAPI", "WebSockets", "WebRTC", "LiveKit"], "backend"),
        "AI & Data": (["RAG", "ChromaDB", "Deepgram", "Playwright", "thefuzz"], "ai"),
    }

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    nodes.append({
        "id": "skill-hub",
        "label": "Prem's Tech Stack",
        "group": "default",
        "description": "Core engineering capabilities",
        "sources": [_extract_source_ref(hits[0])],
    })

    for cat_name, (skills, group) in categories.items():
        cat_id = f"cat-{cat_name.lower().replace(' ', '-').replace('&', 'and')}"
        nodes.append({
            "id": cat_id,
            "label": cat_name,
            "group": group,
            "sources": [_extract_source_ref(hits[0])],
        })
        edges.append({"from": "skill-hub", "to": cat_id, "label": "Domain"})

        for skill in skills:
            skill_id = f"skill-{skill.lower().replace('.', '').replace('+', 'p').replace(' ', '')}"
            nodes.append({
                "id": skill_id,
                "label": skill,
                "group": group,
                "sources": [_extract_source_ref(hits[0])],
            })
            edges.append({"from": cat_id, "to": skill_id, "label": "Skill"})

    return {
        "type": "skill_graph",
        "title": "Skills & Technologies Graph",
        "nodes": nodes,
        "edges": edges,
        "metadata": {"query": query, "total_sources": len(hits)},
    }


# Public Dispatch

_BUILDERS: dict[str, Any] = {
    "architecture": _build_architecture,
    "projects_overview": _build_projects_overview,
    "comparison": _build_comparison,
    "timeline": _build_timeline,
    "workflow": _build_workflow,
    "skill_graph": _build_skill_graph,
}


def build_visualization(query: str, hits: list[RetrievalHit]) -> dict[str, Any] | None:
    viz_type = classify_viz_type(query)
    if viz_type is None:
        return None

    builder = _BUILDERS.get(viz_type)
    if builder is None:
        return None

    try:
        return builder(query, hits)
    except Exception:
        logger.exception("Failed to build %s visualization", viz_type)
        return None


def format_canvas_context(viz_data: dict[str, Any] | None) -> str:
    """Format active canvas state into a concise context block for the LLM."""
    if not viz_data or viz_data.get("type") == "clear":
        return "Interactive AI Canvas State: The canvas is currently cleared/idle."

    title = viz_data.get("title", "Active Diagram")
    viz_type = viz_data.get("type", "architecture")
    nodes = viz_data.get("nodes", [])
    node_summaries = []
    for n in nodes:
        label = n.get("label", "")
        desc = n.get("description", "")
        if desc:
            node_summaries.append(f"  • {label}: {desc}")
        elif label:
            node_summaries.append(f"  • {label}")

    nodes_text = "\n".join(node_summaries) if node_summaries else "Standard flow components"
    edges = [
        f"{e.get('from')} -> {e.get('to')} ({e.get('label', '')})"
        for e in viz_data.get("edges", [])
        if e.get("label")
    ]
    edges_text = "; ".join(edges[:5]) if edges else "Connected data pipeline"

    return (
        f"Active Canvas Diagram on User's Screen:\n"
        f"- Diagram Title: {title}\n"
        f"- Diagram Type: {viz_type}\n"
        f"- Visible Nodes:\n{nodes_text}\n"
        f"- Key Connections: {edges_text}\n"
        f"- Guidance: This visual diagram has been rendered on the user's interactive AI canvas. "
        f"You are fully aware of it. Refer directly to these nodes, connections, and technologies when explaining."
    )


async def publish_visualization(
    room: rtc.Room,
    query: str,
    hits: list[RetrievalHit],
    viz_data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not hits or room.local_participant is None:
        return None

    if viz_data is None:
        viz_data = build_visualization(query, hits)
    payload = viz_data if viz_data is not None else {"type": "clear", "nodes": [], "edges": []}

    try:
        await room.local_participant.publish_data(
            json.dumps(payload).encode("utf-8"),
            topic=VISUALIZATION_TOPIC,
            reliable=True,
        )
        if viz_data:
            logger.info("Published %s visualization for query: %s", viz_data.get("type"), query)
        else:
            logger.info("Published canvas clear action for query: %s", query)
    except Exception:
        logger.exception("Failed to publish visualization payload")

    return viz_data
