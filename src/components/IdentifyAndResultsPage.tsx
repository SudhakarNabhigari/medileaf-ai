import React, { useRef, useState } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  Clock,
  CloudUpload,
  Cpu,
  Database,
  Image as ImageIcon,
  Leaf,
  Loader2,
  ShieldCheck,
  Upload,
  X,
  Zap,
} from 'lucide-react';
import { motion } from 'motion/react';
import { LeafScannerGraphic } from './BotanicalArt';
import { PredictionResult, SAFETY_DISCLAIMER, UserAccount, UserPreferences, WorkspaceState } from '../types';

interface IdentifyAndResultsPageProps {
  mode: 'identify' | 'results';
  user: UserAccount;
  preferences: UserPreferences;
  workspace: WorkspaceState | null;
  lastPrediction: PredictionResult | null;
  lastImageUrl: string | null;
  onPredictionComplete: (result: PredictionResult, imageUrl: string) => void;
  onBackToIdentify: () => void;
}

const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];
const MAX_BYTES = 10 * 1024 * 1024;

export function IdentifyAndResultsPage({
  mode,
  user,
  preferences,
  workspace,
  lastPrediction,
  lastImageUrl,
  onPredictionComplete,
  onBackToIdentify,
}: IdentifyAndResultsPageProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [predicting, setPredicting] = useState(false);

  function handleFileSelected(file: File | null) {
    setValidationError(null);
    if (!file) return;
    if (file.size === 0) {
      setValidationError('Selected file is empty (0 bytes).');
      return;
    }
    if (file.size > MAX_BYTES) {
      setValidationError('File exceeds maximum allowed size of 10 MB.');
      return;
    }
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    if (!ALLOWED_TYPES.includes(file.type) && !['jpg', 'jpeg', 'png'].includes(ext)) {
      setValidationError('Unsupported format. Please upload a JPG, JPEG, or PNG leaf image.');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      setSelectedFile(file);
      setPreviewUrl(String(reader.result));
    };
    reader.onerror = () => setValidationError('Failed to read image file.');
    reader.readAsDataURL(file);
  }

  async function handlePredict() {
    if (!selectedFile || !previewUrl) return;
    setValidationError(null);
    setPredicting(true);
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          imageBase64: previewUrl,
          filename: selectedFile.name,
          userId: user.id,
          saveHistory: preferences.save_history_enabled,
        }),
      });
      const data: PredictionResult = await res.json();
      onPredictionComplete(data, previewUrl);
    } catch {
      setValidationError('Failed communicating with inference endpoint.');
    } finally {
      setPredicting(false);
    }
  }

  // PAGE 4 — PREDICTION RESULTS
  if (mode === 'results' && lastPrediction) {
    const conf = lastPrediction.confidence ?? 0;
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="space-y-6 relative z-10"
      >
        <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-6 sm:p-8 shadow-xs">
          <div className="grid grid-cols-1 md:grid-cols-[260px_1fr] gap-8 items-start">
            <div className="rounded-2xl overflow-hidden border border-[#DCE8DF] dark:border-[#1E3B2E] bg-[#F6FAF5] dark:bg-[#0D1B15]">
              {lastImageUrl ? (
                <img src={lastImageUrl} alt="Uploaded leaf" className="w-full h-60 object-cover" />
              ) : (
                <div className="h-60 flex items-center justify-center text-xs text-[#68796F]">
                  No preview
                </div>
              )}
            </div>

            {lastPrediction.status === 'MODEL_NOT_READY' ? (
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 text-[#B45309] dark:text-[#F4B740] font-bold text-base">
                  <Clock className="w-5 h-5" />
                  <span>Model Training Pending</span>
                </div>
                <h2 className="font-display text-2xl font-bold text-[#18352A] dark:text-white">
                  Trained ResNet50 Checkpoint Required
                </h2>
                <p className="text-sm text-[#465B50] dark:text-emerald-100/80 leading-relaxed">
                  {lastPrediction.reason}
                </p>
                <div className="rounded-xl bg-[#FFF8EB] dark:bg-[#2A2212] border border-[#F6D897] dark:border-[#5D4618] p-4 text-xs text-[#78350F] dark:text-amber-200 space-y-1.5">
                  <div className="font-bold">Academic Integrity Enforcement:</div>
                  <div>
                    MEDILEAF.AI never generates dummy predictions or LLM guesses when{' '}
                    <code>artifacts/best_model.pth</code> is absent. Train ResNet50 via{' '}
                    <code>notebooks/medicinal_leaf_identifier_colab.ipynb</code> and place the
                    artifacts in <code>artifacts/</code>.
                  </div>
                </div>
              </div>
            ) : lastPrediction.accepted ? (
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 text-[#13823D] dark:text-emerald-400 font-bold text-base">
                  <CheckCircle2 className="w-5 h-5" />
                  <span>Prediction Accepted</span>
                </div>
                <h2 className="font-display text-3xl font-extrabold text-[#18352A] dark:text-white italic">
                  {lastPrediction.predicted_species}
                </h2>
                <div className="font-mono-num text-lg font-semibold text-[#18352A] dark:text-emerald-100">
                  Confidence: {conf.toFixed(2)} ({(conf * 100).toFixed(1)}%)
                </div>
                <div className="w-full h-3 rounded-full bg-[#E8F5E9] dark:bg-[#193026] overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, Math.max(0, conf * 100))}%` }}
                    transition={{ duration: 0.45 }}
                    className="h-full bg-[#13823D] rounded-full"
                  />
                </div>
                <p className="text-xs text-[#68796F] dark:text-emerald-200/75">
                  {lastPrediction.reason}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 text-[#D97706] dark:text-[#F4B740] font-extrabold text-xl">
                  <AlertTriangle className="w-6 h-6" />
                  <span>UNCERTAIN</span>
                </div>
                <p className="text-base font-semibold text-[#18352A] dark:text-white">
                  The model cannot confidently identify this leaf.
                </p>
                <div className="font-mono-num text-sm font-semibold text-[#465B50] dark:text-emerald-100/80">
                  Confidence: {conf.toFixed(2)} ({(conf * 100).toFixed(1)}%) · Threshold:{' '}
                  {lastPrediction.threshold_used?.toFixed(2) ?? '—'}
                </div>
                <div className="w-full h-3 rounded-full bg-[#F3EFE6] dark:bg-[#2A2212] overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, Math.max(4, conf * 100))}%` }}
                    transition={{ duration: 0.45 }}
                    className="h-full bg-[#F4B740] rounded-full"
                  />
                </div>
              </div>
            )}
          </div>

          {lastPrediction.status !== 'MODEL_NOT_READY' && (
            <div className="mt-8">
              {lastPrediction.accepted ? (
                <div className="rounded-2xl bg-[#F9FCF8] dark:bg-[#0E1D17] border border-[#DCE8DF] dark:border-[#1E3B2E] p-5 space-y-3">
                  <h3 className="font-display font-bold text-base text-[#053821] dark:text-emerald-300">
                    Plant Information
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-[160px_1fr] gap-y-2 text-sm">
                    <span className="text-[#68796F]">Dataset Class</span>
                    <span className="font-semibold text-[#18352A] dark:text-white">
                      {lastPrediction.predicted_species}
                    </span>
                    <span className="text-[#68796F]">Gate Method</span>
                    <span className="font-mono-num text-[#18352A] dark:text-emerald-100">
                      {lastPrediction.gate_method} (Energy:{' '}
                      {lastPrediction.energy_score?.toFixed(3) ?? '—'})
                    </span>
                    <span className="text-[#68796F]">Reference</span>
                    <span className="text-[#18352A] dark:text-emerald-100">
                      Indian Medicinal Leaves Image Datasets v3 (Mendeley DOI: 10.17632/748f8jkphb.3)
                    </span>
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl bg-[#FFF8EB] dark:bg-[#2A2212] border border-[#F6D897] dark:border-[#5D4618] p-5 space-y-2">
                  <h3 className="font-display font-bold text-base text-[#92400E] dark:text-[#F4B740]">
                    Why UNCERTAIN?
                  </h3>
                  <ul className="list-disc pl-5 text-sm text-[#78350F] dark:text-amber-100/90 space-y-1">
                    <li>{lastPrediction.reason}</li>
                    <li>
                      The leaf may belong to an out-of-distribution species not seen during training.
                    </li>
                    <li>Try uploading a clearer leaf photograph with clean framing and lighting.</li>
                  </ul>
                </div>
              )}
            </div>
          )}

          <div className="mt-6 flex flex-wrap items-center justify-between gap-4 pt-5 border-t border-[#E6EFE8] dark:border-[#1E3B2E]">
            <p className="text-xs text-[#68796F] dark:text-emerald-200/70 max-w-2xl">
              {SAFETY_DISCLAIMER}
            </p>
            <button
              type="button"
              onClick={onBackToIdentify}
              className="px-5 py-2.5 rounded-xl bg-[#13823D] hover:bg-[#0F6B31] text-white text-sm font-semibold transition-colors whitespace-nowrap"
            >
              Identify Another Leaf
            </button>
          </div>
        </div>
      </motion.div>
    );
  }

  // PAGE 3 — LEAF IDENTIFICATION matching Reference Image 2
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="space-y-5 relative z-10"
    >
      {/* Top Dark Emerald Banner */}
      <div className="rounded-2xl bg-gradient-to-r from-[#053821] via-[#0A5331] to-[#116E40] p-6 sm:p-8 text-white shadow-lg flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
        <div className="space-y-3 max-w-xl">
          <h2 className="font-display text-2xl sm:text-4xl font-extrabold tracking-tight flex items-center gap-2">
            <span>Identify a</span>
            <span className="text-[#9AE66E]">Leaf</span>
            <Leaf className="w-7 h-7 text-[#9AE66E]" />
          </h2>
          <p className="text-sm text-emerald-50/90 leading-relaxed">
            Upload a leaf image to identify the plant species using our ResNet50 model with a
            reject option.
          </p>
          <div className="pt-1 flex flex-wrap items-center gap-6 text-xs">
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <Cpu className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">CNN</div>
                <div className="text-emerald-100/80">(ResNet50)</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <ShieldCheck className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">Rejects</div>
                <div className="text-emerald-100/80">Unknown (Uncertain)</div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center text-[#9AE66E]">
                <Zap className="w-3.5 h-3.5" />
              </span>
              <div>
                <div className="font-bold">Accurate</div>
                <div className="text-emerald-100/80">&amp; Reliable</div>
              </div>
            </div>
          </div>
        </div>
        <div className="shrink-0 self-center lg:self-auto leaf-float">
          <LeafScannerGraphic badgeLabel="Medicinal Leaf Recognition" compact />
        </div>
      </div>

      {!workspace?.modelReady && (
        <div className="rounded-2xl bg-[#FFF7EC] dark:bg-[#2A2212] border border-[#F7D7A8] dark:border-[#5D4618] px-4 py-3 text-xs sm:text-sm text-[#7C4010] dark:text-amber-100 flex items-center gap-3">
          <Clock className="w-5 h-5 text-[#D97706] shrink-0" />
          <div>
            <strong>Model Training Pending:</strong> Upload and client/server image validation are
            active. Full PyTorch ResNet50 inference requires training{' '}
            <code>artifacts/best_model.pth</code> via Google Colab GPU or <code>src/train.py</code>.
          </div>
        </div>
      )}

      {/* Upload Dropzone Card matching Reference Image 2 */}
      <div className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#DCEEE0] dark:border-[#1E3B2E] p-6 sm:p-8 shadow-xs">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            handleFileSelected(e.dataTransfer.files?.[0] ?? null);
          }}
          onClick={() => !previewUrl && fileInputRef.current?.click()}
          className={`rounded-2xl border-2 border-dashed p-6 sm:p-10 transition-colors ${
            dragOver
              ? 'border-[#13823D] bg-[#E8F5E9]/70 dark:bg-[#173A2B]/60'
              : 'border-[#B6D8BE] dark:border-[#2B5240] bg-[#F7FCF7] dark:bg-[#0D1B15]'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".jpg,.jpeg,.png"
            className="hidden"
            onChange={(e) => handleFileSelected(e.target.files?.[0] ?? null)}
          />

          {!previewUrl ? (
            <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1.2fr] gap-6 items-center">
              <div className="flex justify-center">
                <div className="w-36 h-32 rounded-2xl bg-white dark:bg-[#11221B] border border-[#DCECE0] dark:border-[#1E3B2E] shadow-md flex items-center justify-center relative">
                  <Leaf className="w-16 h-16 text-[#22C55E]" />
                  <span className="absolute top-2.5 left-2.5 w-3 h-3 border-t-2 border-l-2 border-[#053821] dark:border-lime-400" />
                  <span className="absolute top-2.5 right-2.5 w-3 h-3 border-t-2 border-r-2 border-[#053821] dark:border-lime-400" />
                  <span className="absolute bottom-2.5 left-2.5 w-3 h-3 border-b-2 border-l-2 border-[#053821] dark:border-lime-400" />
                  <span className="absolute bottom-2.5 right-2.5 w-3 h-3 border-b-2 border-r-2 border-[#053821] dark:border-lime-400" />
                </div>
              </div>

              <div className="hidden md:block w-px h-32 bg-[#DCECE0] dark:bg-[#1E3B2E]" />

              <div className="text-center space-y-2.5">
                <CloudUpload className="w-10 h-10 text-[#13823D] mx-auto" />
                <div className="font-display text-lg font-bold text-[#18352A] dark:text-white">
                  Upload a Leaf Image
                </div>
                <p className="text-xs sm:text-sm text-[#68796F] dark:text-emerald-200/75">
                  Drag and drop an image here, or click to browse
                </p>
                <p className="text-xs text-[#8FA196] bg-[#EEF5EF] dark:bg-[#162C22] inline-block px-3 py-1 rounded-md">
                  Supported formats: JPG, JPEG, PNG | Max size: 10 MB
                </p>
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      fileInputRef.current?.click();
                    }}
                    className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-gradient-to-r from-[#0E6A30] to-[#168A41] hover:brightness-105 text-white text-sm font-semibold shadow-sm"
                  >
                    <Upload className="w-4 h-4" />
                    <span>Choose Image</span>
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <div className="relative rounded-2xl overflow-hidden border border-[#DCE8DF] dark:border-[#1E3B2E] shadow-sm w-64 h-48 bg-white">
                <img
                  src={previewUrl}
                  alt={selectedFile?.name || 'Leaf preview'}
                  className="w-full h-full object-cover"
                />
                <button
                  type="button"
                  onClick={() => {
                    setSelectedFile(null);
                    setPreviewUrl(null);
                    setValidationError(null);
                  }}
                  aria-label="Remove uploaded image"
                  className="absolute top-2 right-2 w-7 h-7 rounded-full bg-black/70 hover:bg-black text-white flex items-center justify-center"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="text-xs font-mono-num text-[#68796F]">
                {selectedFile?.name} · {((selectedFile?.size || 0) / 1024).toFixed(1)} KB
              </div>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2.5 rounded-xl border border-[#DCE8DF] text-xs font-semibold hover:bg-white"
                >
                  Replace Image
                </button>
                <button
                  type="button"
                  onClick={handlePredict}
                  disabled={predicting}
                  className="px-6 py-2.5 rounded-full bg-gradient-to-r from-[#0E6A30] to-[#168A41] text-white text-sm font-semibold shadow-sm flex items-center gap-2 disabled:opacity-60"
                >
                  {predicting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Running ResNet50...</span>
                    </>
                  ) : (
                    <>
                      <span>Predict Species</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {validationError && (
          <div
            role="alert"
            className="mt-4 rounded-xl bg-[#FEF2F2] border border-[#FECACA] px-4 py-3 text-xs font-medium text-[#B91C1C] text-center"
          >
            {validationError}
          </div>
        )}
      </div>

      {/* Bottom 4 Mini Feature Cards matching Reference Image 2 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            icon: ImageIcon,
            title: 'Plant Identification',
            desc: 'Detects known medicinal leaves',
          },
          {
            icon: ShieldCheck,
            title: 'Uncertainty Handling',
            desc: 'Returns "UNCERTAIN" for unfamiliar leaves',
          },
          {
            icon: BarChart3,
            title: 'Model',
            desc: 'ResNet50 (Transfer Learning)',
          },
          {
            icon: Leaf,
            title: 'Dataset',
            desc: 'Indian Medicinal Leaf Dataset (Mendeley)',
          },
        ].map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className="bg-white dark:bg-[#11221B] rounded-2xl border border-[#E2ECE4] dark:border-[#1E3B2E] p-4 flex items-center gap-3 shadow-xs"
            >
              <span className="w-10 h-10 rounded-full bg-[#E8F5E9] dark:bg-[#1A3529] text-[#13823D] flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4" />
              </span>
              <div className="min-w-0">
                <div className="text-xs font-bold text-[#18352A] dark:text-white">{card.title}</div>
                <div className="text-[11px] text-[#68796F] dark:text-emerald-200/70">
                  {card.desc}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
