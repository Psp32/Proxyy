import { AccessToken } from "livekit-server-sdk";
import { RoomAgentDispatch, RoomConfiguration } from "@livekit/protocol";
import { NextResponse } from "next/server";

const AGENT_NAME = process.env.LIVEKIT_AGENT_NAME ?? "Prem's-proxy";

export async function GET() {
  const apiKey = process.env.LIVEKIT_API_KEY;
  const apiSecret = process.env.LIVEKIT_API_SECRET;
  const livekitUrl = process.env.LIVEKIT_URL;

  if (!apiKey || !apiSecret || !livekitUrl) {
    return NextResponse.json(
      { error: "LiveKit credentials are not configured" },
      { status: 500 },
    );
  }

  const roomName = `twin-${crypto.randomUUID().slice(0, 8)}`;
  const participantName = `user-${crypto.randomUUID().slice(0, 8)}`;

  const token = new AccessToken(apiKey, apiSecret, {
    identity: participantName,
    name: participantName,
  });

  token.addGrant({
    roomJoin: true,
    room: roomName,
    canPublish: true,
    canSubscribe: true,
    canPublishData: true,
  });

  token.roomConfig = new RoomConfiguration({
    name: roomName,
    agents: [
      new RoomAgentDispatch({
        agentName: AGENT_NAME,
      }),
    ],
  });

  return NextResponse.json({
    token: await token.toJwt(),
    serverUrl: livekitUrl,
    roomName,
  });
}
