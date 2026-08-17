---

source_id: voxel
source_type: project
title: Voxel — AI-Powered Workspace
url:
----

# Overview

Voxel is an AI-powered canvas that converts hand-drawn sketches into AI-generated 2D illustrations and 3D models.

The project combines an interactive digital whiteboard with AI generation capabilities, allowing users to create and edit sketches and use them as input for generating visual content.

# Problem

Creating digital illustrations and 3D models can require specialized tools and workflows. Voxel explores a more direct interaction model where users can sketch their ideas on an interactive whiteboard and use AI to transform those sketches into generated visual content.

# Solution

* Provides an interactive whiteboard for creating and editing sketches.
* Uses AI to convert hand-drawn sketches into 2D illustrations and 3D models.
* Integrates multiple AI providers.
* Uses WebSockets as part of the architecture for real-time collaboration.
* Uses asynchronous AI processing for AI-related tasks.

# Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* tldraw

## Graphics and 3D

* Three.js

## Real-Time Communication

* WebSockets

## AI

* Multiple AI providers
* Asynchronous AI processing

# Key Features

## Interactive Whiteboard

Voxel provides an interactive whiteboard using tldraw.

Users can:

* Draw freehand
* Create shapes
* Select objects
* Resize objects
* Edit objects

## AI-Powered Generation

Voxel can convert hand-drawn sketches into AI-generated:

* 2D illustrations
* 3D models

## Multiple AI Providers

The application integrates multiple AI providers rather than relying on a single AI provider.

## Real-Time Collaboration

The architecture is designed to support real-time collaboration using WebSockets.

## Asynchronous AI Processing

AI processing is handled asynchronously to support the application's generation workflow.

# How It Works

1. A user creates a sketch using the interactive whiteboard.
2. The sketch can be edited using drawing, selection, resizing, and other whiteboard interactions.
3. The sketch is provided as input to the AI generation workflow.
4. The system processes the request asynchronously.
5. AI-generated 2D illustrations or 3D models are produced from the sketch.
6. WebSockets are used as part of the architecture for real-time collaboration.

# Project Information

* Project: Voxel
* Dates: July 2026 – Present
* Type: AI-powered workspace
* Technologies: Next.js, React, TypeScript, tldraw, Three.js, WebSockets, AI

# Project Goal

Voxel explores how AI generation can be combined with an interactive drawing workspace.

The goal is to allow users to start with a simple hand-drawn idea and use AI to transform that idea into richer 2D or 3D visual content while providing an interactive workspace for creating and editing the original sketch.

# Important Limitations

* The available project documentation does not specify the names of the AI providers.
* The documentation does not specify which AI models are used.
* The documentation does not provide performance benchmarks for AI generation.
* The documentation does not provide the number of concurrent collaborators supported.
* Do not claim specific 3D generation capabilities beyond generating 3D models from hand-drawn sketches unless another source confirms them.

# Resume Facts

* Built an AI-powered workspace that converts hand-drawn sketches into AI-generated 2D illustrations and 3D models.
* Developed an interactive whiteboard with freehand drawing, shape creation, selection, resizing, and editing using tldraw.
* Integrated multiple AI providers.
* Designed architecture for real-time collaboration using WebSockets.
* Implemented asynchronous AI processing.
* Technologies: Next.js, React, TypeScript, tldraw, Three.js, WebSockets, AI.

# Grounding Rules

* Do not invent the names of AI providers or models.
* Do not claim a specific AI-generated result unless it is supported by the project documentation.
* When discussing the whiteboard, identify tldraw as the technology used.
* When discussing real-time collaboration, identify WebSockets as part of the architecture.
* When discussing 3D capabilities, describe them as AI-generated 3D models from hand-drawn sketches.
* If a requested implementation detail is not documented here, state that the available Voxel documentation does not provide that information.
