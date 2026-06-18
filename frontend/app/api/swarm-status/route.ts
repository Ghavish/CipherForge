// frontend/app/api/swarm-status/route.ts
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const projectId = searchParams.get('projectId');
  
  if (!projectId) {
    return NextResponse.json({ error: "Missing projectId" }, { status: 400 });
  }

  try {
    // Ping YOUR Python backend on the Oracle VPS (or localhost)
    const response = await fetch(`${process.env.NEXT_PUBLIC_PYTHON_BACKEND_URL}/status/${projectId}`, {
      cache: 'no-store'
    });

    if (!response.ok) throw new Error("Python backend unreachable");
    
    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error("Failed to fetch from Python backend:", error); 
    // Fallback so the UI stays clean if the server is booting up
    return NextResponse.json({ currentStage: 'Initializing', logs: [] }, { status: 503 });
  }
}