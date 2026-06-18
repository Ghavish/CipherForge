'use client';

import { useState } from 'react';
import { Play, Loader2, TerminalSquare } from 'lucide-react';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';
import AgentProgress from '@/components/AgentProgress';
import TerminalLogs from '@/components/TerminalLogs';
import { useSwarmStatus } from '@/hooks/UseSwarmStatus';

export default function Home() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [prompt, setPrompt] = useState('');
  const [isDeploying, setIsDeploying] = useState(false);

  // Hook handles data syncing automatically!
  const { status } = useSwarmStatus(projectId);

  const handleDeploy = async () => {
    if (!prompt.trim()) return;
    setIsDeploying(true);
    setProjectId(null); // Clear previous runs

    try {
      const response = await fetch('/api/start-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ taskDescription: prompt }),
      });

      const data = await response.json();
      
      // --- THE NEW DIAGNOSTIC BLOCK ---
      if (!response.ok) {
        alert(`API Error: ${data.error}`);
        setIsDeploying(false);
        return;
      }
      // --------------------------------
      
      if (data.projectId) {
        setProjectId(data.projectId); 
        setPrompt(''); 
      }
    } catch (error) {
      console.error('Failed to start swarm:', error);
    } finally {
      setIsDeploying(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleDeploy();
    }
  };

  return (
    <div className="flex h-screen bg-[#0E0E0F] text-white">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-y-auto relative">
        <Topbar />
        
        <div className="flex-1 flex flex-col items-center pt-8 px-8 pb-32">
          
          {projectId ? (
            <div className="w-full max-w-5xl flex flex-col items-center animate-in fade-in slide-in-from-bottom-4 duration-700">
              
              <AgentProgress currentStage={status.currentStage} />
              <TerminalLogs logs={status.logs} projectId={projectId} />
              
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center opacity-40 mt-20">
              <TerminalSquare className="w-16 h-16 mb-4 text-purple-500" />
              <h2 className="text-xl font-mono tracking-widest text-gray-400">AWAITING ARCHITECTURE DIRECTIVE</h2>
            </div>
          )}

        </div>

        {/* Command Bar */}
        <div className="absolute bottom-0 left-0 w-full p-8 bg-linear-to-t from-[#0E0E0F] via-[#0E0E0F] to-transparent">
          <div className="max-w-4xl mx-auto flex items-end gap-3 bg-[#121214] border border-purple-500/20 rounded-2xl p-2 shadow-[0_0_30px_rgba(123,44,191,0.1)] focus-within:border-purple-500/50 focus-within:shadow-[0_0_40px_rgba(123,44,191,0.2)] transition-all">
            
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isDeploying}
              placeholder="Describe the software you want to build... (Press Enter to deploy)"
              className="flex-1 max-h-32 min-h-14 bg-transparent p-4 text-gray-200 font-mono text-sm focus:outline-none resize-none disabled:opacity-50"
              rows={1}
            />

            <button
              onClick={handleDeploy}
              disabled={isDeploying || !prompt.trim()}
              className="group relative h-14 flex items-center justify-center gap-2 px-6 bg-white text-[#0D0221] font-bold rounded-xl hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0 overflow-hidden"
            >
              {isDeploying ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Deploying...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-black" />
                  <span>Build & Deploy</span>
                </>
              )}
              <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-linear-to-r from-transparent via-white/40 to-transparent" />
            </button>
            
          </div>
        </div>
      </main>
    </div>
  );
}