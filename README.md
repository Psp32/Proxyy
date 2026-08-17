# Proxy - Digital Twin Voice Bot

A voice-powered digital twin that answers questions about me in real time. It uses a RAG pipeline to ground every answer in my actual resume, projects, and open-source contributions, so it only says things that are true.

The frontend is a Next.js app with a custom WebGL voice orb. The backend is a Python agent that runs on LiveKit's real-time infrastructure with speech-to-text, an LLM, and text-to-speech working together in a live voice loop.

## How It Works

1. You tap the orb to start a voice session.
2. Your speech is transcribed in real time using Deepgram Nova 3.
3. The agent classifies your intent and retrieves relevant chunks from a ChromaDB vector store.
4. The LLM generates a grounded, conversational answer using only the retrieved context.
5. The answer is spoken back to you through LiveKit's TTS pipeline.
6. Source citations are pushed to the frontend over a LiveKit data channel and displayed below the orb.

## Tech Stack

**Frontend**
- Next.js 16 with TypeScript
- LiveKit Components React for real-time audio
- Custom WebGL shader (Siri-style fluid dot animation)
- Tailwind CSS

**Backend (Python Agent)**
- LiveKit Agents SDK for the voice pipeline
- Deepgram Nova 3 (STT), Google Gemma 4 31B (LLM), Inworld TTS 2
- ChromaDB for vector storage and retrieval
- Custom markdown chunker with frontmatter parsing
- Intent classifier with keyword rules and word boundary matching

## Project Structure

```
src/                          # Next.js frontend
  app/
    api/token/route.ts        # LiveKit token generation endpoint
    layout.tsx                # Root layout
    page.tsx                  # Home page
    globals.css               # Global styles
  components/
    voice-interface.tsx       # Main voice session component
    ui/siri-wave.tsx          # WebGL voice orb animation
  lib/
    utils.ts                  # Utility functions

agent/                        # Python voice agent
  agent.py                    # LiveKit agent entry point
  requirements.txt            # Python dependencies
  knowledge/
    __init__.py               # Package exports
    models.py                 # Data models (chunks, citations, metadata)
    chunker.py                # Markdown document chunker
    store.py                  # ChromaDB vector store wrapper
    retriever.py              # RAG retriever with intent classification
    ingest.py                 # CLI to rebuild the vector index

knowledge/sources/            # Markdown documents for RAG grounding
  resume.md
  github/profile.md
  projects/                   # Main project write-ups
  prs/                        # Open source PR summaries
  side_projects/              # Side project write-ups
```

## Setup

### Prerequisites

- Node.js 18 or later
- Python 3.10 or later
- A LiveKit Cloud account (or self-hosted LiveKit server)

### 1. Clone and install

```bash
git clone https://github.com/Premx24/Proxyy.git
cd Proxyy
npm install
```

### 2. Set up environment variables

Copy the example env file and fill in your LiveKit credentials:

```bash
cp .env.example .env
```

For the Python agent:

```bash
cp agent/.env.example agent/.env.local
```

### 3. Set up Python

```bash
python -m venv .venv
.venv/Scripts/activate     # Windows
pip install -r agent/requirements.txt
```

### 4. Build the knowledge index

```bash
npm run knowledge:ingest
```

This reads all the markdown files in `knowledge/sources/`, chunks them, and stores the embeddings in a local ChromaDB index.

### 5. Run the agent

```bash
npm run agent:dev
```

### 6. Run the frontend

```bash
npm run dev
```

Open http://localhost:3000 and tap the orb to start talking.

## Environment Variables

See `.env.example` for the full list. You need:

- `LIVEKIT_URL` - Your LiveKit server URL
- `LIVEKIT_API_KEY` - LiveKit API key
- `LIVEKIT_API_SECRET` - LiveKit API secret

## License

MIT
