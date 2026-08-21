import asyncio
import os
import re

from dotenv import load_dotenv

from livekit import agents, rtc

from livekit.agents import (

    Agent,

    AgentServer,

    AgentSession,

    JobContext,

    TurnHandlingOptions,

    cli,

    inference,

    llm,

)

from livekit.agents import APIConnectOptions



try:
    from .knowledge import get_default_retriever
    from .knowledge.retriever import KnowledgeRetriever
    from .knowledge.visualizer import build_visualization, format_canvas_context, publish_visualization
except ImportError:
    try:
        from agent.knowledge import get_default_retriever
        from agent.knowledge.retriever import KnowledgeRetriever
        from agent.knowledge.visualizer import build_visualization, format_canvas_context, publish_visualization
    except ImportError:
        from knowledge import get_default_retriever
        from knowledge.retriever import KnowledgeRetriever
        from knowledge.visualizer import build_visualization, format_canvas_context, publish_visualization



load_dotenv(".env.local")

load_dotenv("../.env")



AGENT_NAME = "Prem's-proxy"



RETRIEVER: KnowledgeRetriever = get_default_retriever()

if not RETRIEVER.is_ready:
    RETRIEVER.ingest_sources()



RAG_INSTRUCTIONS = """
You are Prem's digital twin in a real-time voice conversation with an interactive AI Canvas on the user's screen.

Key Voice Principles:
- Speak concisely: keep answers to 2-4 natural sentences (around 30-50 words). Never monologue or give walls of text.
- Sound human and conversational: speak like a real engineer chatting with a friend or colleague. Use contractions ("I've", "it's", "I'm", "didn't").
- Prioritize high-level clarity over exhaustive detail. Give the core idea first, then let the user ask if they want to dive deeper.
- Speak in first person ("I built...", "My project...", "I worked on...").
- Never use bullet points, lists, or structured document styling in speech.
- Never use robotic transitions ("According to...", "Certainly!", "I'd be glad to help"). Jump straight into the answer.

Interactive AI Canvas Alignment:
- You are equipped with a live Interactive AI Canvas that automatically renders architecture diagrams, workflow pipelines, comparison charts, skill graphs, and project nodes on the user's screen.
- When an active diagram is displayed (see "Active Canvas Diagram"), naturally acknowledge or refer to it (e.g. "I've pulled up the architecture diagram on your screen", "As you can see in the data flow on the canvas...", "I've mapped out the components for you").
- If the user asks about the canvas ("what's on the canvas?", "explain this diagram", "can you draw/visualize X?"), speak with full confidence about the diagram rendered on screen and explain its components.
- Your voice explanation must align with the nodes, technologies, and connections visible on the canvas.

Handling Common Questions:
- When asked about projects generally:
  Briefly mention your main projects in 1-2 punchy sentences and reference the projects diagram on screen.
- When asked about a specific project:
  Explain what it does and the 1-2 key technologies behind it in 2-3 sentences matching the architecture on screen.
- When asked about open-source / PRs:
  Mention 2-3 highlights briefly (e.g. urCV.ai, Layr, Sustaina).
- When asked about skills or background:
  Summarize your core strengths conversationally in 2 short sentences.
- When asked to draw / sketch / visualize:
  Enthusiastically confirm you've mapped it out on the canvas and briefly walk through the main components.

Grounding rules:
- Strictly ground your answers in the retrieved context and canvas details. Do not invent projects, numbers, or facts.
- If you don't know something completely absent from both knowledge and canvas, say "I don't have that detail on hand."
"""


class TwinAssistant(Agent):
    def __init__(self, retriever: KnowledgeRetriever, room: rtc.Room) -> None:
        self._retriever = retriever
        self._room = room
        super().__init__(
            instructions=(
                "You are Prem's Proxy, speaking in a natural human voice. "
                "Keep every answer short, punchy, and conversational—usually 2 to 4 sentences. "
                "Answer directly in first person as Prem. "
                "Do not lecture, list bullet points, or speak too long. "
                "Ground all answers in the provided knowledge."
            ),
        )

    async def on_user_turn_completed(
        self,
        turn_ctx: llm.ChatContext,
        new_message: llm.ChatMessage,
    ) -> None:
        query = (new_message.text_content or "").strip()
        if not query or not self._retriever.is_ready:
            return

        # Filter out isolated background noises, clicks, or single punctuation
        cleaned_words = re.findall(r"\b\w+\b", query)
        if not cleaned_words:
            return

        hits = await asyncio.to_thread(self._retriever.search, query, top_k=5)

        if not hits:

            return



        context = self._retriever.format_context(hits)
        viz_data = build_visualization(query, hits)
        canvas_context = format_canvas_context(viz_data)

        turn_ctx.add_message(
            role="assistant",
            content=(
                f"{RAG_INSTRUCTIONS.strip()}\n\n"
                f"{canvas_context}\n\n"
                f"Retrieved knowledge for the user's question:\n{context}"
            ),
        )

        await self._retriever.publish_citations(self._room, query, hits)

        # Publish visualization to the frontend canvas
        await publish_visualization(self._room, query, hits, viz_data=viz_data)





server = AgentServer()







@server.rtc_session(agent_name=AGENT_NAME)

async def digital_twin_agent(ctx: JobContext) -> None:

    ctx.log_context_fields = {"room": ctx.room.name}



    session = AgentSession(

        stt=inference.STT(

            model="deepgram/nova-3",

            language="en",

            conn_options=APIConnectOptions(max_retry=1, retry_interval=1.0, timeout=5.0),

        ),

        llm=inference.LLM(
            model="google/gemma-4-31b-it",
        ),

        tts=inference.TTS(
            model="cartesia/sonic-2",
            voice=os.environ.get("CARTESIA_VOICE_ID", ""),
            conn_options=APIConnectOptions(max_retry=1, retry_interval=1.0, timeout=5.0),
        ),

        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            endpointing={
                "mode": "dynamic",
                "min_delay": 0.4,
                "max_delay": 1.2,
            },
            interruption={
                "enabled": True,
                "min_duration": 0.6,
                "min_words": 2,
                "resume_false_interruption": True,
            },
        ),

    )



    await session.start(

        room=ctx.room,

        agent=TwinAssistant(retriever=RETRIEVER, room=ctx.room),

    )

    await ctx.connect()



    greeting = (

        "Greet the user briefly and invite them to ask about Prem."

        if RETRIEVER.is_ready

        else "Greet the user briefly. Mention that your knowledge base is still being set up."

    )

    await session.generate_reply(instructions=greeting)





if __name__ == "__main__":

    cli.run_app(server)

