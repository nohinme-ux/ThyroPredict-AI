import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  UserCheck,
  CheckCircle2,
  AlertTriangle,
  Printer,
  RefreshCw,
  Info,
  ChevronRight,
  Database,
  ArrowRight,
  FileText,
  Activity,
  Layers,
  FlaskConical,
  BrainCircuit
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchParticipant, Prediction } from '../types';

interface NewPredictionPageProps {
  onPredictionSuccess?: () => void;
  onNavigate: (tab: string) => void;
}

export const NewPredictionPage: React.FC<NewPredictionPageProps> = ({ onNavigate, onPredictionSuccess }) => {
  const [participants, setParticipants] = useState<ResearchParticipant[]>([]);
  const [selectedParticipantId, setSelectedParticipantId] = useState<string>('');
  const [modelType, setModelType] = useState<'sts_clinical' | 'uci_benchmark'>('sts_clinical');

  // New Participant Quick Modal
  const [showQuickParticipantModal, setShowQuickParticipantModal] = useState(false);
  const [newCode, setNewCode] = useState('');
  const [newName, setNewName] = useState('');
  const [newAge, setNewAge] = useState<number>(45);
  const [newSex, setNewSex] = useState('F');

  // Form State for STS Clinical Model
  const [stsForm, setStsForm] = useState({
    AGE: 45,
    SEX: 'F',
    DURATION: 3,
    HGT: 155,
    WGT: 65,
    bmi: 27.0,
    SYS: 120,
    DIA: 80,
    FBS: 95,
    FT3: 2.1,
    FT4: 0.65,
    TSH: 26.5,
    Anti_tpo: 5.2,
    Visfatin: 24.0,
    Thyroglobulin: 18.0,
    IL6: 4.2,
    TCHOL: 215,
    TGL: 155,
    HDL: 44,
    LDL: 140,
    HB: 12.8,
    WBC: 6600,
    PLT: 255
  });

  // Form State for UCI Benchmark Model
  const [uciForm, setUciForm] = useState({
    age: 55,
    sex: 'F',
    on_thyroxine: false,
    query_on_thyroxine: false,
    on_antithyroid_medication: false,
    sick: false,
    pregnant: false,
    thyroid_surgery: false,
    I131_treatment: false,
    query_hypothyroid: false,
    query_hyperthyroid: false,
    lithium: false,
    goitre: false,
    tumor: false,
    hypopituitary: false,
    psych: false,
    TSH: 35.0,
    T3: 1.1,
    TT4: 45.0,
    T4U: 1.15,
    FTI: 39.0
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Prediction | null>(null);

  useEffect(() => {
    loadParticipants();
  }, []);

  const loadParticipants = async () => {
    try {
      const data = await api.getParticipants();
      setParticipants(data);
      if (data.length > 0 && !selectedParticipantId) {
        setSelectedParticipantId(data[0].id);
      }
    } catch (err: any) {
      console.error('Failed to load participants', err);
    }
  };

  const handleQuickCreateParticipant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCode.trim()) return;
    try {
      const p = await api.createParticipant({
        research_participant_code: newCode.trim(),
        display_name: newName.trim() || undefined,
        age: Number(newAge) || undefined,
        sex: newSex,
        consent_status: true,
        notes: 'Enrolled via New Prediction workflow'
      });
      setParticipants([p, ...participants]);
      setSelectedParticipantId(p.id);
      setShowQuickParticipantModal(false);
      setNewCode('');
      setNewName('');
    } catch (err: any) {
      alert(`Error creating participant: ${err.message}`);
    }
  };

  // Preset loaders for rapid testing
  const loadPreset = (presetType: 'hypo' | 'autoimmune' | 'normal' | 'hyper') => {
    if (modelType === 'sts_clinical') {
      if (presetType === 'hypo') {
        setStsForm({
          AGE: 56, SEX: 'F', DURATION: 5, HGT: 153, WGT: 48, bmi: 20.5,
          SYS: 120, DIA: 80, FBS: 92, FT3: 2.65, FT4: 0.47, TSH: 22.7,
          Anti_tpo: 0.11, Visfatin: 22.0, Thyroglobulin: 15.0, IL6: 3.8,
          TCHOL: 210, TGL: 140, HDL: 48, LDL: 130, HB: 13.1, WBC: 7200, PLT: 284
        });
      } else if (presetType === 'autoimmune') {
        setStsForm({
          AGE: 44, SEX: 'F', DURATION: 4, HGT: 142, WGT: 51, bmi: 25.3,
          SYS: 100, DIA: 70, FBS: 89, FT3: 4.90, FT4: 2.12, TSH: 0.01,
          Anti_tpo: 228.4, Visfatin: 28.0, Thyroglobulin: 35.0, IL6: 5.2,
          TCHOL: 175, TGL: 120, HDL: 52, LDL: 95, HB: 12.8, WBC: 6800, PLT: 250
        });
      } else if (presetType === 'normal') {
        setStsForm({
          AGE: 37, SEX: 'F', DURATION: 0, HGT: 158, WGT: 56, bmi: 22.4,
          SYS: 110, DIA: 70, FBS: 88, FT3: 3.65, FT4: 1.09, TSH: 2.45,
          Anti_tpo: 8.5, Visfatin: 20.0, Thyroglobulin: 22.0, IL6: 2.1,
          TCHOL: 170, TGL: 105, HDL: 55, LDL: 94, HB: 13.5, WBC: 6200, PLT: 240
        });
      } else if (presetType === 'hyper') {
        setStsForm({
          AGE: 32, SEX: 'F', DURATION: 2, HGT: 160, WGT: 49, bmi: 19.1,
          SYS: 135, DIA: 75, FBS: 94, FT3: 6.8, FT4: 3.2, TSH: 0.005,
          Anti_tpo: 12.0, Visfatin: 24.0, Thyroglobulin: 45.0, IL6: 4.8,
          TCHOL: 155, TGL: 95, HDL: 42, LDL: 94, HB: 12.4, WBC: 5900, PLT: 230
        });
      }
    } else {
      if (presetType === 'hypo') {
        setUciForm({
          ...uciForm, age: 58, TSH: 42.0, T3: 0.9, TT4: 35.0, T4U: 1.2, FTI: 29.0
        });
      } else if (presetType === 'normal') {
        setUciForm({
          ...uciForm, age: 35, TSH: 1.8, T3: 2.2, TT4: 115.0, T4U: 0.98, FTI: 117.0
        });
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedParticipantId) {
      setError('Please select or register a research participant first.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload: any = {
        participant_id: selectedParticipantId,
        model_type: modelType,
      };

      if (modelType === 'sts_clinical') {
        payload.sts_features = stsForm;
      } else {
        payload.uci_features = uciForm;
      }

      const res = await api.createPrediction(payload);
      setResult(res);
      if (onPredictionSuccess) onPredictionSuccess();
    } catch (err: any) {
      setError(err.message || 'Error occurred while computing prediction.');
    } finally {
      setLoading(false);
    }
  };

  const getClinicalDescription = (predClass: string) => {
    switch (predClass) {
      case 'Autoimmune Thyroid Disease':
        return 'Elevated Anti-TPO autoantibody levels characteristic of chronic autoimmune thyroiditis (Hashimoto\'s) or Graves\' disease pathology.';
      case 'Primary Hypothyroidism':
        return 'Markedly elevated serum TSH with deficient or borderline thyroid hormone concentration, indicating intrinsic thyroid gland hypoactivity without high autoantibodies.';
      case 'Euthyroid / Normal':
        return 'Normal pituitary-thyroid negative feedback equilibrium with serum TSH, FT4, and FT3 within physiological reference ranges.';
      case 'Hyperthyroid':
        return 'Suppressed pituitary TSH concentration accompanied by excess circulating thyroid hormone, reflecting biochemical thyrotoxicosis.';
      case 'compensated hypothyroid':
        return 'Mild subclinical state where compensatory elevated TSH maintains circulating peripheral thyroid hormone in the normal reference window.';
      case 'primary hypothyroid':
        return 'Overt clinical hypothyroidism supported by elevated TSH and low circulating thyroxine.';
      case 'negative':
        return 'Euthyroid baseline: laboratory measurements do not indicate hypothyroidism.';
      default:
        return 'Documented classification according to dataset criteria.';
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>New Research Prediction</span>
            <span className="text-xs bg-sky-100 text-sky-800 font-semibold px-2.5 py-0.5 rounded-full">
              Decision Tree Classifier
            </span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Input verified clinical or laboratory markers to generate reproducible, explainable Decision Tree predictions.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onNavigate('history')}
            className="text-xs text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 font-medium px-3.5 py-2 rounded-lg transition-all"
          >
            Review Past Records
          </button>
        </div>
      </div>

      {/* Main Grid: Form Left, Results/Presets Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <form onSubmit={handleSubmit} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
            {/* Step 1: Participant Selection */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <UserCheck className="h-4 w-4 text-sky-600" />
                  <span>1. Research Participant</span>
                </label>
                <button
                  type="button"
                  onClick={() => setShowQuickParticipantModal(true)}
                  className="text-xs text-sky-600 hover:text-sky-700 font-semibold inline-flex items-center gap-1"
                >
                  <span>+ Quick Add Participant</span>
                </button>
              </div>

              {participants.length > 0 ? (
                <select
                  value={selectedParticipantId}
                  onChange={(e) => setSelectedParticipantId(e.target.value)}
                  className="w-full text-xs bg-slate-50 border border-slate-300 rounded-lg p-2.5 text-slate-800 focus:ring-2 focus:ring-sky-500 font-medium"
                >
                  {participants.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.research_participant_code} {p.display_name ? `(${p.display_name})` : ''} - Age: {p.age ?? 'N/A'}, Sex: {p.sex ?? 'F'}
                    </option>
                  ))}
                </select>
              ) : (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-amber-800 text-xs">
                  No participants found. Please click "+ Quick Add Participant" above to enroll a research code.
                </div>
              )}
            </div>

            {/* Step 2: Model Architecture Selection */}
            <div className="pt-2 border-t border-slate-100">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block mb-2">
                2. Select Trained Model Pipeline
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setModelType('sts_clinical')}
                  className={`p-3 rounded-lg border text-left text-xs transition-all ${
                    modelType === 'sts_clinical'
                      ? 'border-sky-600 bg-sky-50/60 ring-2 ring-sky-500/20'
                      : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <div className="font-bold text-slate-900 flex items-center justify-between">
                    <span>STS Clinical Model</span>
                    <span className="text-[10px] bg-sky-200 text-sky-800 px-1.5 py-0.2 rounded font-semibold">94.4%</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    TSH, FT3, FT4, Anti-TPO, Visfatin, IL-6, Lipids & CBC (User Dataset)
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => setModelType('uci_benchmark')}
                  className={`p-3 rounded-lg border text-left text-xs transition-all ${
                    modelType === 'uci_benchmark'
                      ? 'border-sky-600 bg-sky-50/60 ring-2 ring-sky-500/20'
                      : 'border-slate-200 hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <div className="font-bold text-slate-900 flex items-center justify-between">
                    <span>UCI Benchmark</span>
                    <span className="text-[10px] bg-teal-200 text-teal-800 px-1.5 py-0.2 rounded font-semibold">99.1%</span>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Standard Garavan Institute 29-feature benchmark
                  </p>
                </button>
              </div>
            </div>

            {/* Presets Bar */}
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 flex flex-wrap items-center gap-2 text-xs">
              <span className="text-slate-500 font-medium text-[11px] flex items-center gap-1">
                <FlaskConical className="h-3.5 w-3.5 text-slate-400" />
                Clinical Case Presets:
              </span>
              <button
                type="button"
                onClick={() => loadPreset('hypo')}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded text-[11px] font-semibold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
              >
                Case A: Primary Hypothyroid
              </button>
              <button
                type="button"
                onClick={() => loadPreset('autoimmune')}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded text-[11px] font-semibold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
              >
                Case B: Autoimmune (High Anti-TPO)
              </button>
              <button
                type="button"
                onClick={() => loadPreset('normal')}
                className="px-2.5 py-1 bg-white border border-slate-200 rounded text-[11px] font-semibold text-slate-700 hover:bg-slate-100 transition-all shadow-2xs"
              >
                Case C: Euthyroid Normal
              </button>
            </div>

            {/* Step 3: Clinical Parameters Form */}
            <div className="space-y-4 pt-2 border-t border-slate-100">
              <label className="text-xs font-bold text-slate-700 uppercase tracking-wider block">
                3. Clinical & Laboratory Measurements
              </label>

              {modelType === 'sts_clinical' ? (
                <div className="space-y-4 text-xs">
                  {/* Thyroid Panel */}
                  <div className="p-3 bg-sky-50/40 rounded-lg border border-sky-100">
                    <h3 className="font-bold text-slate-900 text-xs mb-3 flex items-center justify-between">
                      <span>Thyroid Hormones & Autoantibodies</span>
                      <span className="text-[10px] text-sky-700 font-medium">Primary Discriminators</span>
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div>
                        <label className="block text-[11px] font-medium text-slate-700 mb-1">
                          TSH <span className="text-slate-400 font-normal">(uIU/mL)</span>
                        </label>
                        <input
                          type="number"
                          step="0.001"
                          required
                          value={stsForm.TSH}
                          onChange={(e) => setStsForm({ ...stsForm, TSH: parseFloat(e.target.value) || 0 })}
                          className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                        />
                        <span className="text-[10px] text-slate-500">Ref: 0.40 - 4.50</span>
                      </div>

                      <div>
                        <label className="block text-[11px] font-medium text-slate-700 mb-1">
                          Anti-TPO <span className="text-slate-400 font-normal">(IU/mL)</span>
                        </label>
                        <input
                          type="number"
                          step="0.1"
                          required
                          value={stsForm.Anti_tpo}
                          onChange={(e) => setStsForm({ ...stsForm, Anti_tpo: parseFloat(e.target.value) || 0 })}
                          className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                        />
                        <span className="text-[10px] text-slate-500">Normal &lt; 34.0</span>
                      </div>

                      <div>
                        <label className="block text-[11px] font-medium text-slate-700 mb-1">
                          Free T4 <span className="text-slate-400 font-normal">(ng/dL)</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          value={stsForm.FT4}
                          onChange={(e) => setStsForm({ ...stsForm, FT4: parseFloat(e.target.value) || 0 })}
                          className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                        />
                        <span className="text-[10px] text-slate-500">Ref: 0.80 - 1.80</span>
                      </div>

                      <div>
                        <label className="block text-[11px] font-medium text-slate-700 mb-1">
                          Free T3 <span className="text-slate-400 font-normal">(pg/mL)</span>
                        </label>
                        <input
                          type="number"
                          step="0.01"
                          required
                          value={stsForm.FT3}
                          onChange={(e) => setStsForm({ ...stsForm, FT3: parseFloat(e.target.value) || 0 })}
                          className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                        />
                        <span className="text-[10px] text-slate-500">Ref: 2.00 - 4.40</span>
                      </div>
                    </div>
                  </div>

                  {/* Demographics & Vitals */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Age (Years)</label>
                      <input
                        type="number"
                        value={stsForm.AGE}
                        onChange={(e) => setStsForm({ ...stsForm, AGE: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Sex</label>
                      <select
                        value={stsForm.SEX}
                        onChange={(e) => setStsForm({ ...stsForm, SEX: e.target.value })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs"
                      >
                        <option value="F">Female (F)</option>
                        <option value="M">Male (M)</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">BMI (kg/m²)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={stsForm.bmi}
                        onChange={(e) => setStsForm({ ...stsForm, bmi: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Duration (Yrs)</label>
                      <input
                        type="number"
                        step="0.5"
                        value={stsForm.DURATION}
                        onChange={(e) => setStsForm({ ...stsForm, DURATION: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                  </div>

                  {/* Inflammatory & Adipokines */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">
                        Visfatin <span className="text-slate-400 font-normal">(ng/mL)</span>
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={stsForm.Visfatin}
                        onChange={(e) => setStsForm({ ...stsForm, Visfatin: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">
                        IL-6 <span className="text-slate-400 font-normal">(pg/mL)</span>
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={stsForm.IL6}
                        onChange={(e) => setStsForm({ ...stsForm, IL6: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">
                        Thyroglobulin <span className="text-slate-400 font-normal">(ng/mL)</span>
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        value={stsForm.Thyroglobulin}
                        onChange={(e) => setStsForm({ ...stsForm, Thyroglobulin: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">
                        FBS <span className="text-slate-400 font-normal">(mg/dL)</span>
                      </label>
                      <input
                        type="number"
                        value={stsForm.FBS}
                        onChange={(e) => setStsForm({ ...stsForm, FBS: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                  </div>

                  {/* Lipids & CBC */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Total Chol</label>
                      <input
                        type="number"
                        value={stsForm.TCHOL}
                        onChange={(e) => setStsForm({ ...stsForm, TCHOL: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Triglycerides</label>
                      <input
                        type="number"
                        value={stsForm.TGL}
                        onChange={(e) => setStsForm({ ...stsForm, TGL: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Hemoglobin</label>
                      <input
                        type="number"
                        step="0.1"
                        value={stsForm.HB}
                        onChange={(e) => setStsForm({ ...stsForm, HB: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Platelets</label>
                      <input
                        type="number"
                        value={stsForm.PLT}
                        onChange={(e) => setStsForm({ ...stsForm, PLT: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-slate-50 border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                /* UCI Benchmark Model Form */
                <div className="space-y-4 text-xs">
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">TSH (uIU/mL)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={uciForm.TSH}
                        onChange={(e) => setUciForm({ ...uciForm, TSH: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">FTI (Index)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={uciForm.FTI}
                        onChange={(e) => setUciForm({ ...uciForm, FTI: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">Total T4 (TT4)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={uciForm.TT4}
                        onChange={(e) => setUciForm({ ...uciForm, TT4: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-medium text-slate-700 mb-1">T4U (Ratio)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={uciForm.T4U}
                        onChange={(e) => setUciForm({ ...uciForm, T4U: parseFloat(e.target.value) || 0 })}
                        className="w-full bg-white border border-slate-300 rounded p-1.5 text-xs font-mono"
                      />
                    </div>
                  </div>

                  {/* Boolean indicators */}
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="text-[11px] font-bold text-slate-700 block mb-2">Clinical History Flags</span>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {[
                        { key: 'on_thyroxine', label: 'On Thyroxine' },
                        { key: 'thyroid_surgery', label: 'Thyroid Surgery' },
                        { key: 'I131_treatment', label: 'I131 Radiotherapy' },
                        { key: 'query_hypothyroid', label: 'Query Hypothyroid' },
                        { key: 'query_hyperthyroid', label: 'Query Hyperthyroid' },
                        { key: 'sick', label: 'Concurrent Illness' },
                        { key: 'pregnant', label: 'Pregnant' },
                        { key: 'goitre', label: 'Goitre Present' },
                        { key: 'tumor', label: 'Thyroid Tumor' },
                      ].map((flag) => (
                        <label key={flag.key} className="flex items-center space-x-2 text-[11px] text-slate-700">
                          <input
                            type="checkbox"
                            checked={(uciForm as any)[flag.key]}
                            onChange={(e) => setUciForm({ ...uciForm, [flag.key]: e.target.checked })}
                            className="rounded border-slate-300 text-sky-600 focus:ring-sky-500"
                          />
                          <span>{flag.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">
                Connected directly to loaded DecisionTree v1.0.0 artifact
              </span>
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold px-6 py-3 rounded-lg shadow-sm transition-all disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Evaluating Decision Path...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4" />
                    <span>Execute Decision Tree Prediction</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Panel: Results & Explainability (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {result ? (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
              {/* Header Result */}
              <div className="pb-4 border-b border-slate-100">
                <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                  <span>Record ID: #{result.id.slice(0, 8)}</span>
                  <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded">
                    Persisted in Database
                  </span>
                </div>
                <h3 className="text-xs uppercase tracking-wider text-slate-400 font-semibold mt-2">
                  Model Predicted Classification
                </h3>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-xl font-bold text-slate-900 tracking-tight">
                    {result.predicted_class}
                  </span>
                </div>
                <p className="text-xs text-slate-600 mt-2 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  {getClinicalDescription(result.predicted_class)}
                </p>
              </div>

              {/* Model Estimated Probabilities */}
              <div>
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center justify-between">
                  <span>Model Estimated Probabilities</span>
                  <span className="text-[10px] text-slate-400 font-normal">Decision Tree Leaf Dist</span>
                </h4>
                <div className="space-y-2.5">
                  {Object.entries(result.class_probabilities || {}).map(([cls, prob]) => {
                    const pct = Math.round(prob * 100);
                    const isWinner = cls === result.predicted_class;
                    return (
                      <div key={cls} className="space-y-1">
                        <div className="flex justify-between text-xs font-medium">
                          <span className={isWinner ? 'text-sky-700 font-bold' : 'text-slate-600'}>{cls}</span>
                          <span className="font-mono text-slate-700">{pct}%</span>
                        </div>
                        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              isWinner ? 'bg-sky-600' : 'bg-slate-300'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Explainability Decision Path Rules */}
              <div className="pt-2 border-t border-slate-100">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <Layers className="h-4 w-4 text-sky-600" />
                  <span>Decision Path Trace (Explainability)</span>
                </h4>
                <p className="text-[11px] text-slate-500 mb-2">
                  Feature thresholds traversed by the fitted decision tree to reach this leaf:
                </p>
                <div className="space-y-1.5 bg-slate-900 text-slate-200 p-3 rounded-lg text-[11px] font-mono overflow-x-auto">
                  {result.explanation_rules && result.explanation_rules.length > 0 ? (
                    result.explanation_rules.map((rule, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <span className="text-sky-400 select-none">[{idx + 1}]</span>
                        <span>{rule}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-400">Direct leaf assignment.</span>
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="pt-2 border-t border-slate-100 flex items-center justify-between no-print">
                <button
                  type="button"
                  onClick={() => window.print()}
                  className="inline-flex items-center space-x-1.5 text-xs text-slate-700 bg-slate-100 hover:bg-slate-200 font-semibold px-3 py-2 rounded-lg transition-all"
                >
                  <Printer className="h-3.5 w-3.5" />
                  <span>Print Report</span>
                </button>
                <button
                  type="button"
                  onClick={() => onNavigate('history')}
                  className="text-xs text-sky-600 hover:text-sky-800 font-semibold"
                >
                  View in Audit History →
                </button>
              </div>
            </div>
          ) : (
            /* Standby Card */
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex flex-col items-center justify-center text-center min-h-[380px] space-y-3">
              <div className="h-14 w-14 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center">
                <BrainCircuit className="h-7 w-7" />
              </div>
              <h3 className="font-bold text-slate-800 text-sm">Prediction Engine Ready</h3>
              <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
                Choose a participant, verify laboratory parameters on the left, and submit to inspect genuine decision paths and confidence metrics.
              </p>
              <div className="pt-2 flex flex-col gap-1 text-[11px] text-slate-400">
                <span>✓ Trained Decision Tree Classifier (scikit-learn)</span>
                <span>✓ Direct Tree Path Introspection</span>
                <span>✓ Relational Record Persistence</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Quick Add Participant Modal */}
      {showQuickParticipantModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <h3 className="font-bold text-base text-slate-900">Enroll Research Participant</h3>
            <p className="text-xs text-slate-500">
              Generate a pseudonymous code for privacy-preserving research records.
            </p>
            <form onSubmit={handleQuickCreateParticipant} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Participant Code *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. THYRO-PART-005"
                  value={newCode}
                  onChange={(e) => setNewCode(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs font-mono"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Pseudonym / Initials (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Subject Epsilon"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Age</label>
                  <input
                    type="number"
                    value={newAge}
                    onChange={(e) => setNewAge(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Sex</label>
                  <select
                    value={newSex}
                    onChange={(e) => setNewSex(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                  >
                    <option value="F">Female</option>
                    <option value="M">Male</option>
                  </select>
                </div>
              </div>
              <div className="p-3 bg-slate-50 rounded border border-slate-200 text-[11px] text-slate-600 flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 flex-shrink-0" />
                <span>Informed Research Consent confirmed in protocol.</span>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowQuickParticipantModal(false)}
                  className="px-3.5 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg shadow-xs"
                >
                  Save Participant
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
