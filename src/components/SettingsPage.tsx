import React, { useState } from 'react';
import {
  Bell,
  Check,
  ChevronDown,
  ChevronRight,
  Database,
  GraduationCap,
  HelpCircle,
  History,
  Image as ImageIcon,
  Info,
  Leaf,
  Lock,
  LogOut,
  Monitor,
  Moon,
  Palette,
  Settings,
  ShieldCheck,
  Sun,
  User,
} from 'lucide-react';
import { motion } from 'motion/react';
import { SAFETY_DISCLAIMER, UserAccount, UserPreferences } from '../types';

interface SettingsPageProps {
  user: UserAccount;
  preferences: UserPreferences;
  onUpdatePreferences: (prefs: UserPreferences) => Promise<void>;
  onLogout: () => void;
}

const HELP_TOPICS = [
  {
    id: 'better',
    icon: Leaf,
    title: 'How to get better results?',
    subtitle: 'Use a sharp, evenly lit photograph showing a single medicinal plant leaf centered in the frame.',
    body: 'Avoid heavy shadows, motion blur, or cluttered multi-species branches. Focus cleanly on one representative leaf so ResNet50 captures venation and margin details.',
  },
  {
    id: 'formats',
    icon: ImageIcon,
    title: 'Supported image formats',
    subtitle: 'JPG, JPEG, PNG | Max size: 10 MB',
    body: 'Images are verified via OpenCV and Pillow, EXIF-transposed to upright RGB, resized to 256 px shorter side, center-cropped to 224×224, and normalized with ImageNet statistics.',
  },
  {
    id: 'uncertain',
    icon: ShieldCheck,
    title: 'Understanding "UNCERTAIN"',
    subtitle: 'Returned for unfamiliar (out-of-distribution) or low-reliability inputs.',
    body: 'When maximum softmax confidence falls below the validation-calibrated threshold or the Energy OOD score exceeds the in-distribution boundary, MEDILEAF.AI abstains rather than guessing.',
  },
  {
    id: 'dataset',
    icon: Database,
    title: 'Dataset and model information',
    subtitle: 'Details about the Indian Medicinal Leaves Dataset and ResNet50 model.',
    body: 'PyTorch ResNet50 (IMAGENET1K_V2 weights) fine-tuned in two stages on known species from Indian Medicinal Leaves Image Datasets v3 (Mendeley DOI: 10.17632/748f8jkphb.3) with held-out species isolated for OOD evaluation.',
  },
  {
    id: 'disclaimer',
    icon: GraduationCap,
    title: 'Safety & academic disclaimer',
    subtitle: 'Academic project only. Not a medical or plant-safety authority.',
    body: SAFETY_DISCLAIMER,
  },
];

export function SettingsPage({
  user,
  preferences,
  onUpdatePreferences,
  onLogout,
}: SettingsPageProps) {
  const [activeTab, setActiveTab] = useState<'settings' | 'help'>('settings');
  const [openTopic, setOpenTopic] = useState<string>('');
  const [showChangePw, setShowChangePw] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [pwMessage, setPwMessage] = useState<{ ok: boolean; text: string } | null>(null);

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwMessage(null);
    const res = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: user.id,
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
    const data = await res.json();
    setPwMessage({ ok: Boolean(data.ok), text: data.message });
    if (data.ok) {
      setCurrentPassword('');
      setNewPassword('');
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-5 relative z-10"
    >
      {/* Pill Tabs matching Reference Image 6 */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={() => setActiveTab('settings')}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === 'settings'
              ? 'bg-[#0B662B] text-white shadow-sm'
              : 'bg-white dark:bg-[#11221B] text-[#18352A] dark:text-emerald-100 border border-[#DCE8DF] dark:border-[#1E3B2E]'
          }`}
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('help')}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            activeTab === 'help'
              ? 'bg-[#0B662B] text-white shadow-sm'
              : 'bg-white dark:bg-[#11221B] text-[#18352A] dark:text-emerald-100 border border-[#DCE8DF] dark:border-[#1E3B2E]'
          }`}
        >
          <HelpCircle className="w-4 h-4" />
          <span>Help &amp; Support</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {activeTab === 'settings' && (
          <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 space-y-6">
            <div className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center">
                <Settings className="w-5 h-5" />
              </span>
              <div>
                <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
                  Application Settings
                </h3>
                <p className="text-xs text-[#68796F]">Customize your MediLeaf AI experience</p>
              </div>
            </div>

            {/* 3-Card App Theme Selector matching Reference Image 6 */}
            <div className="space-y-3 pt-2 border-t border-[#EEF4EF] dark:border-[#1E3B2E]">
              <div className="flex items-center gap-2.5">
                <span className="w-8 h-8 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center">
                  <Palette className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-sm font-bold text-[#18352A] dark:text-white">App Theme</div>
                  <div className="text-xs text-[#68796F]">Choose your preferred appearance</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3 pl-0 sm:pl-10">
                {(
                  [
                    { id: 'Light', icon: Sun },
                    { id: 'Dark', icon: Moon },
                    { id: 'System', icon: Monitor },
                  ] as const
                ).map((item) => {
                  const Icon = item.icon;
                  const active = preferences.theme === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => onUpdatePreferences({ ...preferences, theme: item.id })}
                      className={`relative rounded-xl border p-3.5 flex flex-col items-center gap-1.5 text-xs font-semibold transition-all ${
                        active
                          ? 'border-[#13823D] bg-[#F2FAF3] dark:bg-[#183528] text-[#053821] dark:text-white ring-1 ring-[#13823D]'
                          : 'border-[#DCE8DF] dark:border-[#244435] text-[#68796F] hover:border-[#13823D]'
                      }`}
                    >
                      {active && (
                        <span className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-[#13823D] text-white flex items-center justify-center">
                          <Check className="w-3 h-3" />
                        </span>
                      )}
                      <Icon className="w-4 h-4" />
                      <span>{item.id}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Toggles */}
            <div className="space-y-4 pt-4 border-t border-[#EEF4EF] dark:border-[#1E3B2E]">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center shrink-0">
                    <Bell className="w-4 h-4" />
                  </span>
                  <div>
                    <div className="text-sm font-bold text-[#18352A] dark:text-white">
                      Notifications
                    </div>
                    <div className="text-xs text-[#68796F]">
                      Get alerts for model status and updates
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={preferences.notifications_enabled}
                  onClick={() =>
                    onUpdatePreferences({
                      ...preferences,
                      notifications_enabled: !preferences.notifications_enabled,
                    })
                  }
                  className={`w-12 h-6 rounded-full transition-colors p-0.5 shrink-0 ${
                    preferences.notifications_enabled ? 'bg-[#0B662B]' : 'bg-[#CBD5E1]'
                  }`}
                >
                  <span
                    className={`block w-5 h-5 rounded-full bg-white transition-transform ${
                      preferences.notifications_enabled ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center shrink-0">
                    <History className="w-4 h-4" />
                  </span>
                  <div>
                    <div className="text-sm font-bold text-[#18352A] dark:text-white">
                      Save Prediction History
                    </div>
                    <div className="text-xs text-[#68796F]">
                      Automatically store your leaf identification results
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={preferences.save_history_enabled}
                  onClick={() =>
                    onUpdatePreferences({
                      ...preferences,
                      save_history_enabled: !preferences.save_history_enabled,
                    })
                  }
                  className={`w-12 h-6 rounded-full transition-colors p-0.5 shrink-0 ${
                    preferences.save_history_enabled ? 'bg-[#0B662B]' : 'bg-[#CBD5E1]'
                  }`}
                >
                  <span
                    className={`block w-5 h-5 rounded-full bg-white transition-transform ${
                      preferences.save_history_enabled ? 'translate-x-6' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            </div>

            {/* Account Section */}
            <div className="space-y-3 pt-4 border-t border-[#EEF4EF] dark:border-[#1E3B2E]">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center">
                  <User className="w-4 h-4" />
                </span>
                <div>
                  <div className="text-sm font-bold text-[#18352A] dark:text-white">Account</div>
                  <div className="text-xs text-[#68796F]">Manage your account settings</div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setShowChangePw((p) => !p)}
                className="w-full py-2.5 px-4 rounded-xl bg-[#F2FAF3] dark:bg-[#173023] border border-[#CDE6D2] dark:border-[#244435] text-sm font-semibold text-[#053821] dark:text-emerald-200 flex items-center justify-center gap-2 hover:bg-[#E7F5E9] transition-colors"
              >
                <Lock className="w-4 h-4" />
                <span>Change Password</span>
              </button>

              {showChangePw && (
                <form onSubmit={handleChangePassword} className="space-y-2.5 pt-1">
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Current password"
                    required
                    className="w-full px-3.5 py-2 rounded-xl border border-[#DCE8DF] dark:border-[#244435] bg-transparent text-sm"
                  />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New password (min 8 chars)"
                    required
                    className="w-full px-3.5 py-2 rounded-xl border border-[#DCE8DF] dark:border-[#244435] bg-transparent text-sm"
                  />
                  {pwMessage && (
                    <div
                      className={`text-xs font-medium ${
                        pwMessage.ok ? 'text-[#13823D]' : 'text-[#E53935]'
                      }`}
                    >
                      {pwMessage.text}
                    </div>
                  )}
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl bg-[#13823D] text-white text-xs font-semibold"
                  >
                    Update Password
                  </button>
                </form>
              )}

              <button
                type="button"
                onClick={onLogout}
                className="w-full py-2.5 px-4 rounded-xl bg-[#FFF5F5] dark:bg-[#291517] border border-[#FECACA] dark:border-[#522427] text-[#E53935] text-sm font-semibold flex items-center justify-center gap-2 hover:bg-[#FEE2E2] transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        )}

        {/* Right Need Help? Card matching Reference Image 6 */}
        <div
          className={`bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 space-y-4 ${
            activeTab === 'help' ? 'lg:col-span-2 max-w-3xl' : ''
          }`}
        >
          <div className="flex items-center gap-3">
            <span className="w-10 h-10 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center">
              <HelpCircle className="w-5 h-5" />
            </span>
            <div>
              <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
                Need Help?
              </h3>
              <p className="text-xs text-[#68796F]">Find answers and learn how to use MediLeaf AI</p>
            </div>
          </div>

          <div className="space-y-2.5">
            {HELP_TOPICS.map((topic) => {
              const Icon = topic.icon;
              const isOpen = openTopic === topic.id;
              return (
                <div
                  key={topic.id}
                  className="rounded-xl border border-[#E6EFE8] dark:border-[#1E3B2E] bg-[#FAFDF9] dark:bg-[#0E1D17] overflow-hidden"
                >
                  <button
                    type="button"
                    onClick={() => setOpenTopic(isOpen ? '' : topic.id)}
                    className="w-full flex items-center justify-between gap-3 p-3.5 text-left"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="w-8 h-8 rounded-full bg-[#E8F5E9] text-[#13823D] flex items-center justify-center shrink-0">
                        <Icon className="w-4 h-4" />
                      </span>
                      <div className="min-w-0">
                        <div className="text-xs sm:text-sm font-bold text-[#18352A] dark:text-white">
                          {topic.title}
                        </div>
                        <div className="text-[11px] text-[#68796F] truncate">{topic.subtitle}</div>
                      </div>
                    </div>
                    {isOpen ? (
                      <ChevronDown className="w-4 h-4 text-[#13823D] shrink-0" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-[#68796F] shrink-0" />
                    )}
                  </button>
                  {isOpen && (
                    <div className="px-4 pb-3.5 pt-1 text-xs text-[#465B50] dark:text-emerald-100/80 leading-relaxed border-t border-[#E6EFE8] dark:border-[#1E3B2E]">
                      {topic.body}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="rounded-xl bg-[#F2FAF3] dark:bg-[#152920] border border-[#DCE8DF] dark:border-[#244435] px-4 py-3 flex items-center gap-2.5 text-xs text-[#18352A] dark:text-emerald-100">
            <Info className="w-4 h-4 text-[#13823D] shrink-0" />
            <span>
              <strong>Academic Computer Vision Project (CA-1)</strong> — Python · PyTorch ResNet50 ·
              Streamlit
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
