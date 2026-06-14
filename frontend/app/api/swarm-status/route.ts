// frontend/app/api/status/route.ts
import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const projectId = searchParams.get('projectId');
  
  try {
    const response = await fetch(`${process.env.BAND_API_URL}/projects/${projectId}/status`, {
      headers: { 
        'Authorization': `Bearer ${process.env.BAND_API_KEY}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) throw new Error("Swarm API unreachable");
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("DEBUG API ERROR:", error); 
    return NextResponse.json({ error: "Failed to fetch", details: String(error) }, { status: 500 });
  }
}