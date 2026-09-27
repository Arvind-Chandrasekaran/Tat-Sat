
import React from 'react';
import { NavigationTab } from '../types';
import { Home, Compass, PlusSquare, User, Activity, Terminal, RefreshCw } from 'lucide-react';

interface SidebarProps {
  activeTab: NavigationTab;
  onTabChange: (tab: NavigationTab) => void;
  semanticStatus?: 'idle' | 'loading' | 'success' | 'error';
  onShowLogs?: () => void;
  onReindex?: () => void;
}

const ShankhaIcon = ({ className, size = 20 }: { className?: string; size?: number }) => (
  <svg 
    viewBox="0 0 24 24" 
    fill="none" 
    stroke="currentColor" 
    strokeWidth="1.5" 
    strokeLinecap="round" 
    strokeLinejoin="round" 
    className={className}
    width={size}
    height={size}
  >
    <path d="M19 8c0-2-2-4-4.5-4-3 0-5 3-5 5.5 0 1 0 2.5 1 3.5" />
    <path d="M10.5 13c-2 1-4.5 1-6 0-1.5-1-2-3-1-5 0-3 3-5 7-5 3 0 6 2 8 5 .5 .8 1.5 2 1.5 4 0 2.5-2 4.5-4 5.5-3 1.5-7 1-9.5-1" />
    <path d="M14.5 8.5c0 0 .5 2 1.5 3" />
    <path d="M11.5 5.5c0 0 1 4 4 6.5" />
    <path d="M6 10.5c1 2 4 4 8 3" />
  </svg>
);

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, semanticStatus = 'idle', onShowLogs, onReindex }) => {
  const navItems = [
    { id: NavigationTab.FEED, icon: Home, label: "Feed" },
    { id: NavigationTab.EXPLORE, icon: Compass, label: "Explore" },
    { id: NavigationTab.CREATE, icon: PlusSquare, label: "Create" },
    { id: NavigationTab.PROFILE, icon: User, label: "Profile" },
  ];

  let statusColor = 'bg-slate-700';
  
  if (semanticStatus === 'loading') {
      statusColor = 'bg-amber-500 animate-pulse';
  } else if (semanticStatus === 'success') {
      statusColor = 'bg-emerald-500';
  } else if (semanticStatus === 'error') {
      statusColor = 'bg-rose-500';
  }

  return (
    <>
      {/* --- DESKTOP SIDEBAR (Hidden on Mobile) --- */}
      <div className="hidden md:flex w-64 h-screen sticky top-0 bg-slate-950 border-r border-slate-900 flex-col p-6 z-30">
        <div className="flex flex-col gap-1 mb-8 px-2">
          <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shadow-lg shadow-primary-900/20">
                  <ShankhaIcon className="text-white transform -rotate-12" size={20} />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-slate-100">TatSat</h1>
          </div>
          <div className="pl-11">
              <p className="text-[10px] text-slate-500 font-medium tracking-wider uppercase">The Clarion Call of Truth</p>
          </div>
        </div>

        <nav className="flex-1 flex flex-col gap-2">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`flex items-center gap-4 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  isActive 
                    ? 'bg-slate-900 text-primary-500 font-medium border border-slate-800' 
                    : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200 border border-transparent'
                }`}
              >
                <item.icon size={24} className={isActive ? 'text-primary-500' : 'text-slate-500 group-hover:text-slate-300'} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="mt-auto p-4 bg-slate-900/50 rounded-xl border border-slate-900 space-y-4">
          <div>
              <h4 className="text-sm font-semibold text-slate-300 mb-2">Discourse Health</h4>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[75%] shadow-[0_0_10px_rgba(16,185,129,0.3)]"></div>
              </div>
              <p className="text-xs text-slate-500 mt-2">Platform discourse is trending <span className="text-emerald-400 font-medium">Constructive</span>.</p>
          </div>
          
          <div className="pt-4 border-t border-slate-800">
              <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">System Status</span>
                  <div className="flex gap-2">
                      {onReindex && (
                          <button onClick={onReindex} className="text-slate-600 hover:text-emerald-400 transition-colors" title="Re-Index Graph">
                               <RefreshCw size={12} />
                          </button>
                      )}
                      {onShowLogs && (
                          <button onClick={onShowLogs} className="text-slate-600 hover:text-primary-400 transition-colors" title="View Logs">
                              <Terminal size={12} />
                          </button>
                      )}
                  </div>
              </div>
              <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${statusColor}`}></div>
                  <span className="text-xs text-slate-300 font-medium">{semanticStatus === 'success' ? 'PgVector Online' : 'Connecting...'}</span>
              </div>
          </div>
        </div>
      </div>

      {/* --- MOBILE BOTTOM NAVIGATION (Visible on Mobile) --- */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-slate-950/95 backdrop-blur-lg border-t border-slate-900 flex justify-around items-center px-2 z-50 pb-safe">
        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`flex flex-col items-center justify-center p-2 rounded-lg transition-all ${
                isActive ? 'text-primary-500' : 'text-slate-500'
              }`}
            >
              <item.icon size={24} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-[9px] font-medium mt-1">{item.label}</span>
            </button>
          );
        })}
        {/* Status Indicator Dot for Mobile */}
        <div className={`absolute top-2 right-2 w-1.5 h-1.5 rounded-full ${statusColor}`} />
      </div>
    </>
  );
};
