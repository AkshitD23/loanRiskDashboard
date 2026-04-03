import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, History, Settings, ShieldAlert } from 'lucide-react';
import { cn } from '../lib/utils';

export function Sidebar() {
  const routes = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'History', path: '/history', icon: History },
  ];

  return (
    <aside className="w-64 border-r border-white/10 bg-surface backdrop-blur-3xl h-screen flex flex-col fixed left-0 top-0">
      <div className="h-16 flex items-center px-6 border-b border-white/10">
        <ShieldAlert className="w-6 h-6 text-primary mr-3" />
        <span className="text-lg font-semibold tracking-wide text-white">RiskModel</span>
      </div>
      <nav className="flex-1 py-6 px-3 space-y-2">
        {routes.map((route) => (
          <NavLink
            key={route.path}
            to={route.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200',
                isActive 
                  ? 'bg-primary/20 text-primary font-medium' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              )
            }
          >
            <route.icon className="w-5 h-5" />
            {route.name}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-white/10">
        <button className="flex w-full items-center gap-3 px-4 py-3 text-slate-400 hover:text-slate-200 rounded-xl hover:bg-white/5 transition-all">
          <Settings className="w-5 h-5" />
          Settings
        </button>
      </div>
    </aside>
  );
}
