// frontend/app/api/status/route.ts
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const projectId = searchParams.get('projectId');
  
  // 1. Safety Check: Guard against empty requests
  if (!projectId || projectId === 'null') {
    return NextResponse.json({ error: "Missing or invalid projectId" }, { status: 400 });
  }

  try {
    // Note: Since you are using LangGraph, ensure BAND_API_URL is pointing 
    // to your custom Python FastAPI/Flask server on your Oracle VPS!
    const response = await fetch(`${process.env.BAND_API_URL}/projects/${projectId}/status`, {
      headers: { 
        'Authorization': `Bearer ${process.env.BAND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      cache: 'no-store' // 2. Cache Busting: Guarantee fresh data on every poll
    });

    if (!response.ok) {
      throw new Error(`Backend returned status: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error(`[Swarm Status Error] Project ${projectId}:`, error); 
    
    // 3. Safe Fallback: Return a valid, empty state so the UI AgentProgress tracker doesn't crash
    return NextResponse.json({
      conductor: 'pending',
      architect: 'pending',
      ui: 'pending',
      api: 'pending',
      reviewer: 'pending',
      merge: 'pending'
    }, { status: 503 }); // 503 Service Unavailable is more accurate for polling drops
  }
}