'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';

// Import our newly created distinct mock components
import MockTaskInput from '@/components/mock/MockTaskInput';
import MockAgentProgress from '@/components/mock/MockAgentProgress';
import MockTerminalLogs from '@/components/mock/MockTerminalLogs';

export default function TestPlayground() {
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);

  return (
    <div className="flex h-screen bg-[#0E0E0F] text-white">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-y-auto">
        <Topbar />
        
        {/* Banner to warn you that you are in the test area */}
        <div className="w-full bg-emerald-900/40 border-b border-emerald-500/30 text-emerald-200 text-xs py-2 px-8 text-center tracking-widest uppercase font-semibold">
          Offline Simulation Environment Active
        </div>

        <div className="flex-1 flex flex-col items-center pt-8 px-8">
          <MockTaskInput onSessionCreated={() => setIsSimulationRunning(true)} />
          <MockAgentProgress isActive={isSimulationRunning} />
          <MockTerminalLogs isActive={isSimulationRunning} />
        </div>
      </main>
    </div>
  );
}