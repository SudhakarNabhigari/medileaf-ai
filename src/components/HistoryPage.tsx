import React, { useMemo, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Calendar,
  CheckCircle2,
  FileClock,
  HelpCircle,
  Leaf,
  Search,
  Trash2,
} from 'lucide-react';
import { motion } from 'motion/react';
import { NavSection, PredictionRecord } from '../types';

interface HistoryPageProps {
  history: PredictionRecord[];
  onClearHistory: () => Promise<void>;
  onNavigate?: (section: NavSection) => void;
}

const PAGE_SIZE = 8;

export function HistoryPage({ history, onClearHistory, onNavigate }: HistoryPageProps) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [statusFilter, setStatusFilter] = useState<'all' | 'Accepted' | 'Rejected'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);

  const acceptedCount = useMemo(
    () => history.filter((h) => h.status === 'Accepted').length,
    [history],
  );
  const rejectedCount = useMemo(
    () => history.filter((h) => h.status === 'Rejected').length,
    [history],
  );
  const lastPredictionTime = history.length > 0 ? history[0].created_at : '--';

  const filtered = useMemo(() => {
    return history.filter((rec) => {
      const matchesStatus = statusFilter === 'all' || rec.status === statusFilter;
      const matchesSearch =
        !searchQuery.trim() ||
        rec.predicted_species.toLowerCase().includes(searchQuery.trim().toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [history, statusFilter, searchQuery]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const paged = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  async function handleConfirmClear() {
    setClearing(true);
    try {
      await onClearHistory();
      setConfirmOpen(false);
      setPage(1);
    } finally {
      setClearing(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-5 relative z-10"
    >
      {/* Top Emerald Banner matching Reference Image 3 */}
      <div className="rounded-2xl bg-gradient-to-r from-[#053821] via-[#0A5331] to-[#116E40] p-6 sm:p-7 text-white shadow-lg flex items-center gap-5">
        <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center shrink-0">
          <FileClock className="w-7 h-7 text-[#9AE66E]" />
        </div>
        <div>
          <h2 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight">
            Your <span className="text-[#9AE66E]">Prediction History</span>
          </h2>
          <p className="text-xs sm:text-sm text-emerald-50/90 mt-1">
            All your leaf identification attempts are stored here with predicted species, confidence
            scores and results.
          </p>
        </div>
      </div>

      {/* 4 Summary KPI Cards matching Reference Image 3 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#F4FAF4] dark:bg-[#11221B] rounded-2xl border border-[#DCEEE0] dark:border-[#1E3B2E] p-4 flex items-center gap-3">
          <span className="w-10 h-10 rounded-full bg-[#DCFCE7] text-[#13823D] flex items-center justify-center shrink-0">
            <Leaf className="w-5 h-5" />
          </span>
          <div>
            <div className="text-xs text-[#68796F]">Total Predictions</div>
            <div className="font-mono-num text-2xl font-extrabold text-[#18352A] dark:text-white">
              {history.length}
            </div>
          </div>
        </div>

        <div className="bg-[#F1FAF5] dark:bg-[#11221B] rounded-2xl border border-[#C9EBD8] dark:border-[#1E3B2E] p-4 flex items-center gap-3">
          <span className="w-10 h-10 rounded-full bg-[#D1FAE5] text-[#13823D] flex items-center justify-center shrink-0">
            <CheckCircle2 className="w-5 h-5" />
          </span>
          <div>
            <div className="text-xs text-[#68796F]">Known (Accepted)</div>
            <div className="font-mono-num text-2xl font-extrabold text-[#18352A] dark:text-white">
              {acceptedCount}
            </div>
          </div>
        </div>

        <div className="bg-[#FFF9F0] dark:bg-[#1E1A12] rounded-2xl border border-[#FBE3BA] dark:border-[#4D3B1E] p-4 flex items-center gap-3">
          <span className="w-10 h-10 rounded-full bg-[#FEF3C7] text-[#D97706] flex items-center justify-center shrink-0">
            <HelpCircle className="w-5 h-5" />
          </span>
          <div>
            <div className="text-xs text-[#68796F]">Uncertain (Rejected)</div>
            <div className="font-mono-num text-2xl font-extrabold text-[#18352A] dark:text-white">
              {rejectedCount}
            </div>
          </div>
        </div>

        <div className="bg-[#F5F5FF] dark:bg-[#161829] rounded-2xl border border-[#DFDFFC] dark:border-[#2C2F4E] p-4 flex items-center gap-3">
          <span className="w-10 h-10 rounded-full bg-[#E0E7FF] text-[#4338CA] flex items-center justify-center shrink-0">
            <Calendar className="w-5 h-5" />
          </span>
          <div className="min-w-0">
            <div className="text-xs text-[#68796F]">Last Prediction</div>
            <div className="font-mono-num text-sm font-bold text-[#18352A] dark:text-white truncate">
              {lastPredictionTime}
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Records Card */}
      <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 space-y-5 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
            Prediction Records
          </h3>
          <div className="flex flex-wrap items-center gap-2.5">
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value as 'all' | 'Accepted' | 'Rejected');
                setPage(1);
              }}
              aria-label="Filter by result status"
              className="px-3 py-1.5 rounded-xl border border-[#DCE8DF] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-xs font-medium"
            >
              <option value="all">All Results</option>
              <option value="Accepted">Accepted</option>
              <option value="Rejected">Uncertain (Rejected)</option>
            </select>

            <div className="relative">
              <Search className="w-3.5 h-3.5 text-[#68796F] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                placeholder="Search by species..."
                className="pl-8 pr-3 py-1.5 rounded-xl border border-[#DCE8DF] dark:border-[#244435] bg-white dark:bg-[#0D1B15] text-xs w-44"
              />
            </div>

            {history.length > 0 && (
              <button
                type="button"
                onClick={() => setConfirmOpen(true)}
                className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#E53935] hover:bg-[#C62828] text-white text-xs font-semibold transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear History</span>
              </button>
            )}
          </div>
        </div>

        {confirmOpen && (
          <div className="rounded-xl bg-[#FFF8EB] border border-[#F6D897] p-4 flex flex-wrap items-center justify-between gap-4">
            <span className="text-xs font-medium text-[#78350F]">
              Permanently delete all saved prediction history records?
            </span>
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={clearing}
                onClick={handleConfirmClear}
                className="px-3.5 py-1.5 rounded-lg bg-[#E53935] text-white text-xs font-semibold"
              >
                {clearing ? 'Clearing...' : 'Confirm Clear'}
              </button>
              <button
                type="button"
                onClick={() => setConfirmOpen(false)}
                className="px-3.5 py-1.5 rounded-lg bg-white border border-[#DCE8DF] text-xs font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {filtered.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-[#C7E0CC] dark:border-[#244435] bg-[#F7FCF7] dark:bg-[#0D1B15] py-14 px-6 text-center space-y-3">
            <div className="w-16 h-14 rounded-2xl bg-white dark:bg-[#11221B] border border-[#DCECE0] mx-auto flex items-center justify-center shadow-xs">
              <Leaf className="w-7 h-7 text-[#13823D]" />
            </div>
            <div className="font-display text-lg font-bold text-[#18352A] dark:text-white">
              {history.length === 0 ? 'No predictions yet' : 'No matching records'}
            </div>
            <p className="text-xs sm:text-sm text-[#68796F] dark:text-emerald-200/70 max-w-md mx-auto">
              Upload a leaf on the Leaf Identification page after model training to record real
              predictions and confidence scores here.
            </p>
            {onNavigate && (
              <div className="pt-2">
                <button
                  type="button"
                  onClick={() => onNavigate('identify')}
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-[#0E6A30] to-[#168A41] text-white text-xs font-semibold shadow-sm"
                >
                  <Leaf className="w-3.5 h-3.5" />
                  <span>Identify a Leaf</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-[#E6EFE8] dark:border-[#1E3B2E] text-xs font-semibold text-[#68796F]">
                  <th className="py-3 px-3">#</th>
                  <th className="py-3 px-3">Image</th>
                  <th className="py-3 px-3">Predicted Species</th>
                  <th className="py-3 px-3">Confidence</th>
                  <th className="py-3 px-3">Status</th>
                  <th className="py-3 px-3">Date &amp; Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#EEF4EF] dark:divide-[#1E3B2E]">
                {paged.map((rec, i) => (
                  <tr key={rec.id}>
                    <td className="py-3 px-3 font-mono-num text-xs text-[#68796F]">
                      {(page - 1) * PAGE_SIZE + i + 1}
                    </td>
                    <td className="py-3 px-3">
                      {rec.image_thumbnail_b64 ? (
                        <img
                          src={`data:image/jpeg;base64,${rec.image_thumbnail_b64}`}
                          alt={rec.filename}
                          className="w-11 h-11 rounded-lg object-cover border border-[#DCE8DF]"
                        />
                      ) : (
                        <div className="w-11 h-11 rounded-lg bg-[#E8F5E9] flex items-center justify-center">
                          <Leaf className="w-5 h-5 text-[#13823D]" />
                        </div>
                      )}
                    </td>
                    <td className="py-3 px-3 font-semibold text-[#18352A] dark:text-white">
                      {rec.predicted_species}
                    </td>
                    <td className="py-3 px-3 font-mono-num">
                      {rec.confidence !== null ? `${(rec.confidence * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-3">
                      {rec.status === 'Accepted' ? (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-[#13823D]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Accepted
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-[#B45309]">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          Rejected
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3 text-xs text-[#68796F] whitespace-nowrap">
                      {rec.created_at}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2 text-xs">
          <button
            type="button"
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-3 py-1.5 rounded-lg border border-[#DCE8DF] bg-white disabled:opacity-40"
          >
            Previous
          </button>
          <span className="font-mono-num">
            Page {page} of {totalPages}
          </span>
          <button
            type="button"
            disabled={page === totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="px-3 py-1.5 rounded-lg border border-[#DCE8DF] bg-white disabled:opacity-40"
          >
            Next
          </button>
        </div>
      )}
    </motion.div>
  );
}
