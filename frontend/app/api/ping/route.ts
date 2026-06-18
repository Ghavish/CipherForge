import { NextResponse } from 'next/server';

export async function POST() {
  console.log("--- RUNNING HEALTH CHECK ---");

  const apiKey = process.env.BAND_API_KEY;

  if (!apiKey) {
    console.error(" FATAL: Missing BAND_API_KEY in .env.local!");
    return NextResponse.json({ error: "Missing API Key" }, { status: 500 });
  }

  try {
    // Using the exact logic you were provided
    const response = await fetch(`${process.env.BAND_API_URL}/health`, {
      method: "GET",
      headers: {
        "X-API-Key": apiKey
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`🔴HEALTH CHECK FAILED (Status ${response.status}):`, errorText);
      throw new Error(`Band API Error: ${response.status}`);
    }

    const data = await response.json();
    
    // Check if the status is exactly "ok" as requested by the snippet
    if (data.status === "ok") {
        console.log("✅ HEALTH CHECK PASSED! Band.ai is online.");
        return NextResponse.json({ success: true, message: "Connection to Band.ai is perfect!" });
    } else {
        console.warn("⚠️ Connected, but status is not 'ok':", data);
        return NextResponse.json({ success: false, message: "Connected, but abnormal status." });
    }
    
  } catch (error) {
    console.error("🔴 NETWORK CRASH:", error);
    return NextResponse.json({ error: "Ping Failed" }, { status: 500 });
  }
}