'use client';
import { useState, useEffect } from 'react';
import { Terminal } from 'lucide-react';
import { mockLogs, MOCK_PROJECT_ID } from '@/lib/mock-data';

export default function MockTerminalLogs({ isActive }: { isActive: boolean }) {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (!isActive) {
      setLogs([]);
      return;
    }

    setLogs([]);
    let currentStep = 0;
    
    const mockInterval = setInterval(() => {
      if (currentStep < mockLogs.length) {
        setLogs(prev => [...prev, mockLogs[currentStep]]);
        currentStep++;
      } else {
        clearInterval(mockInterval);
      }
    }, 2000);

    return () => clearInterval(mockInterval);
  }, [isActive]);

  return (
    <div className="w-full max-w-4xl bg-[#0A0A0B] border border-white/5 rounded-xl overflow-hidden shadow-2xl mt-6">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#121214]">
        <Terminal className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-mono text-emerald-400">
          {isActive ? `OFFLINE_SIMULATION: [${MOCK_PROJECT_ID}]` : 'SYSTEM_IDLE'}
        </span>
      </div>
      <div className="p-4 h-64 overflow-y-auto font-mono text-sm space-y-2">
        {logs.length === 0 && <div className="text-gray-600 italic">Waiting for mock initialization...</div>}
        {logs.map((log, idx) => (
          <div key={idx} className="text-gray-300">{log}</div>
        ))}
      </div>
    </div>
  );
}