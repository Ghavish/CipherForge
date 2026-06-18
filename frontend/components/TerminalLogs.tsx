'use client';
import { Terminal } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface TerminalLogsProps {
  logs: string[];
  projectId: string | null;
}

export default function TerminalLogs({ logs, projectId }: TerminalLogsProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="w-full max-w-4xl bg-[#0D0221] border border-[#7B2CBF]/20 rounded-xl overflow-hidden shadow-[0_0_30px_rgba(123,44,191,0.1)] mt-6">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-[#7B2CBF]/20 bg-[#121214]">
        <Terminal className="w-4 h-4 text-[#7B2CBF]" />
        <span className="text-xs font-mono text-purple-400 uppercase tracking-widest">
          {projectId ? `WORKSPACE: [${projectId}]` : 'SYSTEM_IDLE'}
        </span>
      </div>
      
      <div ref={scrollRef} className="p-4 h-64 overflow-y-auto font-mono text-sm space-y-2 bg-[#0A0A0B] relative">
        {logs.length === 0 && <div className="text-gray-600 italic">Awaiting process execution...</div>}
        
        {logs.map((log, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-gray-300"
          >
            <span className="text-[#7B2CBF] mr-2 font-bold">{'>'}</span>
            {log}
          </motion.div>
        ))}

        {projectId && (
          <motion.div 
            animate={{ opacity: [1, 0, 1] }} 
            transition={{ repeat: Infinity, duration: 0.8 }}
            className="inline-block w-2 h-4 bg-purple-500 ml-1 translate-y-1"
          />
        )}
      </div>
    </div>
  );
}