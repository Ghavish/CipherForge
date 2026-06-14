'use client';

import { Bell, User } from 'lucide-react';

export default function Topbar() {
  return (
    <header className="h-16 border-b border-white/5 bg-[#0E0E0F]/80 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10">
      <div className="flex items-center gap-2 text-sm font-mono text-gray-400">
        <span>Workspace</span>
        <span className="text-gray-600">/</span>
        <span className="text-blue-400 animate-pulse">AWAITING_INPUT</span>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-400 hover:text-gray-200 transition-colors">
          <Bell className="w-4 h-4" />
        </button>
        <div className="w-8 h-8 rounded-full bg-[#1A1A1C] border border-white/10 flex items-center justify-center cursor-pointer hover:border-white/20 transition-colors">
          <User className="w-4 h-4 text-gray-400" />
        </div>
      </div>
    </header>
  );
}