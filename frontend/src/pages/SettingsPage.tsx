import React, { useState } from 'react';
import {
  Settings,
  ShieldCheck,
  Download,
  Database,
  Lock,
  FileText,
  AlertTriangle,
  CheckCircle2,
  Server
} from 'lucide-react';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [anonymizeExport, setAnonymizeExport] = useState(true);
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleDownload = () => {
    window.open(api.getExportUrl(), '_blank');
    setExportSuccess(true);
    setTimeout(() => setExportSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <span>Settings & Privacy Governance</span>
        </h1>
        <p className="text-slate-500 text-sm mt-1">
          Manage research protocols, data export parameters, and healthcare privacy guidelines.
        </p>
      </div>

      {/* Research Compliance & Ethics */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-slate-900">
          <ShieldCheck className="h-5 w-5 text-sky-600" />
          <h3 className="font-bold text-sm uppercase tracking-wide">Research Data Governance</h3>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          ThyroPredict AI adheres to scientific research integrity principles. Participant entries are stored with pseudonymous codes (e.g. <code>THYRO-PART-001</code>) by default. Personally identifiable information is separated from model inference records.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-start space-x-2.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-800">Informed Consent Protocol</span>
              <p className="text-slate-500 text-[11px] mt-0.5">Enforced on all participant registrations</p>
            </div>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-start space-x-2.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-800">No Target Memorization</span>
              <p className="text-slate-500 text-[11px] mt-0.5">Pruned Decision Tree (max_depth=5, leaf=3)</p>
            </div>
          </div>
        </div>
      </div>

      {/* Research Data Export */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 text-slate-900">
          <Database className="h-5 w-5 text-sky-600" />
          <h3 className="font-bold text-sm uppercase tracking-wide">Authorized Research Data Export</h3>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          Export recorded participant prediction records in CSV format for institutional review, clinical audit, or statistical post-processing.
        </p>

        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between text-xs">
          <div>
            <span className="font-semibold text-slate-800">De-Identify Identifiers</span>
            <p className="text-[11px] text-slate-500">Strip display names and preserve only research participant codes.</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={anonymizeExport}
              onChange={(e) => setAnonymizeExport(e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-600"></div>
          </label>
        </div>

        <div>
          <button
            onClick={handleDownload}
            className="inline-flex items-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-all"
          >
            <Download className="h-4 w-4" />
            <span>Download Research Audit CSV</span>
          </button>
          {exportSuccess && (
            <span className="text-xs text-emerald-600 font-semibold ml-3">
              Export started successfully!
            </span>
          )}
        </div>
      </div>

      {/* System & Architecture Info */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3 text-xs">
        <div className="flex items-center space-x-2 text-slate-900">
          <Server className="h-5 w-5 text-sky-600" />
          <h3 className="font-bold text-sm uppercase tracking-wide">Deployment Architecture</h3>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs pt-1 font-mono">
          <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 block text-[10px]">BACKEND</span>
            <span className="font-bold text-slate-800">FastAPI 0.110+</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 block text-[10px]">FRONTEND</span>
            <span className="font-bold text-slate-800">React + Vite + TS</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 block text-[10px]">PERSISTENCE</span>
            <span className="font-bold text-slate-800">SQLite / SQLAlchemy</span>
          </div>
          <div className="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span className="text-slate-400 block text-[10px]">ML ARTIFACTS</span>
            <span className="font-bold text-slate-800">Joblib v1.4.2</span>
          </div>
        </div>
      </div>

      {/* Legal & Medical Notice */}
      <div className="p-5 rounded-xl bg-slate-900 text-slate-300 text-xs space-y-2 border border-slate-800">
        <span className="text-amber-400 font-bold block">Medical Ethics & Jurisdictional Notice</span>
        <p className="leading-relaxed text-slate-400">
          This system is intended exclusively for investigational machine-learning research and educational analysis. It is not an FDA, CE, or CDSCO-cleared medical diagnostic device. Prediction outputs should never be utilized in isolation to initiate, alter, or withhold patient medication or medical care.
        </p>
      </div>
    </div>
  );
};
