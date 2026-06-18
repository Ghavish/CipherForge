'use client';
import { motion } from 'framer-motion';

interface AgentProgressProps {
  currentStage: string;
}

const STAGES = ['Initializing', 'Planning', 'Architecture', 'Coding', 'QA Review', 'Deployment'];

export default function AgentProgress({ currentStage }: AgentProgressProps) {
  const activeIndex = STAGES.indexOf(currentStage);

  return (
    <div className="w-full max-w-4xl mb-8 p-8 bg-[#0D0221] border border-[#7B2CBF]/20 rounded-xl shadow-[0_0_40px_rgba(123,44,191,0.1)] relative overflow-hidden">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[#7B2CBF]/5 blur-3xl pointer-events-none" />

      <div className="flex justify-between items-center relative z-10">
        <div className="absolute top-3 left-0 w-full h-0.5 bg-[#1f1f22] z-0 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-linear-to-r from-[#7B2CBF] to-purple-400"
            initial={{ width: '0%' }}
            animate={{ width: activeIndex >= 0 ? `${(activeIndex / (STAGES.length - 1)) * 100}%` : '0%' }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />
        </div>

        {STAGES.map((stage, idx) => {
          const isActive = idx === activeIndex;
          const isPast = idx < activeIndex;

          return (
            <div key={stage} className="flex flex-col items-center z-10 w-24">
              <motion.div
                animate={{ 
                  backgroundColor: isPast || isActive ? '#7B2CBF' : '#1f1f22',
                  scale: isActive ? 1.3 : 1,
                  boxShadow: isActive ? '0 0 20px rgba(123,44,191,0.6)' : 'none'
                }}
                transition={{ duration: 0.4 }}
                className={`w-6 h-6 rounded-full mb-3 flex items-center justify-center border-2 ${isPast || isActive ? 'border-transparent' : 'border-[#3a3a40]'}`}
              />
              <span className={`text-xs font-mono tracking-wider text-center transition-colors duration-300 ${isActive || isPast ? 'text-purple-300' : 'text-gray-600'}`}>
                {stage}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}