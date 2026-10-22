import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  CheckCircle2,
  AlertTriangle,
  GitBranch,
  Layers,
  FileText,
  Download,
  Info,
  Calendar,
  ShieldCheck,
  BrainCircuit
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { api } from '../services/api';
import { ModelMetrics } from '../types';

export const ModelPerformancePage: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<'sts_clinical' | 'uci_benchmark'>('sts_clinical');
  const [metrics, setMetrics] = useState<ModelMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, [selectedModel]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const data = await api.getModelMetrics(selectedModel);
      setMetrics(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const featureChartData = metrics?.feature_importances
    ? metrics.feature_importances.slice(0, 8).map((f) => ({
        feature: f.feature,
        importance: Math.round(f.importance * 100),
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Model Scientific Performance</span>
            <span className="text-xs bg-emerald-100 text-emerald-800 font-semibold px-2.5 py-0.5 rounded-full">
              Held-Out Test Set Verified
            </span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Audited scikit-learn Decision Tree metrics. Strictly isolated validation partitions with zero target leakage.
          </p>
        </div>

        {/* Model Switcher Buttons */}
        <div className="inline-flex p-1 bg-slate-200/80 rounded-xl space-x-1 text-xs">
          <button
            onClick={() => setSelectedModel('sts_clinical')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              selectedModel === 'sts_clinical'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            STS Clinical Model (User Dataset)
          </button>
          <button
            onClick={() => setSelectedModel('uci_benchmark')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              selectedModel === 'uci_benchmark'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            UCI Benchmark Model (allhypo)
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading performance evaluation...</div>
      ) : metrics ? (
        <div className="space-y-6">
          {/* Top Performance Metric Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Held-Out Test Accuracy
              </span>
              <div className="text-2xl font-bold text-slate-900 mt-1">
                {(metrics.metrics.accuracy * 100).toFixed(2)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                N={metrics.dataset.test_samples} test subjects
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Balanced Accuracy
              </span>
              <div className="text-2xl font-bold text-slate-900 mt-1">
                {(metrics.metrics.balanced_accuracy * 100).toFixed(2)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Accounts for class imbalance
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Macro-Averaged F1
              </span>
              <div className="text-2xl font-bold text-slate-900 mt-1">
                {(metrics.metrics.macro_f1 * 100).toFixed(2)}%
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                Harmonic mean across classes
              </p>
            </div>

            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Tree Complexity
              </span>
              <div className="text-2xl font-bold text-slate-900 mt-1">
                Depth {metrics.tree_structure.depth}
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                {metrics.tree_structure.n_leaves} Leaves (Pruned for generalization)
              </p>
            </div>
          </div>

          {/* Confusion Matrix & Feature Importances */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Real Confusion Matrix Table */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  Real Held-Out Confusion Matrix
                </h3>
                <p className="text-xs text-slate-500">
                  Rows: True Ground-Truth Label • Columns: Model Predicted Label
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-center text-xs border border-slate-200">
                  <thead className="bg-slate-100 text-slate-600 font-bold text-[11px]">
                    <tr>
                      <th className="p-2 border border-slate-200 text-left bg-slate-50">Actual \ Predicted</th>
                      {metrics.metrics.confusion_matrix.labels.map((lbl) => (
                        <th key={lbl} className="p-2 border border-slate-200 max-w-[100px] truncate" title={lbl}>
                          {lbl}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.metrics.confusion_matrix.matrix.map((row, rowIdx) => {
                      const actualLabel = metrics.metrics.confusion_matrix.labels[rowIdx];
                      return (
                        <tr key={actualLabel}>
                          <td className="p-2 border border-slate-200 font-semibold text-left bg-slate-50 text-[11px] truncate max-w-[120px]" title={actualLabel}>
                            {actualLabel}
                          </td>
                          {row.map((count, colIdx) => {
                            const isDiagonal = rowIdx === colIdx;
                            return (
                              <td
                                key={colIdx}
                                className={`p-2 border border-slate-200 font-mono font-bold ${
                                  isDiagonal
                                    ? count > 0 ? 'bg-emerald-50 text-emerald-800' : 'bg-slate-50 text-slate-400'
                                    : count > 0 ? 'bg-rose-50 text-rose-700' : 'text-slate-300'
                                }`}
                              >
                                {count}
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <p className="text-[11px] text-slate-400 italic">
                Evaluated on {metrics.dataset.test_samples} independent held-out samples.
              </p>
            </div>

            {/* Feature Importance Bar Chart */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  Top Feature Importances (Gini Impurity)
                </h3>
                <p className="text-xs text-slate-500">
                  Relative contribution to decision tree branch splits
                </p>
              </div>

              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={featureChartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 50, bottom: 5 }}
                  >
                    <XAxis type="number" unit="%" tick={{ fontSize: 11 }} />
                    <YAxis dataKey="feature" type="category" tick={{ fontSize: 10 }} width={70} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0F172A', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                      formatter={(val: any) => [`${val}%`, 'Importance']}
                    />
                    <Bar dataKey="importance" fill="#0284C7" radius={[0, 4, 4, 0]}>
                      {featureChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={index === 0 ? '#0284C7' : '#0D9488'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Per-Class Evaluation Metrics Table */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-200">
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                Per-Class Performance Metrics
              </h3>
              <p className="text-xs text-slate-500">
                Precision, Recall (Sensitivity), and F1-Score per diagnostic category
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-500 font-semibold border-b border-slate-200 text-[11px] uppercase">
                  <tr>
                    <th className="py-3 px-4">Class Label</th>
                    <th className="py-3 px-4">Precision</th>
                    <th className="py-3 px-4">Recall (Sensitivity)</th>
                    <th className="py-3 px-4">F1-Score</th>
                    <th className="py-3 px-4">Test Support (N)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {Object.entries(metrics.metrics.per_class).map(([cls, m]) => (
                    <tr key={cls} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-sans font-bold text-slate-900">{cls}</td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{(m.precision * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 font-semibold text-slate-700">{(m.recall * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 font-bold text-sky-700">{(m.f1_score * 100).toFixed(1)}%</td>
                      <td className="py-3 px-4 text-slate-500">{m.support} samples</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Documented Limitations */}
          <div className="bg-slate-900 text-slate-300 rounded-xl p-6 space-y-3">
            <div className="flex items-center space-x-2 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              <h3 className="font-bold text-sm text-white">Scientifically Documented Model Limitations</h3>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-400 list-disc list-inside">
              {metrics.limitations.map((lim, idx) => (
                <li key={idx} className="leading-relaxed">
                  {lim}
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </div>
  );
};
