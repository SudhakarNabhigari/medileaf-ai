import React, { useState } from 'react';
import { BarChart3, Eye, EyeOff, Info, Leaf, Loader2, Lock, Mail, Network, ShieldCheck, User, UserPlus } from 'lucide-react';
import { motion } from 'motion/react';
import { CornerLeafPattern, LeafScannerGraphic, MediLeafLogo } from './BotanicalArt';
import { SAFETY_DISCLAIMER, UserAccount } from '../types';

interface LoginPageProps {
  onAuthenticated: (user: UserAccount) => void;
}

export function LoginPage({ onAuthenticated }: LoginPageProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [identifier, setIdentifier] = useState('');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [forgotOpen, setForgotOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setForgotOpen(false);

    if (mode === 'register') {
      if (username.trim().length < 3) {
        setError('Username must be at least 3 characters.');
        return;
      }
      if (!email.includes('@') || !email.includes('.')) {
        setError('Please enter a valid email address.');
        return;
      }
      if (password.length < 8) {
        setError('Password must be at least 8 characters.');
        return;
      }
      if (password !== confirmPassword) {
        setError('Passwords do not match.');
        return;
      }
    } else if (!identifier.trim() || !password) {
      setError('Please enter your email/username and password.');
      return;
    }

    setLoading(true);
    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body =
        mode === 'login'
          ? { identifier: identifier.trim(), password }
          : { username: username.trim(), email: email.trim(), password };

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!data.ok || !data.user) {
        setError(data.message || 'Authentication failed.');
        return;
      }
      if (rememberMe) {
        localStorage.setItem('medileaf_user', JSON.stringify(data.user));
      } else {
        sessionStorage.setItem('medileaf_user', JSON.stringify(data.user));
      }
      onAuthenticated(data.user);
    } catch {
      setError('Unable to reach authentication service.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#DFEEE2] via-[#F2F8F3] to-[#CFE5D4] dark:from-[#07130E] dark:to-[#0C2017] flex items-center justify-center p-4 sm:p-8 relative overflow-hidden">
      <CornerLeafPattern className="pointer-events-none absolute -top-4 -right-4 w-52 h-44 opacity-60" />
      <CornerLeafPattern className="pointer-events-none absolute -bottom-6 -left-6 w-56 h-48 rotate-180 opacity-50" />

      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.32, ease: [0.16, 1, 0.3, 1] }}
        className="w-full max-w-6xl bg-white dark:bg-[#11221B] rounded-3xl border border-[#DCE8DF] dark:border-[#1E3B2E] shadow-2xl shadow-[#053821]/15 overflow-hidden grid grid-cols-1 lg:grid-cols-[1.15fr_1fr]"
      >
        {/* Left Emerald Botanical Panel matching Reference Image 7 */}
        <div className="relative bg-gradient-to-br from-[#042E1B] via-[#064327] to-[#0D5A36] p-8 sm:p-10 flex flex-col justify-between text-white">
          <div className="flex items-center gap-3">
            <MediLeafLogo className="w-10 h-10" />
            <div>
              <div className="font-display text-lg font-extrabold tracking-tight">
                MediLeaf <span className="text-[#9AE66E]">AI</span>
              </div>
              <div className="text-[11px] text-emerald-200/80">Medicinal Leaf Identifier</div>
            </div>
          </div>

          <div className="my-6 grid grid-cols-1 sm:grid-cols-[1.15fr_0.9fr] gap-4 items-center">
            <div>
              <h1 className="font-display text-3xl sm:text-4xl font-extrabold leading-tight text-balance">
                Medicinal-Leaf Identifier with a{' '}
                <span className="text-[#9AE66E]">Reject Option</span>
              </h1>
              <div className="w-8 h-1 bg-[#9AE66E] rounded-full my-4" />
              <p className="text-sm text-emerald-50/90 leading-relaxed">
                Fine-tuned PyTorch ResNet50 classification with validation-calibrated confidence
                &amp; energy gating so unfamiliar species return{' '}
                <span className="font-bold text-[#F4B740]">UNCERTAIN</span> instead of forced guesses.
              </p>
            </div>
            <div className="flex justify-center leaf-float">
              <LeafScannerGraphic badgeLabel="Medicinal Leaf Recognition" />
            </div>
          </div>

          {/* 4 Bottom Feature Highlights */}
          <div className="space-y-5">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-white/10 text-center">
              {[
                { icon: Leaf, label: 'Identify Medicinal Leaves' },
                { icon: ShieldCheck, label: 'Reject Unknown (Uncertain)' },
                { icon: Network, label: 'ResNet50 (CNN)' },
                { icon: BarChart3, label: 'Confidence Based Prediction' },
              ].map((feat) => {
                const Icon = feat.icon;
                return (
                  <div key={feat.label} className="flex flex-col items-center gap-1.5">
                    <div className="w-9 h-9 rounded-xl bg-white/10 border border-white/15 flex items-center justify-center text-[#9AE66E]">
                      <Icon className="w-4 h-4" />
                    </div>
                    <span className="text-[11px] text-emerald-50/90 leading-snug">{feat.label}</span>
                  </div>
                );
              })}
            </div>

            <div className="rounded-xl bg-black/20 border border-white/12 p-3 flex items-start gap-2.5 text-[11px] text-emerald-100/85 leading-relaxed">
              <Info className="w-4 h-4 text-[#9AE66E] shrink-0 mt-0.5" />
              <span>{SAFETY_DISCLAIMER}</span>
            </div>
          </div>
        </div>

        {/* Right Form Panel matching Reference Image 7 */}
        <div className="p-7 sm:p-10 flex flex-col justify-center bg-[#FCFDFC] dark:bg-[#11221B]">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center mb-3">
              <MediLeafLogo className="w-12 h-12 shadow-md rounded-2xl" />
            </div>
            <h2 className="font-display text-2xl font-extrabold text-[#053821] dark:text-white tracking-tight">
              MediLeaf <span className="text-[#13823D] dark:text-[#9AE66E]">AI</span>
            </h2>
            <p className="text-xs sm:text-sm text-[#68796F] dark:text-emerald-200/75 mt-1">
              Discover Nature. Identify Leaves. Understand with Confidence.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-1.5 p-1 bg-[#EBF3EC] dark:bg-[#193026] rounded-xl mb-6">
            <button
              type="button"
              onClick={() => {
                setMode('login');
                setError(null);
              }}
              className={`py-2.5 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 whitespace-nowrap ${
                mode === 'login'
                  ? 'bg-gradient-to-r from-[#0E6A30] to-[#168A41] text-white shadow-sm'
                  : 'text-[#18352A] dark:text-emerald-100 hover:bg-white/60 dark:hover:bg-white/5'
              }`}
            >
              <User className="w-4 h-4" />
              <span>Login</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('register');
                setError(null);
              }}
              className={`py-2.5 text-sm font-semibold rounded-lg transition-all flex items-center justify-center gap-2 whitespace-nowrap ${
                mode === 'register'
                  ? 'bg-gradient-to-r from-[#0E6A30] to-[#168A41] text-white shadow-sm'
                  : 'text-[#18352A] dark:text-emerald-100 hover:bg-white/60 dark:hover:bg-white/5'
              }`}
            >
              <UserPlus className="w-4 h-4" />
              <span>Register</span>
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' ? (
              <>
                <div>
                  <label className="block text-xs font-semibold text-[#18352A] dark:text-emerald-100 mb-1.5">
                    Username
                  </label>
                  <div className="relative">
                    <User className="w-4 h-4 text-[#13823D] absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Choose a username"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#D4E2D7] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-sm text-[#18352A] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#13823D]"
                      required
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-[#18352A] dark:text-emerald-100 mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="w-4 h-4 text-[#13823D] absolute left-3.5 top-1/2 -translate-y-1/2" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@university.edu"
                      className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#D4E2D7] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-sm text-[#18352A] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#13823D]"
                      required
                    />
                  </div>
                </div>
              </>
            ) : (
              <div>
                <label className="block text-xs font-semibold text-[#18352A] dark:text-emerald-100 mb-1.5">
                  Email or Username
                </label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-[#13823D] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    placeholder="Enter your email or username"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#D4E2D7] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-sm text-[#18352A] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#13823D]"
                    required
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-[#18352A] dark:text-emerald-100 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-[#13823D] absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="w-full pl-10 pr-11 py-2.5 rounded-xl border border-[#D4E2D7] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-sm text-[#18352A] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#13823D]"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#68796F] hover:text-[#18352A] dark:hover:text-white p-1"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {mode === 'register' && (
              <div>
                <label className="block text-xs font-semibold text-[#18352A] dark:text-emerald-100 mb-1.5">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-[#13823D] absolute left-3.5 top-1/2 -translate-y-1/2" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat password"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-[#D4E2D7] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-sm text-[#18352A] dark:text-white focus:outline-none focus:ring-2 focus:ring-[#13823D]"
                    required
                  />
                </div>
              </div>
            )}

            {mode === 'login' && (
              <div className="flex items-center justify-between text-xs">
                <label className="inline-flex items-center gap-2 text-[#18352A] dark:text-emerald-100 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded border-[#C8D8CC] text-[#13823D] focus:ring-[#13823D]"
                  />
                  Remember me
                </label>
                <button
                  type="button"
                  onClick={() => setForgotOpen((prev) => !prev)}
                  className="text-[#13823D] dark:text-emerald-400 font-semibold hover:underline"
                >
                  Forgot password?
                </button>
              </div>
            )}

            {forgotOpen && (
              <div className="rounded-xl bg-[#F4F8F2] dark:bg-[#172B22] border border-[#DCE8DF] dark:border-[#244435] p-3 text-xs text-[#465B50] dark:text-emerald-100/80">
                Credentials are stored locally in SQLite using PBKDF2-HMAC-SHA256. Switch to{' '}
                <strong>Register</strong> to create a new local account, or change your password in{' '}
                <strong>Settings &amp; Help</strong> once signed in.
              </div>
            )}

            {error && (
              <div
                role="alert"
                className="rounded-xl bg-[#FEF2F2] border border-[#FECACA] px-3.5 py-2.5 text-xs font-medium text-[#B91C1C]"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-full bg-gradient-to-r from-[#0E6A30] to-[#168A41] hover:from-[#0B5627] hover:to-[#127235] text-white font-semibold text-sm shadow-md transition-all flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              <span>{mode === 'login' ? 'Login' : 'Create Account'}</span>
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-[#68796F] dark:text-emerald-200/70 flex items-center justify-center gap-1.5">
            <Leaf className="w-3.5 h-3.5 text-[#13823D]" />
            <span>Local PBKDF2-HMAC-SHA256 authentication · No hardcoded credentials</span>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
