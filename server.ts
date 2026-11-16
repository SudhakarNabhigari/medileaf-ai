import express from 'express';
import { execFile } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';
import { promisify } from 'util';
import { createServer as createViteServer } from 'vite';

const execFileAsync = promisify(execFile);
const ROOT_DIR = process.cwd();
const PORT = 3000;

function readJsonIfExists(relPath: string): Record<string, unknown> | null {
  const fullPath = path.join(ROOT_DIR, relPath);
  if (!fs.existsSync(fullPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
  } catch {
    return null;
  }
}

function parseCsvLine(line: string): string[] {
  const fields: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === ',' && !inQuotes) {
      fields.push(current.trim());
      current = '';
    } else {
      current += ch;
    }
  }
  fields.push(current.trim());
  return fields;
}

function readCsvRecords(relPath: string, limit = 50): Array<Record<string, string>> {
  const fullPath = path.join(ROOT_DIR, relPath);
  if (!fs.existsSync(fullPath)) return [];
  const raw = fs.readFileSync(fullPath, 'utf-8').trim();
  if (!raw) return [];
  const lines = raw.split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1, 1 + limit).map((line) => {
    const vals = parseCsvLine(line);
    const row: Record<string, string> = {};
    headers.forEach((h, i) => {
      row[h] = (vals[i] ?? '').trim();
    });
    return row;
  });
}

async function runAuthBridge(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const child = execFile(
      'python3',
      ['-m', 'auth.cli_bridge'],
      { cwd: ROOT_DIR, maxBuffer: 5 * 1024 * 1024 },
      (err, stdout, stderr) => {
        if (err) {
          reject(new Error(stderr || err.message));
          return;
        }
        try {
          resolve(JSON.parse(stdout.trim()));
        } catch (parseErr) {
          reject(parseErr);
        }
      },
    );
    child.stdin?.write(JSON.stringify(payload));
    child.stdin?.end();
  });
}

async function startServer() {
  const app = express();
  app.use(express.json({ limit: '15mb' }));

  app.get('/api/health', async (_req, res) => {
    const checkpointExists = fs.existsSync(path.join(ROOT_DIR, 'artifacts/best_model.pth'));
    const modelMeta = readJsonIfExists('artifacts/model_metadata.json');
    const datasetLoaded = fs.existsSync(path.join(ROOT_DIR, 'reports/dataset/dataset_metadata.json'));
    let pythonVersion = 'unknown';
    try {
      const { stdout } = await execFileAsync('python3', ['--version'], { cwd: ROOT_DIR });
      pythonVersion = stdout.trim();
    } catch {
      pythonVersion = 'unavailable';
    }
    res.json({
      ok: true,
      app: 'MEDILEAF.AI',
      checkpointExists,
      modelReady: Boolean(checkpointExists && modelMeta && modelMeta['status'] === 'READY'),
      datasetLoaded,
      pythonVersion,
    });
  });

  app.get('/api/workspace-state', async (_req, res) => {
    const datasetMeta = readJsonIfExists('reports/dataset/dataset_metadata.json');
    const classMapping = readJsonIfExists('artifacts/class_mapping.json');
    const modelMeta = readJsonIfExists('artifacts/model_metadata.json');
    const rejectionConfig = readJsonIfExists('artifacts/rejection_config.json');
    const splitConfig = readJsonIfExists('data/processed/split_configuration.json');
    const evaluationSummary = readJsonIfExists('reports/metrics/evaluation_summary.json');
    const classDistribution = readCsvRecords('reports/dataset/class_distribution.csv', 15);
    const trainingHistory = readCsvRecords('artifacts/training_history.csv', 100);
    const checkpointExists = fs.existsSync(path.join(ROOT_DIR, 'artifacts/best_model.pth'));

    let cvTechnologies: unknown[] = [];
    try {
      const { stdout } = await execFileAsync('python3', ['-m', 'src.cv_technologies'], {
        cwd: ROOT_DIR,
        maxBuffer: 2 * 1024 * 1024,
      });
      cvTechnologies = JSON.parse(stdout.trim());
    } catch {
      cvTechnologies = [];
    }

    res.json({
      verifiedMendeleyMetadata: {
        dataset_name: 'Indian Medicinal Leaves Image Datasets',
        source: 'Mendeley Data',
        record_id: '748f8jkphb',
        version: '3',
        doi: '10.17632/748f8jkphb.3',
        url: 'https://data.mendeley.com/datasets/748f8jkphb/3',
        licence: 'CC BY 4.0',
        contributors: 'Pushpa B R, Shobha Rani (Amrita Vishwa Vidyapeetham)',
        poisonous_coverage_status:
          'Unverified — inspect extracted local archive before claiming poisonous-species coverage.',
      },
      checkpointExists,
      modelReady: Boolean(checkpointExists && modelMeta && modelMeta['status'] === 'READY'),
      datasetMeta,
      classMapping,
      modelMeta,
      rejectionConfig,
      splitConfig,
      evaluationSummary,
      classDistribution,
      trainingHistory,
      cvTechnologies,
      confusionMatrixAvailable: fs.existsSync(path.join(ROOT_DIR, 'reports/figures/confusion_matrix.png')),
      trainingCurvesAvailable: fs.existsSync(path.join(ROOT_DIR, 'reports/figures/training_curves.png')),
    });
  });

  app.post('/api/inspect-dataset', async (_req, res) => {
    const rawDir = path.join(ROOT_DIR, 'data/raw');
    const entries = fs.existsSync(rawDir)
      ? fs.readdirSync(rawDir).filter((name) => !name.startsWith('.'))
      : [];

    if (entries.length === 0) {
      res.json({
        ok: false,
        message:
          'No dataset folders found in data/raw/. Download "Indian Medicinal Leaves Image Datasets" (Version 3, DOI: 10.17632/748f8jkphb.3) from Mendeley Data, extract the species folders into data/raw/, and click Load & Analyze Dataset again (or run python scripts/inspect_dataset.py).',
      });
      return;
    }

    try {
      const { stdout } = await execFileAsync('python3', ['scripts/inspect_dataset.py', '--raw-dir', 'data/raw'], {
        cwd: ROOT_DIR,
        maxBuffer: 10 * 1024 * 1024,
      });
      res.json({ ok: true, summary: JSON.parse(stdout.trim()) });
    } catch (err) {
      res.json({
        ok: false,
        message: `Dataset inspection failed in preview container: ${(err as Error).message}. Run "python scripts/inspect_dataset.py --raw-dir data/raw" inside your Python 3.12 environment with Pillow and Pandas installed.`,
      });
    }
  });

  app.post('/api/auth/register', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'register', ...req.body });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.post('/api/auth/login', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'login', ...req.body });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.post('/api/auth/change-password', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'change_password', ...req.body });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.get('/api/preferences/:userId', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'get_prefs', user_id: Number(req.params.userId) });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.post('/api/preferences', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'update_prefs', ...req.body });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.get('/api/history/:userId', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'get_history', user_id: Number(req.params.userId) });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.delete('/api/history/:userId', async (req, res) => {
    try {
      const result = await runAuthBridge({ action: 'clear_history', user_id: Number(req.params.userId) });
      res.json(result);
    } catch (err) {
      res.status(500).json({ ok: false, message: (err as Error).message });
    }
  });

  app.post('/api/predict', async (req, res) => {
    const { imageBase64, filename, userId, saveHistory } = req.body as {
      imageBase64?: string;
      filename?: string;
      userId?: number;
      saveHistory?: boolean;
    };

    if (!imageBase64 || !filename) {
      res.status(400).json({ status: 'INVALID_IMAGE', accepted: false, reason: 'No image payload received.' });
      return;
    }

    const checkpointPath = path.join(ROOT_DIR, 'artifacts/best_model.pth');
    const classMapPath = path.join(ROOT_DIR, 'artifacts/class_mapping.json');
    if (!fs.existsSync(checkpointPath) || !fs.existsSync(classMapPath)) {
      res.json({
        status: 'MODEL_NOT_READY',
        accepted: false,
        predicted_species: 'TRAINING_PENDING',
        confidence: null,
        energy_score: null,
        threshold_used: null,
        gate_method: null,
        reason:
          'Model Training Pending: Trained ResNet50 checkpoint (artifacts/best_model.pth) and class_mapping.json are not yet present. Run scripts/inspect_dataset.py, scripts/prepare_dataset.py, and train via notebooks/medicinal_leaf_identifier_colab.ipynb on GPU.',
        top_k: [],
      });
      return;
    }

    const cleanBase64 = imageBase64.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(cleanBase64, 'base64');
    const ext = path.extname(filename).toLowerCase() || '.jpg';
    const tempFile = path.join(os.tmpdir(), `medileaf_${Date.now()}${ext}`);

    try {
      fs.writeFileSync(tempFile, buffer);
      const { stdout } = await execFileAsync('python3', ['-m', 'src.inference', tempFile], {
        cwd: ROOT_DIR,
        maxBuffer: 5 * 1024 * 1024,
      });
      const prediction = JSON.parse(stdout.trim());

      if (saveHistory && userId && (prediction.status === 'ACCEPTED' || prediction.status === 'UNCERTAIN')) {
        await runAuthBridge({
          action: 'save_history',
          user_id: userId,
          filename,
          predicted_species: prediction.predicted_species,
          confidence: prediction.confidence,
          energy_score: prediction.energy_score,
          status: prediction.accepted ? 'Accepted' : 'Rejected',
          reason: prediction.reason,
          image_thumbnail_b64: cleanBase64.length <= 250000 ? cleanBase64 : null,
        });
      }

      res.json(prediction);
    } catch (err) {
      res.json({
        status: 'MODEL_NOT_READY',
        accepted: false,
        predicted_species: 'TRAINING_PENDING',
        confidence: null,
        energy_score: null,
        threshold_used: null,
        gate_method: null,
        reason: `Python ResNet50 runtime unavailable in this preview container (${(err as Error).message}). Run Streamlit locally or in Colab with requirements.txt installed.`,
        top_k: [],
      });
    } finally {
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
    }
  });

  app.use('/reports', express.static(path.join(ROOT_DIR, 'reports')));

  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });
  app.use(vite.middlewares);

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`MEDILEAF.AI Workspace Preview Server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
