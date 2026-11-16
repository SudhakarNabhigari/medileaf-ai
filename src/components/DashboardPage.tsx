import React, { useState } from 'react';
import {
  ArrowRight,
  BarChart3,
  Clock,
  Cpu,
  Database,
  Info,
  Layers,
  Leaf,
  ScanLine,
  ShieldCheck,
  X,
  Zap,
} from 'lucide-react';
import { motion } from 'motion/react';
import { LeafScannerGraphic } from './BotanicalArt';
import { CVTechnologyItem, NavSection, PredictionRecord, WorkspaceState } from '../types';

interface DashboardPageProps {
  workspace: WorkspaceState | null;
  history: PredictionRecord[];
  onNavigate: (section: NavSection) => void;
}

export function DashboardPage({ workspace, history, onNavigate }: DashboardPageProps) {
  const [selectedTech, setSelectedTech] = useState<CVTechnologyItem | null>(null);

  const knownSpeciesCount =
    workspace?.classMapping?.num_classes ??
    workspace?.datasetMeta?.valid_species_count ??
    null;

  const totalImagesCount = workspace?.datasetMeta?.valid_image_count ?? null;
  const modelReady = Boolean(workspace?.modelReady);
  const cvTechnologies = workspace?.cvTechnologies ?? [];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-6 relative z-10"
    >
      {/* Dark Emerald Botanical Hero Banner matching Reference Image 1 */}
      <div className="rounded-2xl bg-gradient-to-r from-[#053821] via-[#0A5331] to-[#116E40] p-6 sm:p-8 text-white shadow-lg flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 overflow-hidden">
        <div className="space-y-3 max-w-xl">
          <div className="inline-block px-3 py-1 rounded-full border border-white/25 bg-white/10 text-xs font-medium text-emerald-50">
            Computer Vision · ResNet50 · OOD Detection
          </div>
          <h2 className="font-display text-2xl sm:text-4xl font-extrabold tracking-tight text-balance">
            Welcome to <span className="text-[#9AE66E]">MediLeaf AI</span>
          </h2>
          <p className="text-sm sm:text-base text-emerald-50/90 leading-relaxed">
            An Intelligent Medicinal Leaf Identification System with a Reject Option
          </p>
          <div className="pt-2 flex flex-wrap items-center gap-6 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <Leaf className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">Identify</div>
                <div className="text-emerald-100/80">Known Leaves</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <ShieldCheck className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">Reject</div>
                <div className="text-emerald-100/80">Unknown (Uncertain)</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <Zap className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">Fast &amp;</div>
                <div className="text-emerald-100/80">Accurate</div>
              </div>
            </div>
          </div>
        </div>

        <div className="shrink-0 self-center lg:self-auto leaf-float">
          <LeafScannerGraphic badgeLabel="Medicinal Leaf" subLabel="✓ Recognized" />
        </div>
      </div>

      {/* 4 Summary Cards Row matching Reference Image 1 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#DCEEE0] dark:border-[#1E3B2E] p-4 flex items-center gap-3.5 shadow-xs">
          <div className="w-11 h-11 rounded-full bg-[#E8F5E9] dark:bg-[#1A3529] flex items-center justify-center text-[#13823D] shrink-0">
            <Leaf className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-xs text-[#68796F] dark:text-emerald-200/70">Known Species</div>
            <div className="font-mono-num text-xl font-extrabold text-[#18352A] dark:text-white truncate">
              {knownSpeciesCount !== null ? knownSpeciesCount : 'Not Loaded'}
            </div>
            <div className="text-[11px] text-[#68796F] dark:text-emerald-200/60">
              {knownSpeciesCount !== null ? 'Verified in split' : 'Run inspect_dataset.py'}
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#DCEEE0] dark:border-[#1E3B2E] p-4 flex items-center gap-3.5 shadow-xs">
          <div className="w-11 h-11 rounded-full bg-[#E8F5E9] dark:bg-[#1A3529] flex items-center justify-center text-[#13823D] shrink-0">
            <Database className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-xs text-[#68796F] dark:text-emerald-200/70">Total Images</div>
            <div className="font-mono-num text-xl font-extrabold text-[#18352A] dark:text-white truncate">
              {totalImagesCount !== null ? totalImagesCount.toLocaleString() : 'Not Loaded'}
            </div>
            <div className="text-[11px] text-[#68796F] dark:text-emerald-200/60">
              Mendeley v3 archive
            </div>
          </div>
        </div>

        <div className="bg-[#F2FBF9] dark:bg-[#11221B] rounded-2xl border border-[#CBECE5] dark:border-[#1E3B2E] p-4 flex items-center gap-3.5 shadow-xs">
          <div className="w-11 h-11 rounded-full bg-[#D7F5EE] dark:bg-[#1A3529] flex items-center justify-center text-[#0F766E] shrink-0">
            <Cpu className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-xs text-[#68796F] dark:text-emerald-200/70">Model</div>
            <div className="font-display text-xl font-extrabold text-[#18352A] dark:text-white">
              ResNet50
            </div>
            <div className="text-[11px] text-[#68796F] dark:text-emerald-200/60">
              PyTorch Transfer Learning
            </div>
          </div>
        </div>

        <div
          className={`rounded-2xl border p-4 flex items-center gap-3.5 shadow-xs ${
            modelReady
              ? 'bg-[#F0FAF2] border-[#C6E8CE] dark:bg-[#11221B] dark:border-[#1E3B2E]'
              : 'bg-[#FFF7ED] border-[#FED7AA] dark:bg-[#231B12] dark:border-[#4D381B]'
          }`}
        >
          <div
            className={`w-11 h-11 rounded-full flex items-center justify-center shrink-0 ${
              modelReady
                ? 'bg-[#DCFCE7] text-[#13823D]'
                : 'bg-[#FFEDD5] text-[#D97706]'
            }`}
          >
            <Layers className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-xs text-[#68796F] dark:text-emerald-200/70">Model Status</div>
            <div
              className={`font-display text-lg font-extrabold truncate ${
                modelReady ? 'text-[#13823D]' : 'text-[#C2410C] dark:text-[#F4B740]'
              }`}
            >
              {modelReady ? 'Ready' : 'Training Pending'}
            </div>
            <div
              className={`text-[11px] ${
                modelReady ? 'text-[#13823D]' : 'text-[#C2410C]/80 dark:text-[#F4B740]/80'
              }`}
            >
              {modelReady ? 'Checkpoint loaded' : 'Awaiting best_model.pth'}
            </div>
          </div>
        </div>
      </div>

      {/* Middle 2-Column Row: Quick Actions (3 Tiles) & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 flex flex-col justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Zap className="w-4 h-4 text-[#13823D]" />
              <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
                Quick Actions
              </h3>
            </div>
            <p className="text-xs text-[#68796F] dark:text-emerald-200/70 mb-4">
              Run key tasks of the MediLeaf AI system
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => onNavigate('identify')}
                className="rounded-2xl bg-gradient-to-br from-[#2E8B22] to-[#0E5B24] text-white p-4 text-center flex flex-col items-center justify-between gap-3 hover:brightness-105 transition-all shadow-sm"
              >
                <span className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center">
                  <ScanLine className="w-5 h-5" />
                </span>
                <div>
                  <div className="text-sm font-bold">Identify a Leaf</div>
                  <div className="text-[11px] text-emerald-100/85">Upload &amp; Predict</div>
                </div>
                <span className="w-6 h-6 rounded-full bg-white text-[#0E5B24] flex items-center justify-center self-end">
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </button>

              <button
                type="button"
                onClick={() => onNavigate('analytics')}
                className="rounded-2xl bg-[#F4FAF4] dark:bg-[#0E1D17] border border-[#DCECE0] dark:border-[#1E3B2E] p-4 text-center flex flex-col items-center justify-between gap-3 hover:border-[#13823D] transition-all"
              >
                <span className="w-10 h-10 rounded-xl bg-[#E1F3E4] dark:bg-[#193326] text-[#13823D] flex items-center justify-center">
                  <BarChart3 className="w-5 h-5" />
                </span>
                <div>
                  <div className="text-sm font-bold text-[#18352A] dark:text-white">
                    View Analytics
                  </div>
                  <div className="text-[11px] text-[#68796F]">Model Performance</div>
                </div>
                <span className="w-6 h-6 rounded-full bg-[#DCEFE0] text-[#13823D] flex items-center justify-center self-end">
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </button>

              <button
                type="button"
                onClick={() => onNavigate('dataset')}
                className="rounded-2xl bg-[#F4FAF4] dark:bg-[#0E1D17] border border-[#DCECE0] dark:border-[#1E3B2E] p-4 text-center flex flex-col items-center justify-between gap-3 hover:border-[#13823D] transition-all"
              >
                <span className="w-10 h-10 rounded-xl bg-[#E1F3E4] dark:bg-[#193326] text-[#13823D] flex items-center justify-center">
                  <Database className="w-5 h-5" />
                </span>
                <div>
                  <div className="text-sm font-bold text-[#18352A] dark:text-white">
                    Dataset Info
                  </div>
                  <div className="text-[11px] text-[#68796F]">Explore Classes</div>
                </div>
                <span className="w-6 h-6 rounded-full bg-[#DCEFE0] text-[#13823D] flex items-center justify-center self-end">
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 flex flex-col">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-[#13823D]" />
              <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
                Recent Activity
              </h3>
            </div>
            <button
              type="button"
              onClick={() => onNavigate('history')}
              className="text-xs font-semibold text-[#13823D] hover:underline"
            >
              View all →
            </button>
          </div>
          <p className="text-xs text-[#68796F] dark:text-emerald-200/70 mb-4">
            Your latest leaf identification records
          </p>

          {history.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-8 px-4 rounded-xl bg-[#F9FCF8] dark:bg-[#0E1D17] border border-dashed border-[#D4E2D7] dark:border-[#244435]">
              <Leaf className="w-8 h-8 text-[#75B798] mb-2" />
              <div className="text-sm font-semibold text-[#18352A] dark:text-white">
                No predictions yet
              </div>
              <p className="text-xs text-[#68796F] dark:text-emerald-200/70 mt-1 max-w-xs">
                Real inference results appear here after ResNet50 training and leaf identification.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-[#E6EFE8] dark:border-[#1E3B2E] text-[#68796F]">
                    <th className="py-2 pr-2">#</th>
                    <th className="py-2 pr-2">Leaf Image</th>
                    <th className="py-2 pr-2">Prediction / Result</th>
                    <th className="py-2 pr-2">Confidence</th>
                    <th className="py-2">Time</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#EEF4EF] dark:divide-[#1E3B2E]">
                  {history.slice(0, 3).map((item, idx) => (
                    <tr key={item.id}>
                      <td className="py-2.5 pr-2 font-mono-num text-[#68796F]">{idx + 1}</td>
                      <td className="py-2.5 pr-2">
                        {item.image_thumbnail_b64 ? (
                          <img
                            src={`data:image/jpeg;base64,${item.image_thumbnail_b64}`}
                            alt={item.filename}
                            className="w-9 h-9 rounded-lg object-cover"
                          />
                        ) : (
                          <div className="w-9 h-9 rounded-lg bg-[#E8F5E9] flex items-center justify-center">
                            <Leaf className="w-4 h-4 text-[#13823D]" />
                          </div>
                        )}
                      </td>
                      <td className="py-2.5 pr-2 font-semibold text-[#18352A] dark:text-white">
                        {item.predicted_species}
                      </td>
                      <td className="py-2.5 pr-2 font-mono-num">
                        {item.confidence !== null ? `${(item.confidence * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td className="py-2.5 text-[#68796F] whitespace-nowrap">{item.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* SECTION 6: Interactive Computer Vision Architecture & Technologies */}
      <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="font-display text-lg font-bold text-[#053821] dark:text-white">
              Computer Vision Architecture &amp; Technologies
            </h3>
            <p className="text-xs text-[#68796F] dark:text-emerald-200/75 mt-0.5">
              Click any technology card to inspect how it works, where it runs in MEDILEAF.AI, and
              its verified status.
            </p>
          </div>
          <div className="text-xs text-[#68796F] font-mono-num">
            {cvTechnologies.length} Core Modules
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3.5">
          {cvTechnologies.map((tech) => (
            <button
              key={tech.key}
              type="button"
              onClick={() => setSelectedTech(tech)}
              className="text-left rounded-xl border border-[#DCE8DF] dark:border-[#1E3B2E] bg-[#FAFDF9] dark:bg-[#0D1B15] p-4 hover:border-[#13823D] hover:shadow-sm transition-all flex flex-col justify-between gap-2"
            >
              <div>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-display font-bold text-sm text-[#053821] dark:text-emerald-300">
                    {tech.short_title}
                  </span>
                  <span
                    className={`text-[11px] font-bold ${
                      tech.status === 'VERIFIED'
                        ? 'text-[#13823D]'
                        : tech.status === 'IMPLEMENTED'
                        ? 'text-[#B45309] dark:text-[#F4B740]'
                        : 'text-[#68796F]'
                    }`}
                  >
                    {tech.status}
                  </span>
                </div>
                <div className="text-xs font-semibold text-[#18352A] dark:text-white mt-0.5">
                  {tech.full_name}
                </div>
                <p className="text-[11px] text-[#68796F] dark:text-emerald-200/70 mt-1.5 leading-relaxed">
                  {tech.summary}
                </p>
              </div>
              <div className="text-[11px] font-semibold text-[#13823D] dark:text-emerald-400 flex items-center gap-1 pt-1">
                <span>Inspect explanation</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom About Strip matching Reference Image 1 */}
      <div className="rounded-2xl bg-[#EFF7F0] dark:bg-[#11221B] border border-[#D4E7D7] dark:border-[#1E3B2E] px-5 py-4 flex items-center gap-3 text-xs sm:text-sm text-[#18352A] dark:text-emerald-100">
        <Info className="w-5 h-5 text-[#13823D] shrink-0" />
        <div>
          <strong>About MediLeaf AI:</strong> A CNN-based computer vision system that classifies
          Indian medicinal plant leaves and rejects unfamiliar inputs using a confidence-gated (OOD)
          mechanism.
        </div>
      </div>

      {/* Interactive Technology Modal Popup */}
      {selectedTech && (
        <div
          className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => setSelectedTech(null)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.18 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl bg-white dark:bg-[#11221B] rounded-2xl border border-[#DCE8DF] dark:border-[#1E3B2E] shadow-2xl overflow-hidden"
          >
            <div className="bg-gradient-to-r from-[#053821] to-[#116E40] px-6 py-4 text-white flex items-center justify-between">
              <div>
                <div className="text-xs text-lime-300 font-semibold">{selectedTech.category}</div>
                <h4 className="font-display text-lg font-bold">
                  {selectedTech.short_title} — {selectedTech.full_name}
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setSelectedTech(null)}
                aria-label="Close technology details"
                className="p-1.5 rounded-lg hover:bg-white/15 text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto text-sm">
              <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-[#E6EFE8] dark:border-[#1E3B2E]">
                <span className="text-xs font-mono-num text-[#465B50] dark:text-emerald-200/80">
                  Module: <code>{selectedTech.module_path}</code>
                </span>
                <span
                  className={`text-xs font-bold ${
                    selectedTech.status === 'VERIFIED'
                      ? 'text-[#13823D]'
                      : selectedTech.status === 'IMPLEMENTED'
                      ? 'text-[#B45309] dark:text-[#F4B740]'
                      : 'text-[#68796F]'
                  }`}
                >
                  {selectedTech.status} · {selectedTech.status_detail}
                </span>
              </div>

              <div>
                <div className="font-bold text-[#053821] dark:text-emerald-300 text-xs uppercase tracking-wide">
                  What is this?
                </div>
                <p className="mt-1 text-[#18352A] dark:text-emerald-50/90 leading-relaxed">
                  {selectedTech.what_is_this}
                </p>
              </div>

              <div>
                <div className="font-bold text-[#053821] dark:text-emerald-300 text-xs uppercase tracking-wide">
                  Why do we use it?
                </div>
                <p className="mt-1 text-[#18352A] dark:text-emerald-50/90 leading-relaxed">
                  {selectedTech.why_used}
                </p>
              </div>

              <div>
                <div className="font-bold text-[#053821] dark:text-emerald-300 text-xs uppercase tracking-wide">
                  How does it work in general?
                </div>
                <p className="mt-1 text-[#18352A] dark:text-emerald-50/90 leading-relaxed">
                  {selectedTech.how_it_works}
                </p>
              </div>

              <div>
                <div className="font-bold text-[#053821] dark:text-emerald-300 text-xs uppercase tracking-wide">
                  Where do we use it in MEDILEAF.AI?
                </div>
                <p className="mt-1 text-[#18352A] dark:text-emerald-50/90 leading-relaxed">
                  {selectedTech.where_used_in_medileaf}
                </p>
              </div>

              <div>
                <div className="font-bold text-[#053821] dark:text-emerald-300 text-xs uppercase tracking-wide">
                  What happens when it runs?
                </div>
                <p className="mt-1 text-[#18352A] dark:text-emerald-50/90 leading-relaxed">
                  {selectedTech.what_happens_when_runs}
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </motion.div>
  );
}
