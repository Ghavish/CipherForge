import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { prompt } = await request.json();
    
    // Validate that we have the necessary configuration
    const BAND_API_KEY = process.env.BAND_API_KEY;
    const MANAGER_UUID = process.env.MANAGER_UUID;

    if (!BAND_API_KEY || !MANAGER_UUID) {
      return NextResponse.json({ error: "Configuration missing" }, { status: 500 });
    }
    
    // Trigger the Manager via Band.ai REST API
    const response = await fetch("https://api.band.ai/v1/messages", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${BAND_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        to_agent_id: MANAGER_UUID,
        content: `NEW_BUILD_REQUEST: ${prompt}`
      })
    });

    if (!response.ok) {
      throw new Error("Failed to contact the swarm manager.");
    }

    return NextResponse.json({ success: true, message: "Swarm initiated successfully." });
    
  } catch (error) {
    console.error("Swarm Error:", error);
    return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
  }
}