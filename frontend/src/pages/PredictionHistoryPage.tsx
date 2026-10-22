import React, { useState, useEffect } from 'react';
import {
  History,
  Search,
  Filter,
  Download,
  Trash2,
  Printer,
  X,
  Layers,
  FileSpreadsheet,
  CheckCircle2,
  BrainCircuit
} from 'lucide-react';
import { api } from '../services/api';
import { Prediction } from '../types';

export const PredictionHistoryPage: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedPrediction, setSelectedPrediction] = useState<Prediction | null>(null);

  useEffect(() => {
    fetchPredictions();
  }, [search, selectedClass]);

  const fetchPredictions = async () => {
    try {
      setLoading(true);
      const data = await api.getPredictions({
        search: search || undefined,
        predicted_class: selectedClass || undefined,
      });
      setPredictions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Delete this prediction record from the persistent database?')) return;
    try {
      await api.deletePrediction(id);
      fetchPredictions();
      if (selectedPrediction?.id === id) {
        setSelectedPrediction(null);
      }
    } catch (err: any) {
      alert(`Error deleting record: ${err.message}`);
    }
  };

  const uniqueClasses = Array.from(new Set(predictions.map((p) => p.predicted_class)));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Prediction Audit Trail</span>
            <span className="text-xs bg-slate-200 text-slate-800 font-semibold px-2.5 py-0.5 rounded-full font-mono">
              {predictions.length} Saved Records
            </span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Complete, immutable log of Decision Tree inference calls, model versions, and feature inputs.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <a
            href={api.getExportUrl()}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center space-x-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg transition-all"
          >
            <Download className="h-4 w-4" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter by participant code or disease classification..."
            className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-700 w-full sm:w-48"
          >
            <option value="">All Classification Labels</option>
            {uniqueClasses.map((cls) => (
              <option key={cls} value={cls}>
                {cls}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading audit trail...</div>
        ) : predictions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200 text-[11px]">
                <tr>
                  <th className="py-3 px-4">Record ID</th>
                  <th className="py-3 px-4">Participant Code</th>
                  <th className="py-3 px-4">Model Applied</th>
                  <th className="py-3 px-4">Predicted Condition</th>
                  <th className="py-3 px-4">Inference Timestamp</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {predictions.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-medium text-slate-500 text-[11px]">
                      #{p.id.slice(0, 8)}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-900">
                      {p.participant_code || 'N/A'}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {p.model_name} <span className="text-[10px] text-slate-400">v{p.model_version}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-sky-100 text-sky-800">
                        {p.predicted_class}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(p.prediction_timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => setSelectedPrediction(p)}
                        className="text-sky-600 hover:text-sky-800 font-semibold"
                      >
                        Inspect
                      </button>
                      <button
                        onClick={() => handleDelete(p.id)}
                        className="text-red-500 hover:text-red-700 font-semibold ml-2"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-slate-400 text-xs">
            No prediction records found matching your filters.
          </div>
        )}
      </div>

      {/* Inspect Prediction Modal */}
      {selectedPrediction && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-2xl w-full p-6 space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div>
                <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 block">
                  Prediction Audit Dossier #{selectedPrediction.id}
                </span>
                <h3 className="font-bold text-lg text-slate-900">
                  {selectedPrediction.participant_code}
                </h3>
              </div>
              <button
                onClick={() => setSelectedPrediction(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Classification & Confidence */}
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500 font-medium">Model Output</span>
                <span className="text-xs font-mono text-slate-400">
                  {new Date(selectedPrediction.prediction_timestamp).toLocaleString()}
                </span>
              </div>
              <div className="text-lg font-bold text-slate-900">
                {selectedPrediction.predicted_class}
              </div>
              <div className="text-xs text-slate-500">
                Model: {selectedPrediction.model_name} (Artifact v{selectedPrediction.model_version})
              </div>

              {/* Probabilities breakdown */}
              {selectedPrediction.class_probabilities && (
                <div className="pt-2 border-t border-slate-200 grid grid-cols-2 gap-2 text-xs">
                  {Object.entries(selectedPrediction.class_probabilities).map(([c, p]) => (
                    <div key={c} className="flex justify-between font-mono bg-white p-1.5 rounded border border-slate-100">
                      <span className="text-slate-600 truncate mr-2">{c}:</span>
                      <span className="font-bold text-slate-800">{(p * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Decision Tree Explainability Path */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                <Layers className="h-4 w-4 text-sky-600" />
                <span>Decision Path Explanation (Decision Tree Leaves)</span>
              </h4>
              <div className="bg-slate-900 text-slate-300 p-3 rounded-lg text-xs font-mono space-y-1 overflow-x-auto">
                {selectedPrediction.explanation_rules && selectedPrediction.explanation_rules.length > 0 ? (
                  selectedPrediction.explanation_rules.map((rule, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <span className="text-sky-400">[{idx + 1}]</span>
                      <span>{rule}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-slate-400">No rule trace recorded.</span>
                )}
              </div>
            </div>

            {/* Submitted Laboratory Parameters */}
            <div>
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">
                Submitted Feature Inputs (Reproducibility Data)
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs font-mono">
                {selectedPrediction.submitted_feature_values &&
                  Object.entries(selectedPrediction.submitted_feature_values).map(([k, v]) => (
                    <div key={k} className="truncate">
                      <span className="text-slate-500">{k}: </span>
                      <span className="font-semibold text-slate-900">{String(v)}</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => window.print()}
                className="inline-flex items-center space-x-1.5 text-xs text-slate-700 bg-slate-100 hover:bg-slate-200 font-semibold px-3 py-2 rounded-lg"
              >
                <Printer className="h-3.5 w-3.5" />
                <span>Print Research Report</span>
              </button>
              <button
                type="button"
                onClick={() => setSelectedPrediction(null)}
                className="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-700 text-white rounded-lg"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
