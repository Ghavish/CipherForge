'use client';

import { Terminal } from 'lucide-react';
import { motion } from 'framer-motion';
import { useEffect, useRef } from 'react';

interface TerminalLogsProps {
  logs: string[] | undefined;
}

export default function TerminalLogs({ logs = [] }: TerminalLogsProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logic
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="w-full max-w-3xl bg-[#0A0A0B] border border-white/5 rounded-xl overflow-hidden shadow-2xl mt-6">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5 bg-[#121214]">
        <Terminal className="w-4 h-4 text-gray-400" />
        <span className="text-xs font-mono text-gray-400 uppercase tracking-widest">swarm_execution.log</span>
      </div>
      
      <div ref={scrollRef} className="p-4 h-64 overflow-y-auto font-mono text-sm space-y-2 bg-black">
        {logs.map((log, idx) => (
          <motion.div 
            key={idx}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-gray-300"
          >
            <span className="text-emerald-500 mr-2">{'>'}</span>
            {log}
          </motion.div>
        ))}
        {/* Blinking Cursor */}
        <motion.div 
          animate={{ opacity: [1, 0, 1] }} 
          transition={{ repeat: Infinity, duration: 0.8 }}
          className="inline-block w-2 h-4 bg-emerald-500 ml-1"
        />
      </div>
    </div>
  );
}