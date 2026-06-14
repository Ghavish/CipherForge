'use client';
import { motion } from 'framer-motion';

interface AgentProgressProps {
  status: any;
}

const STAGES = ['Planning', 'Coding', 'QA Review', 'Deployment'];

export default function AgentProgress({ status }: AgentProgressProps) {
  const activeIndex = STAGES.indexOf(status?.currentStage || '');

  return (
    <div className="w-full max-w-3xl mb-8 p-6 bg-[#0A0A0B] border border-white/5 rounded-xl shadow-lg">
      <div className="flex justify-between items-center relative">
        {STAGES.map((stage, idx) => (
          <div key={stage} className="flex flex-col items-center z-10">
            <motion.div
              animate={{ 
                backgroundColor: idx <= activeIndex ? '#d4af37' : '#1f1f22',
                scale: idx === activeIndex ? 1.2 : 1 
              }}
              className="w-4 h-4 rounded-full mb-2"
            />
            <span className={`text-xs font-mono ${idx <= activeIndex ? 'text-amber-500' : 'text-gray-600'}`}>
              {stage}
            </span>
          </div>
        ))}
        {/* Background Connector Line */}
        <div className="absolute top-2 left-0 w-full h-0.5 bg-[#1f1f22] z-0" />
      </div>
    </div>
  );
}