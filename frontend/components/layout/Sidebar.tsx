'use client';

import { LayoutDashboard, History, Settings, Cpu } from 'lucide-react';
import { motion } from 'framer-motion';

const navItems = [
  { icon: LayoutDashboard, label: 'Active Build', active: true },
  { icon: History, label: 'Project History', active: false },
  { icon: Settings, label: 'Swarm Config', active: false },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-[#0A0A0B] border-r border-white/5 flex flex-col pt-6 pb-4 shrink-0">
      {/* Brand / Logo Area */}
      <div className="flex items-center gap-3 px-6 mb-12">
        <div className="w-8 h-8 rounded-lg bg-linear-to-tr from-blue-600 to-indigo-400 flex items-center justify-center shadow-[0_0_15px_rgba(96,165,250,0.3)]">
          <Cpu className="w-5 h-5 text-white" />
        </div>
        <span className="text-gray-100 font-semibold tracking-wide">Swarm Factory</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        {navItems.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all relative ${
                item.active 
                  ? 'bg-white/10 text-gray-100' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
              }`}
            >
              <Icon className={`w-4 h-4 ${item.active ? 'text-blue-400' : ''}`} />
              <span className="z-10">{item.label}</span>
              {item.active && (
                <motion.div 
                  layoutId="activeNav"
                  className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 rounded-r-full"
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer Status */}
      <div className="px-6 mt-auto">
        <div className="flex items-center gap-2 text-xs font-mono text-gray-500">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Network: CONNECTED
        </div>
      </div>
    </aside>
  );
}