import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  // --- Validate required env vars before doing anything ---
  const bandApiUrl      = process.env.BAND_API_URL;
  const bandRoomId      = process.env.BAND_ROOM_ID;
  const bandAgentApiKey = process.env.BAND_AGENT_API_KEY;
  const managerUuid     = process.env.MANAGER_UUID;

  const missing = [
    !bandApiUrl      && 'BAND_API_URL',
    !bandRoomId      && 'BAND_ROOM_ID',
    !bandAgentApiKey && 'BAND_AGENT_API_KEY',
    !managerUuid     && 'MANAGER_UUID',
  ].filter(Boolean);

  if (missing.length > 0) {
    return NextResponse.json(
      { error: `Missing environment variables: ${missing.join(', ')}` },
      { status: 500 }
    );
  }

  try {
    const { taskDescription } = await request.json();

    if (!taskDescription?.trim()) {
      return NextResponse.json({ error: 'taskDescription is required' }, { status: 400 });
    }

    const projectId = `PROJ-${Math.floor(Math.random() * 9000) + 1000}`;

    const endpoint = `${bandApiUrl}/agent/chats/${bandRoomId}/messages`;

    const msgRes = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'X-API-Key': bandAgentApiKey!,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: {
          content: `NEW_BUILD_REQUEST: [Project ID]: ${projectId} [Task]: ${taskDescription}`,
          mentions: [{ id: managerUuid }],
        },
      }),
    });

    if (!msgRes.ok) {
      const errText = await msgRes.text();
      throw new Error(`Band API error ${msgRes.status}: ${errText}`);
    }

    return NextResponse.json({ projectId, roomId: bandRoomId });

  } catch (error: any) {
    console.error('[start-session] Error:', error);
    return NextResponse.json({ error: String(error?.message ?? error) }, { status: 500 });
  }
}