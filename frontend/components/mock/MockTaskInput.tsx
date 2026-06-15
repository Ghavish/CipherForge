'use client';
import { useState } from 'react';
import { Play, Loader2, Code2 } from 'lucide-react';
import { MOCK_PROJECT_ID, MOCK_ROOM_ID, delay } from '@/lib/mock-data';

export default function MockTaskInput({ onSessionCreated }: { onSessionCreated: (pId: string, rId: string) => void }) {
  const [prompt, setPrompt] = useState('');
  const [isDeploying, setIsDeploying] = useState(false);

  const handleMockDeploy = async () => {
    if (!prompt.trim()) return;
    setIsDeploying(true);
    
    // Simulate API network latency
    await delay(800);
    
    // Instantly return the mock IDs without hitting the backend
    onSessionCreated(MOCK_PROJECT_ID, MOCK_ROOM_ID);
    setPrompt('');
    setIsDeploying(false);
  };

  return (
    <div className="w-full max-w-4xl bg-[#0A0A0B] border border-emerald-500/30 rounded-2xl p-6 shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1 bg-linear-to-r from-transparent via-emerald-500/50 to-transparent blur-sm" />
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-2 mb-2">
          <Code2 className="w-5 h-5 text-emerald-400" />
          <h2 className="text-lg font-medium text-white tracking-wide">Mock Offline Factory</h2>
        </div>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={isDeploying}
          placeholder="[OFFLINE MODE] Describe the software..."
          className="w-full h-32 bg-[#121214] border border-white/10 rounded-xl p-4 text-gray-300 font-mono text-sm focus:outline-none focus:border-emerald-500/50 transition-all resize-none disabled:opacity-50"
        />
        <div className="flex justify-end mt-2">
          <button
            onClick={handleMockDeploy}
            disabled={isDeploying || !prompt.trim()}
            className="group relative flex items-center gap-2 px-6 py-3 bg-white text-black font-semibold rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50"
          >
            {isDeploying ? <><Loader2 className="w-4 h-4 animate-spin" /><span>Simulating...</span></> : <><Play className="w-4 h-4" /><span>Test Deploy</span></>}
          </button>
        </div>
      </div>
    </div>
  );
}