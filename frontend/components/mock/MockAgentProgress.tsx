'use client';
import { useState, useEffect } from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { getMockSwarmHealth } from '@/lib/mock-data';

export default function MockAgentProgress({ isActive }: { isActive: boolean }) {
  const [health, setHealth] = useState(getMockSwarmHealth(0));

  useEffect(() => {
    if (!isActive) return;

    let step = 0;
    setHealth(getMockSwarmHealth(step));
    
    const mockInterval = setInterval(() => {
      step++;
      setHealth(getMockSwarmHealth(step));
      if (step >= 5) clearInterval(mockInterval);
    }, 4000); 

    return () => clearInterval(mockInterval);
  }, [isActive]);

  const StatusIcon = ({ status }: { status: string }) => {
    if (status === 'complete') return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    if (status === 'active') return <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />;
    return <Circle className="w-5 h-5 text-gray-700" />;
  };

  const agents = [
    { key: 'conductor', label: 'Manager' }, { key: 'architect', label: 'Architect' },
    { key: 'ui', label: 'UI Coder' }, { key: 'api', label: 'API Coder' },
    { key: 'reviewer', label: 'QA Review' }, { key: 'merge', label: 'Deployment' },
  ];

  return (
    <div className="w-full max-w-4xl bg-[#121214] border border-white/5 rounded-xl p-6 shadow-lg mt-6">
      <div className="flex justify-between items-center">
        {agents.map((agent, index) => (
          <div key={agent.key} className="flex flex-col items-center gap-2 relative z-10">
            <div className="bg-[#0E0E0F] rounded-full p-1 border border-white/5 shadow-md">
              <StatusIcon status={health[agent.key as keyof typeof health]} />
            </div>
            <span className={`text-xs font-medium tracking-wide ${health[agent.key as keyof typeof health] === 'active' ? 'text-emerald-400' : 'text-gray-400'}`}>
              {agent.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}