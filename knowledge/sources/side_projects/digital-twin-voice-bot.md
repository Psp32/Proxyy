---
source_id: proxy
source_type: project
title: Proxyy
url: https://github.com/Premx24/Proxyy
---

# Overview

A voice-first digital twin that answers questions about Prem using LiveKit, speech-to-text, retrieval-augmented generation, and text-to-speech.

# Problem

Visitors and collaborators need a natural way to ask questions about Prem's background, projects, and experience without reading long documents.

# Solution

- LiveKit voice pipeline for real-time conversation
- Knowledge base built from resume, project docs, and GitHub information
- Chunk-level source tracking so answers can be cited back to the original document

# Tech Stack

- Frontend: Next.js, LiveKit Components, custom voice orb UI
- Backend agent: Python LiveKit Agents
- Knowledge layer: markdown sources, chunking, ChromaDB embeddings, retrieval

# Current Status

- Basic voice conversation works
- Knowledge ingestion and retrieval pipeline in progress
- Citation UI planned next

# Key Features

- Tap-to-talk voice orb interface
- Optional typed questions
- Source-aware retrieval for grounded answers

# Your Notes

Add more project-specific details here when you provide your real project documentation.
