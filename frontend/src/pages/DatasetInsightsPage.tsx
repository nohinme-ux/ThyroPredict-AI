import React, { useState, useEffect } from 'react';
import {
  Database,
  Search,
  BookOpen,
  Layers,
  FileSpreadsheet,
  CheckCircle2,
  ExternalLink,
  Table
} from 'lucide-react';
import { api } from '../services/api';
import { DatasetSummary } from '../types';

export const DatasetInsightsPage: React.FC = () => {
  const [summary, setSummary] = useState<DatasetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDataset, setSelectedDataset] = useState<'sts' | 'uci'>('sts');
  const [featureSearch, setFeatureSearch] = useState('');

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getDatasetSummary();
      setSummary(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const currentDict =
    selectedDataset === 'sts'
      ? summary?.dictionary?.sts_clinical_dataset
      : summary?.dictionary?.uci_benchmark_dataset;

  const filteredFeatures = currentDict?.features?.filter((f) =>
    f.name.toLowerCase().includes(featureSearch.toLowerCase()) ||
    f.description.toLowerCase().includes(featureSearch.toLowerCase())
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Dataset Exploration & Data Dictionary</span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Verified schemas, class taxonomies, normal reference ranges, and academic source attributions.
          </p>
        </div>

        {/* Dataset Switcher */}
        <div className="inline-flex p-1 bg-slate-200/80 rounded-xl space-x-1 text-xs">
          <button
            onClick={() => setSelectedDataset('sts')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              selectedDataset === 'sts'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            STS Clinical Study (269 Samples)
          </button>
          <button
            onClick={() => setSelectedDataset('uci')}
            className={`px-3 py-1.5 rounded-lg font-semibold transition-all ${
              selectedDataset === 'uci'
                ? 'bg-white text-slate-900 shadow-xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            UCI Benchmark (3,772 Samples)
          </button>
        </div>
      </div>

      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs">Loading dataset dictionary...</div>
      ) : currentDict ? (
        <div className="space-y-6">
          {/* Dataset Summary Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-100 pb-3">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-sky-600">
                  Dataset Profile
                </span>
                <h3 className="text-lg font-bold text-slate-900">{currentDict.title}</h3>
              </div>
              <div className="text-xs text-slate-500">
                Total Samples: <span className="font-bold text-slate-800">{currentDict.sample_count}</span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed">
              {currentDict.description}
            </p>

            <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 text-xs flex items-center justify-between">
              <div>
                <span className="font-bold text-slate-700">Source Attribution: </span>
                <span className="text-slate-600">{currentDict.source}</span>
              </div>
            </div>
          </div>

          {/* Class Definitions */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-3">
            <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
              Diagnostic Target Classes & Medical Definitions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(currentDict.classes || {}).map(([cls, desc]) => (
                <div key={cls} className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 space-y-1">
                  <span className="font-bold text-xs text-slate-900 block">{cls}</span>
                  <p className="text-xs text-slate-600 leading-relaxed">{desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Feature Dictionary with Search */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-4 p-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                  Feature Dictionary ({filteredFeatures.length} Parameters)
                </h3>
                <p className="text-xs text-slate-500">
                  Biological variables, measurement units, and standard physiological reference windows
                </p>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="h-4 w-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={featureSearch}
                  onChange={(e) => setFeatureSearch(e.target.value)}
                  placeholder="Search features..."
                  className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-slate-800"
                />
              </div>
            </div>

            <div className="overflow-x-auto border border-slate-200 rounded-lg">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 font-bold border-b border-slate-200 text-[11px] uppercase">
                  <tr>
                    <th className="py-3 px-4">Feature Name</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Unit</th>
                    <th className="py-3 px-4">Normal Reference Range</th>
                    <th className="py-3 px-4">Clinical Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredFeatures.map((f) => (
                    <tr key={f.name} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-mono font-bold text-slate-900">{f.name}</td>
                      <td className="py-3 px-4 text-slate-600">
                        <span className="text-[10px] uppercase font-semibold bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                          {f.type}
                        </span>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-600">{f.unit || '—'}</td>
                      <td className="py-3 px-4 font-mono text-emerald-700 font-semibold">
                        {f.normal_range || '—'}
                      </td>
                      <td className="py-3 px-4 text-slate-600 leading-relaxed max-w-xs">{f.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
