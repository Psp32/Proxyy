"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useChat,
  useConnectionState,
  useDataChannel,
  useLocalParticipant,
  useVoiceAssistant,
} from "@livekit/components-react";
import { ConnectionState } from "livekit-client";
import { SendHorizontal, X } from "lucide-react";
import { SiriWave } from "@/components/ui/siri-wave";
import { AICanvas } from "@/components/ai-canvas";
import type { VisualizationData } from "@/lib/canvas-types";
import { cn } from "@/lib/utils";

type ConnectionDetails = {
  token: string;
  serverUrl: string;
  roomName: string;
};

function VoiceSession({
  onDisconnect,
  showTextInput,
  onCloseTextInput,
}: {
  onDisconnect: () => void;
  showTextInput: boolean;
  onCloseTextInput: () => void;
}) {
  const { state: agentState } = useVoiceAssistant();
  const { isMicrophoneEnabled } = useLocalParticipant();
  const connectionState = useConnectionState();
  const { send, chatMessages, isSending } = useChat();
  const [message, setMessage] = useState("");
  const [citationSources, setCitationSources] = useState<Array<{ title: string; source_type: string; section?: string; url?: string; excerpt?: string }>>([]);
  const [vizData, setVizData] = useState<VisualizationData | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useDataChannel("citations", (msg) => {
    const payload = msg.payload ? new TextDecoder().decode(msg.payload) : "";
    if (!payload) return;

    try {
      const parsed = JSON.parse(payload) as {
        sources?: Array<{
          title?: string;
          source_type?: string;
          section?: string;
          url?: string;
          excerpt?: string;
        }>;
      };
      const nextSources = parsed.sources ?? [];
      if (nextSources.length > 0) {
        setCitationSources(nextSources as typeof citationSources);
      }
    } catch {
      // ignore malformed citation payloads
    }
  });

  useDataChannel("visualization", (msg) => {
    const payload = msg.payload ? new TextDecoder().decode(msg.payload) : "";
    if (!payload) return;

    try {
      const parsed = JSON.parse(payload) as {
        type?: string;
        title?: string;
        nodes?: any[];
        edges?: any[];
        metadata?: any;
      };
      if (!parsed || parsed.type === "clear" || !parsed.nodes || parsed.nodes.length === 0) {
        setVizData(null);
      } else {
        setVizData(parsed as VisualizationData);
      }
    } catch {
      // ignore malformed visualization payloads
    }
  });

  const isConnected = connectionState === ConnectionState.Connected;
  const isActive =
    isConnected &&
    (agentState === "listening" ||
      agentState === "speaking" ||
      agentState === "thinking" ||
      isMicrophoneEnabled);

  useEffect(() => {
    if (showTextInput) {
      inputRef.current?.focus();
    }
  }, [showTextInput]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleOrbClick = useCallback(() => {
    if (!isConnected) return;
    onDisconnect();
  }, [isConnected, onDisconnect]);

  const handleSend = useCallback(
    async (event: React.FormEvent) => {
      event.preventDefault();
      const trimmed = message.trim();
      if (!trimmed || isSending) return;

      await send(trimmed);
      setMessage("");
    },
    [message, isSending, send],
  );

  const statusLabel = !isConnected
    ? "Connecting..."
    : agentState === "speaking"
      ? "Speaking"
      : agentState === "thinking"
        ? "Thinking"
        : agentState === "listening"
          ? "Listening"
          : isMicrophoneEnabled
            ? "Tap to end"
            : "Tap to speak";

  return (
    <>
      <RoomAudioRenderer />

      <div className={cn(
        "flex flex-1 flex-col items-center px-6 transition-all duration-500 ease-out",
        vizData ? "justify-start pt-6" : "justify-center",
      )}>
        {/* AI Canvas — renders above the orb when visualization data is present */}
        {vizData && (
          <AICanvas
            data={vizData}
            onDismiss={() => setVizData(null)}
          />
        )}

        <button
          type="button"
          onClick={handleOrbClick}
          disabled={!isConnected}
          aria-label={isMicrophoneEnabled ? "End conversation" : "Start talking"}
          className={cn(
            "group relative flex items-center justify-center rounded-full transition-transform duration-300",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0c]",
            isConnected && "cursor-pointer hover:scale-[1.02] active:scale-[0.98]",
            !isConnected && "cursor-wait opacity-80",
            vizData && "mt-4",
          )}
        >
          <SiriWave
            variant="fluid-dots"
            size={vizData ? 200 : 320}
            active={isActive}
            speaking={agentState === "speaking"}
            className="shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
          />
        </button>

        {citationSources.length > 0 && (
          <div className="mt-6 w-full max-w-xl rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left text-sm text-zinc-300 backdrop-blur-md">
            <p className="mb-3 text-[10px] font-medium uppercase tracking-[0.2em] text-zinc-500">
              sources used
            </p>
            <ul className="space-y-3">
              {citationSources.map((source, index) => (
                <li key={`${source.title}-${index}`} className="rounded-xl border border-white/5 bg-black/10 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-medium text-zinc-200">{source.title}</span>
                    <span className="rounded-full border border-white/10 bg-white/[0.03] px-2 py-0.5 text-[10px] uppercase tracking-[0.12em] text-zinc-400">
                      {source.source_type}
                    </span>
                  </div>
                  {source.section && (
                    <p className="mt-1 text-xs text-zinc-400">{source.section}</p>
                  )}
                  {source.excerpt && (
                    <p className="mt-2 text-xs leading-relaxed text-zinc-300">&ldquo;{source.excerpt}&rdquo;</p>
                  )}
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2 inline-block text-xs text-cyan-300 underline underline-offset-4"
                    >
                      Open source
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <p className="mt-8 text-sm tracking-wide text-zinc-500 transition-colors duration-300">
          {statusLabel}
        </p>
      </div>

      {showTextInput && (
        <div className="absolute inset-x-0 bottom-24 mx-auto w-full max-w-lg px-6">
          <div className="overflow-hidden rounded-2xl border border-white/10 bg-[#141416]/90 shadow-2xl backdrop-blur-xl">
            {chatMessages.length > 0 && (
              <div className="max-h-40 space-y-2 overflow-y-auto border-b border-white/8 px-4 py-3">
                {chatMessages.slice(-6).map((msg) => (
                  <p key={msg.timestamp} className="text-sm leading-relaxed text-zinc-300">
                    <span className="text-zinc-500">
                      {msg.from?.isLocal ? "You" : "Twin"}:
                    </span>{" "}
                    {msg.message}
                  </p>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}

            <form onSubmit={handleSend} className="flex items-center gap-2 p-3">
              <input
                ref={inputRef}
                type="text"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Type a question..."
                disabled={!isConnected || isSending}
                className="flex-1 bg-transparent px-2 py-2 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none"
              />
              <button
                type="submit"
                disabled={!message.trim() || isSending || !isConnected}
                aria-label="Send message"
                className="flex h-9 w-9 items-center justify-center rounded-full text-zinc-400 transition-colors hover:bg-white/8 hover:text-zinc-200 disabled:opacity-40"
              >
                <SendHorizontal className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={onCloseTextInput}
                aria-label="Close text input"
                className="flex h-9 w-9 items-center justify-center rounded-full text-zinc-500 transition-colors hover:bg-white/8 hover:text-zinc-300"
              >
                <X className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export function VoiceInterface() {
  const [connectionDetails, setConnectionDetails] = useState<ConnectionDetails | null>(
    null,
  );
  const [isConnecting, setIsConnecting] = useState(false);
  const [showTextInput, setShowTextInput] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startSession = useCallback(async () => {
    if (isConnecting || connectionDetails) return;

    setIsConnecting(true);
    setError(null);

    try {
      const response = await fetch("/api/token");
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error ?? "Failed to connect");
      }

      setConnectionDetails(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Connection failed");
    } finally {
      setIsConnecting(false);
    }
  }, [connectionDetails, isConnecting]);

  const endSession = useCallback(() => {
    setConnectionDetails(null);
    setShowTextInput(false);
  }, []);

  return (
    <div className="relative flex min-h-screen flex-col bg-[#0a0a0c]">
      <main className="relative flex flex-1 flex-col">
        {!connectionDetails ? (
          <div className="flex flex-1 flex-col items-center justify-center px-6">
            <button
              type="button"
              onClick={startSession}
              disabled={isConnecting}
              aria-label="Start voice conversation"
              className={cn(
                "group relative flex items-center justify-center rounded-full transition-transform duration-300",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/30 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0c]",
                !isConnecting && "cursor-pointer hover:scale-[1.02] active:scale-[0.98]",
                isConnecting && "cursor-wait opacity-80",
              )}
            >
              <SiriWave
                variant="fluid-dots"
                size={320}
                active={isConnecting}
                speaking={false}
                className="shadow-[0_20px_60px_rgba(0,0,0,0.6)]"
              />
            </button>

            <p className="mt-8 text-sm tracking-wide text-zinc-500">
              {isConnecting ? "Connecting..." : "Tap to talk"}
            </p>

            {error && (
              <p className="mt-4 max-w-sm text-center text-sm text-red-400/90">{error}</p>
            )}
          </div>
        ) : (
          <LiveKitRoom
            token={connectionDetails.token}
            serverUrl={connectionDetails.serverUrl}
            connect
            audio={{
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true,
            }}
            className="flex flex-1 flex-col"
            onDisconnected={endSession}
          >
            <VoiceSession
              onDisconnect={endSession}
              showTextInput={showTextInput}
              onCloseTextInput={() => setShowTextInput(false)}
            />
          </LiveKitRoom>
        )}
      </main>
    </div>
  );
}
