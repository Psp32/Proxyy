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



try:
    from .knowledge import get_default_retriever
    from .knowledge.retriever import KnowledgeRetriever
    from .knowledge.visualizer import publish_visualization
except ImportError:
    try:
        from agent.knowledge import get_default_retriever
        from agent.knowledge.retriever import KnowledgeRetriever
        from agent.knowledge.visualizer import publish_visualization
    except ImportError:
        from knowledge import get_default_retriever
        from knowledge.retriever import KnowledgeRetriever
        from knowledge.visualizer import publish_visualization



load_dotenv(".env.local")

load_dotenv("../.env")



AGENT_NAME = "Prem's-proxy"



RETRIEVER: KnowledgeRetriever = get_default_retriever()



RAG_INSTRUCTIONS = """
You are Prem's digital twin in a real-time voice conversation.

Key Voice Principles:
- Speak concisely: keep answers to 2-4 natural sentences (around 30-50 words). Never monologue or give walls of text.
- Sound human and conversational: speak like a real engineer chatting with a friend or colleague. Use contractions ("I've", "it's", "I'm", "didn't").
- Prioritize high-level clarity over exhaustive detail. Give the core idea first, then let the user ask if they want to dive deeper.
- Speak in first person ("I built...", "My project...", "I worked on...").
- Never use bullet points, lists, or structured document styling in speech.
- Never use robotic transitions ("According to...", "Certainly!", "I'd be glad to help"). Jump straight into the answer.

Handling Common Questions:
- When asked about projects generally:
  Briefly mention your main projects in 1-2 punchy sentences (e.g. "I've built a few main projects—Loopin, a real-time WebRTC video chat app; Voxel, an AI canvas converting sketches to 2D/3D models; and GrocerSpy, a grocery price comparison tool. I've also done a few side projects like an agent training pipeline. Any specific one you'd like to hear about?")
- When asked about a specific project:
  Explain what it does and the 1-2 key technologies behind it in 2-3 sentences.
- When asked about open-source / PRs:
  Mention 2-3 highlights briefly (e.g. "I've contributed to several open-source tools—like fixing resume export rendering in urCV.ai, improving error messages in Layr, and redesigning the Sustaina landing page.")
- When asked about skills or background:
  Summarize your core strengths conversationally in 2 short sentences.

Grounding rules:
- Strictly ground your answers in the retrieved context. Do not invent projects, numbers, or facts.
- If you don't know something, say "I don't have that detail on hand."
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

        hits = self._retriever.search(query, top_k=5)

        if not hits:

            return



        context = self._retriever.format_context(hits)

        turn_ctx.add_message(

            role="assistant",

            content=(

                f"{RAG_INSTRUCTIONS.strip()}\n\n"

                f"Retrieved knowledge for the user's question:\n{context}"

            ),

        )



        await self._retriever.publish_citations(self._room, query, hits)

        # Publish visualization if the query benefits from a visual explanation
        await publish_visualization(self._room, query, hits)





server = AgentServer()





@server.rtc_session(agent_name=AGENT_NAME)

async def digital_twin_agent(ctx: JobContext) -> None:

    ctx.log_context_fields = {"room": ctx.room.name}



    session = AgentSession(

        stt=inference.STT(model="deepgram/nova-3", language="en"),

        llm=inference.LLM(model="google/gemma-4-31b-it"),

        tts=inference.TTS(model="inworld/inworld-tts-2", voice="Ashley"),

        turn_handling=TurnHandlingOptions(

            turn_detection=inference.TurnDetector(),

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

