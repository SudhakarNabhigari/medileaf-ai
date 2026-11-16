import React from 'react';
import {
  Activity,
  BarChart3,
  CheckCircle2,
  Cpu,
  Database,
  Grid3X3,
  Info,
  Layers,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Target,
  TrendingUp,
} from 'lucide-react';
import { motion } from 'motion/react';
import { WorkspaceState } from '../types';

interface AnalyticsPageProps {
  workspace: WorkspaceState | null;
}

export function AnalyticsPage({ workspace }: AnalyticsPageProps) {
  const ev = workspace?.evaluationSummary;
  const hist = workspace?.trainingHistory ?? [];

  const metricCards = [
    {
      label: 'Accuracy',
      val: ev?.closed_set_accuracy !== undefined ? `${(ev.closed_set_accuracy * 100).toFixed(2)}%` : 'Pending',
      bg: 'bg-[#F2FAF3] dark:bg-[#11221B] border-[#CBE8CF] dark:border-[#1E3B2E]',
      iconBg: 'bg-[#DCFCE7] text-[#13823D]',
      text: 'text-[#13823D]',
      icon: Target,
    },
    {
      label: 'Precision',
      val: ev?.macro_precision !== undefined ? ev.macro_precision.toFixed(2) : 'Pending',
      bg: 'bg-[#F2FAF3] dark:bg-[#11221B] border-[#CBE8CF] dark:border-[#1E3B2E]',
      iconBg: 'bg-[#DCFCE7] text-[#13823D]',
      text: 'text-[#13823D]',
      icon: Layers,
    },
    {
      label: 'Recall',
      val: ev?.macro_recall !== undefined ? ev.macro_recall.toFixed(2) : 'Pending',
      bg: 'bg-[#FFF9F0] dark:bg-[#231B12] border-[#FBE3BA] dark:border-[#4D3B1E]',
      iconBg: 'bg-[#FEF3C7] text-[#D97706]',
      text: 'text-[#C2410C] dark:text-[#F4B740]',
      icon: RefreshCw,
    },
    {
      label: 'F1-Score',
      val: ev?.macro_f1 !== undefined ? ev.macro_f1.toFixed(2) : 'Pending',
      bg: 'bg-[#F0F9FF] dark:bg-[#121E29] border-[#CBE5FA] dark:border-[#243B52]',
      iconBg: 'bg-[#E0F2FE] text-[#0369A1]',
      text: 'text-[#075985] dark:text-sky-300',
      icon: Activity,
    },
    {
      label: 'Coverage',
      val: ev?.known_coverage !== undefined ? ev.known_coverage.toFixed(2) : 'Pending',
      bg: 'bg-[#F6F4FF] dark:bg-[#19162B] border-[#DFD8FC] dark:border-[#2F2A54]',
      iconBg: 'bg-[#EDE9FE] text-[#5B21B6]',
      text: 'text-[#4C1D95] dark:text-violet-300',
      icon: Database,
    },
    {
      label: 'Rejection Rate',
      val: ev?.known_rejection_rate !== undefined ? ev.known_rejection_rate.toFixed(2) : 'Pending',
      bg: 'bg-[#FFF5F5] dark:bg-[#291517] border-[#FBD3D4] dark:border-[#522427]',
      iconBg: 'bg-[#FEE2E2] text-[#DC2626]',
      text: 'text-[#DC2626] dark:text-rose-300',
      icon: ShieldAlert,
    },
  ];

  const svgPoints = (() => {
    if (hist.length === 0) return null;
    const width = 340;
    const height = 160;
    const n = hist.length;
    const toPt = (idx: number, accStr: string) => {
      const x = n === 1 ? width / 2 : 20 + (idx / (n - 1)) * (width - 40);
      const yVal = Math.min(1, Math.max(0, parseFloat(accStr) || 0));
      const y = height - 20 - yVal * (height - 40);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    };
    return {
      train: hist.map((r, i) => toPt(i, r.train_acc)).join(' '),
      val: hist.map((r, i) => toPt(i, r.val_acc)).join(' '),
    };
  })();

  const oodRows = [
    {
      label: 'OOD AUROC (MSP)',
      hint: 'Separability of known vs held-out species using Max Softmax Probability.',
      val: ev?.msp_ood_auroc !== undefined ? ev.msp_ood_auroc.toFixed(3) : 'Pending',
    },
    {
      label: 'OOD AUPR (MSP)',
      hint: 'Area under Precision-Recall curve for MSP OOD separation.',
      val: ev?.msp_ood_aupr !== undefined ? ev.msp_ood_aupr.toFixed(3) : 'Pending',
    },
    {
      label: 'OOD AUROC (Energy)',
      hint: 'Separability using free-energy score -T * logsumexp(logits / T).',
      val: ev?.energy_ood_auroc !== undefined ? ev.energy_ood_auroc.toFixed(3) : 'Pending',
    },
    {
      label: 'Selective Accuracy',
      hint: 'Accuracy strictly among accepted known-species predictions.',
      val: ev?.selective_accuracy !== undefined ? ev.selective_accuracy.toFixed(3) : 'Pending',
    },
    {
      label: 'OOD Rejection Rate',
      hint: 'Fraction of held-out unseen species correctly abstained as UNCERTAIN.',
      val: ev?.ood_rejection_rate !== undefined ? ev.ood_rejection_rate.toFixed(3) : 'Pending',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-5 relative z-10"
    >
      {/* Top Emerald Banner matching Reference Image 4 */}
      <div className="rounded-2xl bg-gradient-to-r from-[#053821] via-[#0A5331] to-[#116E40] p-6 sm:p-7 text-white shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center shrink-0">
            <Cpu className="w-7 h-7 text-[#9AE66E]" />
          </div>
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight">
              Model Performance <span className="text-[#9AE66E]">Analytics</span>
            </h2>
            <p className="text-xs sm:text-sm text-emerald-50/90 mt-1">
              Evaluation results, learning curves, confusion matrix and OOD detection performance
              for MediLeaf AI.
            </p>
          </div>
        </div>
        <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-xl bg-black/25 border border-white/20 text-xs font-semibold shrink-0">
          <CheckCircle2 className="w-4 h-4 text-[#9AE66E]" />
          <div>
            <div>ResNet50</div>
            <div className="text-[10px] text-emerald-200/80">(Transfer Learning)</div>
          </div>
        </div>
      </div>

      {!ev && (
        <div className="rounded-2xl bg-[#FFF7EC] dark:bg-[#2A2212] border border-[#F7D7A8] dark:border-[#5D4618] px-4 py-3 text-xs sm:text-sm text-[#7C4010] dark:text-amber-100 flex items-center gap-3">
          <Info className="w-5 h-5 text-[#D97706] shrink-0" />
          <div>
            <strong>Evaluation Results Not Available (Training Pending):</strong> Genuine metrics
            will populate automatically from <code>reports/metrics/evaluation_summary.json</code>{' '}
            and <code>artifacts/training_history.csv</code> once <code>src/train.py</code> and{' '}
            <code>src/evaluate.py</code> execute.
          </div>
        </div>
      )}

      {/* 6 Colored KPI Cards matching Reference Image 4 */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {metricCards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.label} className={`rounded-2xl border p-4 shadow-xs ${card.bg}`}>
              <div className="flex items-center gap-2.5 mb-2">
                <span
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${card.iconBg}`}
                >
                  <Icon className="w-4 h-4" />
                </span>
                <span className="text-xs font-semibold text-[#18352A] dark:text-emerald-100 truncate">
                  {card.label}
                </span>
              </div>
              <div className={`font-mono-num text-xl font-extrabold ${card.text}`}>{card.val}</div>
            </div>
          );
        })}
      </div>

      {/* Bottom 3-Column Analytics Row matching Reference Image 4 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 items-stretch">
        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-4 h-4 text-[#13823D]" />
            <h3 className="font-display font-bold text-sm text-[#18352A] dark:text-white">
              Training &amp; Validation Accuracy
            </h3>
          </div>
          {workspace?.trainingCurvesAvailable ? (
            <img
              src="/reports/figures/training_curves.png"
              alt="Training and validation curves"
              className="w-full rounded-xl border border-[#EEF4EF]"
            />
          ) : svgPoints ? (
            <svg viewBox="0 0 340 160" className="w-full h-48">
              <polyline fill="none" stroke="#13823D" strokeWidth="2.5" points={svgPoints.train} />
              <polyline fill="none" stroke="#F4B740" strokeWidth="2.5" points={svgPoints.val} />
            </svg>
          ) : (
            <div className="flex-1 min-h-52 rounded-xl bg-[#FAFDF9] dark:bg-[#0E1D17] border border-dashed border-[#D4E2D7] dark:border-[#244435] flex flex-col items-center justify-center p-4 text-center">
              <BarChart3 className="w-9 h-9 text-[#9AE66E] mb-2" />
              <div className="text-sm font-bold text-[#18352A] dark:text-white">
                Training curves pending
              </div>
              <div className="text-xs text-[#68796F] mt-1">Generated by src/train.py</div>
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-5 flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-3">
            <Grid3X3 className="w-4 h-4 text-[#13823D]" />
            <h3 className="font-display font-bold text-sm text-[#18352A] dark:text-white">
              Confusion Matrix
            </h3>
          </div>
          {workspace?.confusionMatrixAvailable ? (
            <img
              src="/reports/figures/confusion_matrix.png"
              alt="Known-species confusion matrix"
              className="w-full rounded-xl border border-[#EEF4EF]"
            />
          ) : (
            <div className="flex-1 min-h-52 rounded-xl bg-[#FAFDF9] dark:bg-[#0E1D17] border border-dashed border-[#D4E2D7] dark:border-[#244435] flex flex-col items-center justify-center p-4 text-center">
              <Grid3X3 className="w-9 h-9 text-[#9AE66E] mb-2" />
              <div className="text-sm font-bold text-[#18352A] dark:text-white">
                Confusion matrix pending
              </div>
              <div className="text-xs text-[#68796F] mt-1">Generated by src/evaluate.py</div>
            </div>
          )}
        </div>

        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-5 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="w-4 h-4 text-[#13823D]" />
            <h3 className="font-display font-bold text-sm text-[#18352A] dark:text-white">
              OOD Evaluation
            </h3>
          </div>
          <div className="space-y-2.5 text-xs flex-1">
            {oodRows.map((row) => (
              <div
                key={row.label}
                title={row.hint}
                className="flex items-center justify-between px-3.5 py-2.5 rounded-xl bg-[#F7FAF7] dark:bg-[#0E1D17] border border-[#E8F0EA] dark:border-[#1E3B2E]"
              >
                <span className="font-medium text-[#18352A] dark:text-emerald-100 flex items-center gap-1.5">
                  <span>{row.label}</span>
                  <Info className="w-3.5 h-3.5 text-[#8FA196]" />
                </span>
                <span
                  className={`font-mono-num font-bold ${
                    row.val === 'Pending'
                      ? 'text-[#13823D] bg-[#E8F5E9] px-2.5 py-0.5 rounded-md'
                      : 'text-[#053821] dark:text-white'
                  }`}
                >
                  {row.val}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
