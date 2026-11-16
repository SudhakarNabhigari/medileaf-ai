import React, { useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  Database,
  ExternalLink,
  FileText,
  Info,
  Layers,
  Leaf,
  Loader2,
  Scale,
  Tag,
  Upload,
  Users,
} from 'lucide-react';
import { motion } from 'motion/react';
import { SAFETY_DISCLAIMER, WorkspaceState } from '../types';

interface DatasetPageProps {
  workspace: WorkspaceState | null;
  onDatasetInspected?: () => Promise<void>;
}

export function DatasetPage({ workspace, onDatasetInspected }: DatasetPageProps) {
  const [inspecting, setInspecting] = useState(false);
  const [inspectMessage, setInspectMessage] = useState<string | null>(null);

  const mendeley = workspace?.verifiedMendeleyMetadata;
  const meta = workspace?.datasetMeta;
  const dist = workspace?.classDistribution ?? [];
  const top5 = dist.slice(0, 5);
  const maxCount = Math.max(1, ...top5.map((d) => Number(d.valid_image_count) || 0));

  async function handleInspectDataset() {
    setInspecting(true);
    setInspectMessage(null);
    try {
      const res = await fetch('/api/inspect-dataset', { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        setInspectMessage('Dataset inspection completed successfully.');
        if (onDatasetInspected) await onDatasetInspected();
      } else {
        setInspectMessage(data.message);
      }
    } catch {
      setInspectMessage('Unable to inspect dataset directory.');
    } finally {
      setInspecting(false);
    }
  }

  const detailRows = [
    { icon: FileText, label: 'Dataset Name', value: mendeley?.dataset_name ?? 'Indian Medicinal Leaves Image Datasets' },
    { icon: Layers, label: 'Source', value: mendeley?.source ?? 'Mendeley Data' },
    { icon: Tag, label: 'Version', value: mendeley?.version ?? '3' },
    { icon: ExternalLink, label: 'DOI', value: mendeley?.doi ?? '10.17632/748f8jkphb.3' },
    { icon: Scale, label: 'License', value: mendeley?.licence ?? 'CC BY 4.0' },
    { icon: Users, label: 'Contributors', value: mendeley?.contributors ?? 'Pushpa B R, Shobha Rani' },
    {
      icon: Database,
      label: 'Total Images',
      value:
        meta?.valid_image_count !== undefined
          ? meta.valid_image_count.toLocaleString()
          : 'Dataset not loaded',
    },
    {
      icon: Leaf,
      label: 'Total Species',
      value:
        meta?.valid_species_count !== undefined
          ? String(meta.valid_species_count)
          : 'Dataset not loaded',
    },
    {
      icon: AlertTriangle,
      label: 'Poisonous Coverage',
      value:
        mendeley?.poisonous_coverage_status ??
        'Unverified — inspect extracted local archive before claiming poisonous-species coverage.',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-5 relative z-10"
    >
      {/* Top Emerald Banner matching Reference Image 5 */}
      <div className="rounded-2xl bg-gradient-to-r from-[#053821] via-[#0A5331] to-[#116E40] p-6 sm:p-7 text-white shadow-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-white/10 border border-white/15 flex items-center justify-center shrink-0">
            <Database className="w-7 h-7 text-[#9AE66E]" />
          </div>
          <div>
            <h2 className="font-display text-2xl sm:text-3xl font-extrabold tracking-tight">
              Dataset &amp; Project Information
            </h2>
            <p className="text-xs sm:text-sm text-emerald-50/90 mt-1">
              Details of the dataset, class distribution, and the MediLeaf AI project.
            </p>
          </div>
        </div>
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-black/25 border border-white/20 text-xs font-semibold shrink-0">
          <Leaf className="w-4 h-4 text-[#9AE66E]" />
          <span>Indian Medicinal Leaves Dataset</span>
        </div>
      </div>

      {/* Middle 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-stretch">
        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-[#13823D]" />
              <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
                Dataset Details
              </h3>
            </div>
            {mendeley?.url && (
              <a
                href={mendeley.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 px-3 py-1 rounded-lg bg-[#EEF7F0] dark:bg-[#193326] text-xs font-semibold text-[#13823D] dark:text-emerald-300 hover:underline"
              >
                <span>Mendeley Record</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>

          <div className="space-y-1.5 text-xs sm:text-sm">
            {detailRows.map((row, i) => {
              const Icon = row.icon;
              return (
                <div
                  key={row.label}
                  className={`grid grid-cols-[150px_1fr] gap-3 px-3 py-2 rounded-lg items-center ${
                    i % 2 === 0 ? 'bg-[#F7FBF7] dark:bg-[#0E1D17]' : ''
                  }`}
                >
                  <div className="flex items-center gap-2 text-[#68796F] dark:text-emerald-200/75 font-medium">
                    <Icon className="w-3.5 h-3.5 text-[#13823D] shrink-0" />
                    <span>{row.label}</span>
                  </div>
                  <div className="font-semibold text-[#18352A] dark:text-white">{row.value}</div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4 text-[#13823D]" />
            <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
              Class Distribution (Top 5)
            </h3>
          </div>

          {top5.length === 0 ? (
            <div className="flex-1 min-h-60 rounded-2xl bg-[#F7FCF7] dark:bg-[#0E1D17] border border-dashed border-[#C7E0CC] dark:border-[#244435] flex flex-col items-center justify-center p-6 text-center space-y-3">
              <Database className="w-10 h-10 text-[#43A047]" />
              <div className="font-display text-base font-bold text-[#18352A] dark:text-white">
                Dataset not loaded
              </div>
              <p className="text-xs text-[#68796F] dark:text-emerald-200/70 max-w-sm leading-relaxed">
                Extract the Mendeley v3 archive into <code>data/raw/</code> and run{' '}
                <code>python scripts/inspect_dataset.py</code> to inspect verified species counts.
              </p>
              <button
                type="button"
                onClick={handleInspectDataset}
                disabled={inspecting}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-[#0E6A30] to-[#168A41] text-white text-xs font-semibold shadow-sm hover:brightness-105 disabled:opacity-60"
              >
                {inspecting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Upload className="w-3.5 h-3.5" />
                )}
                <span>Load &amp; Analyze Dataset</span>
              </button>
              {inspectMessage && (
                <div className="mt-2 rounded-xl bg-[#FFF8EB] border border-[#F6D897] px-3.5 py-2.5 text-xs text-[#78350F] max-w-md text-left">
                  {inspectMessage}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4 flex-1 flex flex-col justify-center">
              {top5.map((row) => {
                const count = Number(row.valid_image_count) || 0;
                const pct = Math.round((count / maxCount) * 100);
                return (
                  <div key={row.species} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="truncate pr-2 text-[#18352A] dark:text-white">
                        {row.species}
                      </span>
                      <span className="font-mono-num text-[#13823D]">
                        {count.toLocaleString()}
                      </span>
                    </div>
                    <div className="h-3 rounded-full bg-[#E8F5E9] dark:bg-[#193026] overflow-hidden">
                      <div
                        className="h-full bg-[#43A047] rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Bottom About the Project Card matching Reference Image 5 */}
      <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 space-y-3">
        <div className="flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-[#13823D]" />
          <h3 className="font-display text-base font-bold text-[#18352A] dark:text-white">
            About the Project
          </h3>
        </div>
        <p className="text-xs sm:text-sm text-[#465B50] dark:text-emerald-100/85 leading-relaxed">
          <strong>MEDILEAF.AI</strong> (<em>Medicinal-Leaf Identifier with a Reject Option</em>) is
          a Computer Vision system that identifies Indian medicinal plant species from leaf
          photographs using a fine-tuned PyTorch ResNet50 CNN and abstains with{' '}
          <strong>UNCERTAIN</strong> for unfamiliar (held-out out-of-distribution) or low-reliability
          inputs.
        </p>
        <div className="rounded-xl bg-[#F4F8F2] dark:bg-[#152920] border border-[#DCE8DF] dark:border-[#244435] p-3.5 text-xs text-[#465B50] dark:text-emerald-100/80 flex items-start gap-2.5">
          <Info className="w-4 h-4 text-[#13823D] shrink-0 mt-0.5" />
          <span>{SAFETY_DISCLAIMER}</span>
        </div>
      </div>
    </motion.div>
  );
}
