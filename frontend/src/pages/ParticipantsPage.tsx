import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Plus,
  Trash2,
  FileText,
  Calendar,
  CheckCircle2,
  X,
  History,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';
import { ResearchParticipant, Prediction } from '../types';

interface ParticipantsPageProps {
  onNavigate: (tab: string) => void;
}

export const ParticipantsPage: React.FC<ParticipantsPageProps> = ({ onNavigate }) => {
  const [participants, setParticipants] = useState<ResearchParticipant[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New participant form
  const [code, setCode] = useState('');
  const [name, setName] = useState('');
  const [age, setAge] = useState<number>(45);
  const [sex, setSex] = useState('F');
  const [notes, setNotes] = useState('');

  // Selected participant detail modal
  const [selectedParticipant, setSelectedParticipant] = useState<ResearchParticipant | null>(null);
  const [participantPredictions, setParticipantPredictions] = useState<Prediction[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    fetchParticipants();
  }, [search]);

  const fetchParticipants = async () => {
    try {
      setLoading(true);
      const data = await api.getParticipants(search || undefined);
      setParticipants(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!code.trim()) return;

    try {
      await api.createParticipant({
        research_participant_code: code.trim(),
        display_name: name.trim() || undefined,
        age: Number(age) || undefined,
        sex,
        consent_status: true,
        notes: notes.trim() || undefined,
      });
      setShowAddModal(false);
      setCode('');
      setName('');
      setNotes('');
      fetchParticipants();
    } catch (err: any) {
      alert(`Error enrolling participant: ${err.message}`);
    }
  };

  const handleDelete = async (id: string, code: string) => {
    if (!window.confirm(`Are you sure you want to delete participant ${code}? All associated predictions will also be deleted according to retention policy.`)) {
      return;
    }
    try {
      await api.deleteParticipant(id);
      fetchParticipants();
    } catch (err: any) {
      alert(`Error deleting participant: ${err.message}`);
    }
  };

  const handleViewDetails = async (p: ResearchParticipant) => {
    setSelectedParticipant(p);
    setLoadingHistory(true);
    try {
      const preds = await api.getPredictions({ participant_id: p.id });
      setParticipantPredictions(preds);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Participant Registry</span>
            <span className="text-xs bg-slate-200 text-slate-800 font-semibold px-2 py-0.5 rounded-full">
              {participants.length} Active Subjects
            </span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Maintain de-identified research participant cohorts and trace individual prediction histories.
          </p>
        </div>
        <div>
          <button
            onClick={() => setShowAddModal(true)}
            className="inline-flex items-center space-x-2 bg-sky-600 hover:bg-sky-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-all"
          >
            <Plus className="h-4 w-4" />
            <span>Enroll Participant</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-3">
        <Search className="h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by participant code (e.g. THYRO-PART-001) or pseudonym..."
          className="w-full text-xs bg-transparent focus:outline-none text-slate-800 placeholder-slate-400"
        />
      </div>

      {/* Participants Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400 text-xs">Loading registry...</div>
        ) : participants.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-b border-slate-200 text-[11px]">
                <tr>
                  <th className="py-3 px-4">Participant Code</th>
                  <th className="py-3 px-4">Display / Pseudonym</th>
                  <th className="py-3 px-4">Demographics</th>
                  <th className="py-3 px-4">Consent</th>
                  <th className="py-3 px-4">Prediction Count</th>
                  <th className="py-3 px-4">Enrolled Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {participants.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-semibold text-slate-900">
                      {p.research_participant_code}
                    </td>
                    <td className="py-3 px-4 text-slate-600">{p.display_name || '—'}</td>
                    <td className="py-3 px-4 text-slate-600 font-mono text-[11px]">
                      {p.age ? `${p.age} yrs` : 'N/A'}, {p.sex || 'F'}
                    </td>
                    <td className="py-3 px-4">
                      {p.consent_status ? (
                        <span className="inline-flex items-center gap-1 text-emerald-700 font-medium text-[11px]">
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                          Consented
                        </span>
                      ) : (
                        <span className="text-amber-700 text-[11px]">Pending</span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono font-medium text-slate-700">
                      {p.prediction_count || 0} records
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(p.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3 px-4 text-right space-x-2">
                      <button
                        onClick={() => handleViewDetails(p)}
                        className="text-sky-600 hover:text-sky-800 font-semibold"
                      >
                        History
                      </button>
                      <button
                        onClick={() => handleDelete(p.id, p.research_participant_code)}
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
            No participants found matching your search.
          </div>
        )}
      </div>

      {/* Add Participant Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-base text-slate-900">Enroll Research Participant</h3>
              <button
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Participant Code *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. THYRO-PART-006"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs font-mono"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Display / Pseudonym (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Participant Zeta"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Age (Years)</label>
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => setAge(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Biological Sex</label>
                  <select
                    value={sex}
                    onChange={(e) => setSex(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                  >
                    <option value="F">Female (F)</option>
                    <option value="M">Male (M)</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Clinical Notes (Optional)</label>
                <textarea
                  rows={2}
                  placeholder="Baseline presentation or inclusion criteria details..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded p-2 text-xs"
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
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

      {/* Participant History Modal */}
      {selectedParticipant && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-2xl w-full p-6 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <div>
                <h3 className="font-bold text-base text-slate-900">
                  {selectedParticipant.research_participant_code}
                </h3>
                <p className="text-xs text-slate-500">
                  {selectedParticipant.display_name ? `${selectedParticipant.display_name} • ` : ''}
                  Age: {selectedParticipant.age ?? 'N/A'}, Sex: {selectedParticipant.sex ?? 'F'}
                </p>
              </div>
              <button
                onClick={() => setSelectedParticipant(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {loadingHistory ? (
              <div className="p-8 text-center text-slate-400 text-xs">Loading prediction history...</div>
            ) : participantPredictions.length > 0 ? (
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                  Historical Decision Tree Predictions ({participantPredictions.length})
                </h4>
                {participantPredictions.map((pred) => (
                  <div key={pred.id} className="p-4 rounded-lg border border-slate-200 bg-slate-50/60 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-slate-800">{pred.model_name} (v{pred.model_version})</span>
                      <span className="text-[11px] font-mono text-slate-500">
                        {new Date(pred.prediction_timestamp).toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-sky-800 bg-sky-100 px-2.5 py-0.5 rounded-full">
                        {pred.predicted_class}
                      </span>
                    </div>
                    {pred.explanation_rules && pred.explanation_rules.length > 0 && (
                      <div className="text-[11px] font-mono bg-slate-900 text-slate-300 p-2.5 rounded mt-2 space-y-1">
                        {pred.explanation_rules.map((r, i) => (
                          <div key={i}>• {r}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-slate-400 text-xs">
                No predictions recorded for this participant yet.
              </div>
            )}

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setSelectedParticipant(null)}
                className="px-4 py-2 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
