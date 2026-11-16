import React, { useState } from 'react';
import {
  BarChart3,
  Bell,
  ChevronDown,
  History,
  Home,
  Layers,
  Leaf,
  LogOut,
  Menu,
  ScanLine,
  Settings,
  User,
  X,
} from 'lucide-react';
import { CornerLeafPattern, MediLeafLogo } from './BotanicalArt';
import { NavSection, UserAccount, WorkspaceState } from '../types';

interface ShellLayoutProps {
  activeSection: NavSection;
  onNavigate: (section: NavSection) => void;
  user: UserAccount;
  onLogout: () => void;
  workspace: WorkspaceState | null;
  children: React.ReactNode;
}

const NAV_ITEMS: Array<{ id: NavSection; label: string; icon: React.ComponentType<{ className?: string }> }> = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'identify', label: 'Leaf Identification', icon: ScanLine },
  { id: 'history', label: 'Prediction History', icon: History },
  { id: 'analytics', label: 'Model Analytics', icon: BarChart3 },
  { id: 'dataset', label: 'Dataset & Information', icon: Layers },
  { id: 'settings', label: 'Settings & Help', icon: Settings },
];

const HEADER_META: Record<NavSection, { title: string; subtitle?: string }> = {
  home: { title: 'Dashboard' },
  identify: { title: 'Leaf Identification' },
  results: { title: 'Prediction Results' },
  history: {
    title: 'Prediction History',
    subtitle: 'View and manage your past leaf identification results',
  },
  analytics: {
    title: 'Model Analytics',
    subtitle: 'Comprehensive evaluation of the leaf identification model',
  },
  dataset: {
    title: 'Dataset & Information',
    subtitle: 'Explore the dataset details, class distribution and project information',
  },
  settings: {
    title: 'Settings & Help',
    subtitle: 'Configure your preferences and get support',
  },
};

export function ShellLayout({
  activeSection,
  onNavigate,
  user,
  onLogout,
  workspace,
  children,
}: ShellLayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);

  const effectiveNav: NavSection = activeSection === 'results' ? 'identify' : activeSection;
  const headerInfo = HEADER_META[activeSection];

  return (
    <div className="min-h-screen flex bg-[#F6FAF5] dark:bg-[#0B1712] text-[#18352A] dark:text-emerald-50">
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/45 md:hidden"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Permanently Visible Fixed Forest Green Sidebar on Desktop/Tablet (md+) */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 shrink-0 bg-gradient-to-b from-[#053821] via-[#04301C] to-[#032515] text-white flex flex-col justify-between transition-transform duration-200 md:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div>
          <div className="px-5 pt-6 pb-5 text-center relative">
            <button
              type="button"
              onClick={() => setMobileOpen(false)}
              className="md:hidden absolute right-3 top-4 p-1.5 rounded-lg text-emerald-100 hover:bg-white/10"
              aria-label="Close navigation"
            >
              <X className="w-5 h-5" />
            </button>
            <button
              type="button"
              onClick={() => {
                onNavigate('home');
                setMobileOpen(false);
              }}
              className="inline-flex flex-col items-center gap-1.5"
            >
              <MediLeafLogo className="w-11 h-11" />
              <span className="font-display text-xl font-extrabold tracking-tight text-white">
                MediLeaf <span className="text-[#9AE66E]">AI</span>
              </span>
              <span className="text-[11px] text-emerald-200/75">Medicinal Leaf Identifier</span>
            </button>
          </div>

          <nav className="px-3.5 space-y-1.5" aria-label="Main navigation">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = effectiveNav === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onNavigate(item.id);
                    setMobileOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-gradient-to-r from-[#9AE66E] to-[#7ED957] text-[#053821] font-bold shadow-md'
                      : 'text-emerald-100/85 hover:bg-white/10 hover:text-white font-medium'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[#053821]' : 'text-emerald-200/80'}`} />
                  <span>{item.id === 'home' && activeSection === 'home' ? 'Dashboard' : item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-white/10">
          <button
            type="button"
            onClick={onLogout}
            className="w-full flex items-center justify-center gap-2.5 px-3.5 py-2.5 rounded-xl border border-white/25 text-sm font-medium text-white hover:bg-white/10 transition-colors whitespace-nowrap"
          >
            <LogOut className="w-4 h-4 shrink-0" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content shifted cleanly to the right of fixed 256px (md:ml-64) sidebar */}
      <div className="flex-1 md:ml-64 flex flex-col min-w-0 relative">
        <header className="min-h-16 py-2.5 bg-white/95 dark:bg-[#102019]/95 backdrop-blur border-b border-[#E2ECE4] dark:border-[#1E3B2E] px-4 sm:px-8 flex items-center justify-between sticky top-0 z-30">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              className="md:hidden p-2 rounded-lg text-[#18352A] dark:text-emerald-100 hover:bg-[#E8F5E9] dark:hover:bg-white/10"
              aria-label="Open navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <Leaf className="w-5 h-5 text-[#13823D] dark:text-emerald-400 shrink-0" />
            <div className="min-w-0">
              <h1 className="font-display text-lg sm:text-xl font-bold text-[#18352A] dark:text-white truncate">
                {headerInfo.title}
              </h1>
              {headerInfo.subtitle && (
                <p className="text-xs text-[#68796F] dark:text-emerald-200/70 truncate">
                  {headerInfo.subtitle}
                </p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 relative">
            <button
              type="button"
              onClick={() => {
                setNotifOpen((p) => !p);
                setProfileOpen(false);
              }}
              aria-label="System status notifications"
              className="p-2.5 rounded-xl text-[#18352A] dark:text-emerald-100 hover:bg-[#E8F5E9] dark:hover:bg-white/10 transition-colors"
            >
              <Bell className="w-5 h-5" />
            </button>

            <button
              type="button"
              onClick={() => {
                setProfileOpen((p) => !p);
                setNotifOpen(false);
              }}
              aria-label="User account menu"
              className="py-1.5 px-3 rounded-full bg-[#E8F5E9] dark:bg-[#1A3529] text-[#053821] dark:text-emerald-100 hover:bg-[#D5EDD8] transition-colors flex items-center gap-2"
            >
              <span className="w-6 h-6 rounded-full bg-[#13823D] text-white flex items-center justify-center">
                <User className="w-3.5 h-3.5" />
              </span>
              <span className="hidden sm:inline text-xs font-semibold whitespace-nowrap">
                {user.username}
              </span>
              <ChevronDown className="w-3.5 h-3.5 hidden sm:inline" />
            </button>

            {notifOpen && (
              <div className="absolute right-0 top-12 w-80 bg-white dark:bg-[#11221B] border border-[#DCE8DF] dark:border-[#1E3B2E] rounded-2xl shadow-lg p-4 z-50 text-xs space-y-2.5">
                <div className="font-display font-bold text-sm text-[#053821] dark:text-emerald-300">
                  Pipeline Readiness
                </div>
                <div className="text-[#465B50] dark:text-emerald-100/80">
                  <strong>Dataset Inventory:</strong>{' '}
                  {workspace?.datasetMeta?.valid_image_count
                    ? `${workspace.datasetMeta.valid_image_count.toLocaleString()} verified images`
                    : 'Not loaded yet (run scripts/inspect_dataset.py)'}
                </div>
                <div className="text-[#465B50] dark:text-emerald-100/80">
                  <strong>ResNet50 Checkpoint:</strong>{' '}
                  {workspace?.modelReady
                    ? 'Ready (best_model.pth loaded)'
                    : 'Training Pending (Colab GPU / src/train.py)'}
                </div>
              </div>
            )}

            {profileOpen && (
              <div className="absolute right-0 top-12 w-64 bg-white dark:bg-[#11221B] border border-[#DCE8DF] dark:border-[#1E3B2E] rounded-2xl shadow-lg p-4 z-50 text-xs space-y-3">
                <div>
                  <div className="font-bold text-sm text-[#18352A] dark:text-white">
                    {user.username}
                  </div>
                  <div className="text-[#68796F] dark:text-emerald-200/70 truncate">{user.email}</div>
                </div>
                <div className="flex flex-col gap-1.5 pt-2 border-t border-[#E6EFE8] dark:border-[#1E3B2E]">
                  <button
                    type="button"
                    onClick={() => {
                      setProfileOpen(false);
                      onNavigate('settings');
                    }}
                    className="text-left px-2.5 py-1.5 rounded-lg hover:bg-[#F4F8F2] dark:hover:bg-white/5 font-medium"
                  >
                    Account Settings
                  </button>
                  <button
                    type="button"
                    onClick={onLogout}
                    className="text-left px-2.5 py-1.5 rounded-lg hover:bg-[#FEF2F2] text-[#E53935] font-medium"
                  >
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 p-4 sm:p-7 max-w-7xl w-full mx-auto relative">
          {children}
          <CornerLeafPattern className="pointer-events-none fixed bottom-0 right-0 w-40 h-32 opacity-35 z-0" />
        </main>
      </div>
    </div>
  );
}
