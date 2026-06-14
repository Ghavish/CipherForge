// frontend/app/page.tsx
'use client';
import { useState, useEffect } from 'react';
import { useSwarmStatus } from '../hooks/UseSwarmStatus';
import AgentProgress from '../components/AgentProgress';
import TerminalLogs from '../components/TerminalLogs';
import Sidebar from '../components/layout/Sidebar';
import Topbar from '../components/layout/Topbar';

export default function Home() {
  const [projectId] = useState<string | null>("PROJ-123");
  const { status } = useSwarmStatus(projectId);
  const [displayedLogs, setDisplayedLogs] = useState<string[]>([]);

  useEffect(() => {
    // Check if the API returned data and logs exist
    if (status?.logs && Array.isArray(status.logs)) {
      setDisplayedLogs(prevLogs => {
        const existingLogs = new Set(prevLogs);
        const newLogs = status.logs.filter((log: string) => !existingLogs.has(log));
        return newLogs.length > 0 ? [...prevLogs, ...newLogs] : prevLogs;
      });
    }
  }, [status]);

  return (
    <div className="flex h-screen bg-[#0E0E0F] text-white overflow-hidden font-sans">
      <Sidebar />
      <main className="flex-1 flex flex-col relative overflow-y-auto">
        <Topbar />
        
        <div className="flex-1 flex flex-col items-center pt-20 px-8">
          <div className="w-full max-w-3xl mb-10">
            <h1 className="text-3xl font-bold text-gray-100 mb-2">
              Active Swarm Deployment
            </h1>
            <p className="text-amber-500 font-mono">
              Project: {projectId || "Initializing..."}
            </p>
          </div>

          {/* Real data is now being passed to components */}
          <AgentProgress status={status} />
          <TerminalLogs logs={displayedLogs} />
        </div>
      </main>
    </div>
  );
}

