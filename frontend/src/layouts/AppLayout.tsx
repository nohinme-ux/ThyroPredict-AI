import React, { useState } from 'react';
import {
  Activity,
  PlusCircle,
  Users,
  History,
  BarChart3,
  Database,
  Settings,
  ShieldCheck,
  AlertTriangle,
  Menu,
  X,
  FileSpreadsheet,
  CheckCircle2
} from 'lucide-react';

interface AppLayoutProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ activeTab, setActiveTab, children }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'new-prediction', label: 'New Prediction', icon: PlusCircle, badge: 'ML Core' },
    { id: 'participants', label: 'Participant Registry', icon: Users },
    { id: 'history', label: 'Prediction History', icon: History },
    { id: 'performance', label: 'Model Performance', icon: BarChart3, badge: '94.4%' },
    { id: 'dataset', label: 'Dataset Insights', icon: Database },
    { id: 'settings', label: 'Settings & Privacy', icon: Settings },
  ];

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      {/* Top Research Notification Banner */}
      <div className="bg-slate-900 text-slate-200 text-xs py-2 px-4 border-b border-slate-800 flex items-center justify-between no-print">
        <div className="flex items-center space-x-2">
          <span className="bg-sky-500/20 text-sky-300 font-semibold px-2 py-0.5 rounded text-[10px] uppercase tracking-wider border border-sky-500/30">
            Research Protocol
          </span>
          <span className="hidden sm:inline text-slate-300">
            ThyroPredict AI Decision Tree Research Platform • Not for direct clinical diagnosis.
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1.5 text-emerald-400">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-[11px] font-medium">Models Active & Connected</span>
          </div>
          <span className="text-slate-500 hidden md:inline">|</span>
          <span className="text-slate-400 text-[11px] hidden md:inline">Artifact v1.0.0</span>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar for Desktop */}
        <aside className="w-64 bg-slate-900 text-slate-300 flex-shrink-0 hidden md:flex flex-col justify-between border-r border-slate-800 no-print">
          <div>
            {/* Branding */}
            <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
              <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-teal-500 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
                <Activity className="h-6 w-6 stroke-[2.2]" />
              </div>
              <div>
                <h1 className="font-bold text-base text-white tracking-tight flex items-center">
                  ThyroPredict <span className="text-sky-400 ml-1">AI</span>
                </h1>
                <p className="text-[11px] text-slate-400">Decision Tree Research</p>
              </div>
            </div>

            {/* Navigation links */}
            <nav className="p-4 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30 font-semibold'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`h-4 w-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                          isActive
                            ? 'bg-sky-700/80 text-white'
                            : 'bg-slate-800 text-slate-400 border border-slate-700'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Sidebar Footer */}
          <div className="p-4 border-t border-slate-800 text-[11px] text-slate-400 space-y-2">
            <div className="bg-slate-800/80 p-3 rounded-lg border border-slate-700/50">
              <div className="flex items-center justify-between text-slate-300 mb-1">
                <span className="font-medium text-xs">Dataset Engine</span>
                <span className="text-[10px] text-emerald-400 font-mono">Synced</span>
              </div>
              <p className="text-[10px] text-slate-400">
                STS Clinical (269) + UCI Benchmark (3,772)
              </p>
            </div>
            <div className="px-1 text-[10px] text-slate-400 flex items-center justify-between">
              <span>DB: SQLite Local Persistent</span>
              <span className="text-slate-400">2026.1</span>
            </div>
          </div>
        </aside>

        {/* Mobile Header */}
        <div className="md:hidden bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between no-print w-full fixed top-8 z-20">
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-sky-600 flex items-center justify-center text-white">
              <Activity className="h-4 w-4" />
            </div>
            <span className="font-bold text-white text-sm">ThyroPredict AI</span>
          </div>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {/* Mobile Nav Drawer */}
        {mobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-30 bg-slate-950/80 backdrop-blur-sm pt-20 px-4 no-print">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveTab(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`w-full flex items-center justify-between px-3.5 py-3 rounded-lg text-sm ${
                      isActive ? 'bg-sky-600 text-white font-semibold' : 'text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className="h-5 w-5" />
                      <span>{item.label}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>
    </div>
  );
};
