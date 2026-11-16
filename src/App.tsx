import React, { useCallback, useEffect, useState } from 'react';
import { AnalyticsPage } from './components/AnalyticsPage';
import { DashboardPage } from './components/DashboardPage';
import { DatasetPage } from './components/DatasetPage';
import { HistoryPage } from './components/HistoryPage';
import { IdentifyAndResultsPage } from './components/IdentifyAndResultsPage';
import { LoginPage } from './components/LoginPage';
import { SettingsPage } from './components/SettingsPage';
import { ShellLayout } from './components/ShellLayout';
import {
  NavSection,
  PredictionRecord,
  PredictionResult,
  UserAccount,
  UserPreferences,
  WorkspaceState,
} from './types';

function readStoredUser(): UserAccount | null {
  try {
    const raw = localStorage.getItem('medileaf_user') || sessionStorage.getItem('medileaf_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export default function App() {
  const [user, setUser] = useState<UserAccount | null>(() => readStoredUser());
  const [section, setSection] = useState<NavSection>('home');
  const [workspace, setWorkspace] = useState<WorkspaceState | null>(null);
  const [history, setHistory] = useState<PredictionRecord[]>([]);
  const [preferences, setPreferences] = useState<UserPreferences>({
    theme: 'Light',
    notifications_enabled: true,
    save_history_enabled: true,
  });
  const [lastPrediction, setLastPrediction] = useState<PredictionResult | null>(null);
  const [lastImageUrl, setLastImageUrl] = useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    try {
      const res = await fetch('/api/workspace-state');
      if (res.ok) {
        setWorkspace(await res.json());
      }
    } catch {
      // ignore transient network errors on initial load
    }
  }, []);

  const loadUserData = useCallback(async (userId: number) => {
    try {
      const [histRes, prefRes] = await Promise.all([
        fetch(`/api/history/${userId}`),
        fetch(`/api/preferences/${userId}`),
      ]);
      if (histRes.ok) {
        const hd = await histRes.json();
        setHistory(hd.history ?? []);
      }
      if (prefRes.ok) {
        const pd = await prefRes.json();
        if (pd.preferences) setPreferences(pd.preferences);
      }
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  useEffect(() => {
    if (user) {
      loadUserData(user.id);
    }
  }, [user, loadUserData]);

  useEffect(() => {
    const root = document.documentElement;
    if (preferences.theme === 'Dark') {
      root.classList.add('dark');
    } else if (preferences.theme === 'Light') {
      root.classList.remove('dark');
    } else {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    }
  }, [preferences.theme]);

  function handleLogout() {
    localStorage.removeItem('medileaf_user');
    sessionStorage.removeItem('medileaf_user');
    setUser(null);
    setHistory([]);
    setLastPrediction(null);
    setLastImageUrl(null);
    setSection('home');
  }

  async function handleUpdatePreferences(nextPrefs: UserPreferences) {
    setPreferences(nextPrefs);
    if (!user) return;
    await fetch('/api/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: user.id, ...nextPrefs }),
    });
  }

  async function handleClearHistory() {
    if (!user) return;
    await fetch(`/api/history/${user.id}`, { method: 'DELETE' });
    setHistory([]);
  }

  if (!user) {
    return (
      <LoginPage
        onAuthenticated={(u) => {
          setUser(u);
          setSection('home');
        }}
      />
    );
  }

  return (
    <ShellLayout
      activeSection={section}
      onNavigate={(s) => setSection(s)}
      user={user}
      onLogout={handleLogout}
      workspace={workspace}
    >
      {section === 'home' && (
        <DashboardPage
          workspace={workspace}
          history={history}
          onNavigate={(s) => setSection(s)}
        />
      )}

      {(section === 'identify' || section === 'results') && (
        <IdentifyAndResultsPage
          mode={section === 'results' ? 'results' : 'identify'}
          user={user}
          preferences={preferences}
          workspace={workspace}
          lastPrediction={lastPrediction}
          lastImageUrl={lastImageUrl}
          onPredictionComplete={(res, imgUrl) => {
            setLastPrediction(res);
            setLastImageUrl(imgUrl);
            setSection('results');
            loadUserData(user.id);
          }}
          onBackToIdentify={() => setSection('identify')}
        />
      )}

      {section === 'history' && (
        <HistoryPage
          history={history}
          onClearHistory={handleClearHistory}
          onNavigate={(s) => setSection(s)}
        />
      )}

      {section === 'analytics' && <AnalyticsPage workspace={workspace} />}

      {section === 'dataset' && (
        <DatasetPage workspace={workspace} onDatasetInspected={loadWorkspace} />
      )}

      {section === 'settings' && (
        <SettingsPage
          user={user}
          preferences={preferences}
          onUpdatePreferences={handleUpdatePreferences}
          onLogout={handleLogout}
        />
      )}
    </ShellLayout>
  );
}
