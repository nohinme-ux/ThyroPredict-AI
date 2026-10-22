import {
  ResearchParticipant,
  Prediction,
  OverviewStats,
  ModelMetrics,
  DatasetSummary,
  User
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('thyropredict_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('thyropredict_token', token);
    } else {
      localStorage.removeItem('thyropredict_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        let errorMsg = `API request failed with status ${response.status}`;
        try {
          const errData = await response.json();
          if (errData.detail) {
            errorMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch {
          // fallback
        }
        throw new Error(errorMsg);
      }

      if (response.status === 204) {
        return null as unknown as T;
      }

      return await response.json();
    } catch (err: any) {
      console.error(`[API Error] ${endpoint}:`, err);
      throw err;
    }
  }

  // --- Auth ---
  async login(email: string, password: string) {
    const res = await this.request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  // --- Overview ---
  async getOverviewStats(): Promise<OverviewStats> {
    return this.request<OverviewStats>('/overview/stats');
  }

  // --- Participants ---
  async getParticipants(search?: string): Promise<ResearchParticipant[]> {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return this.request<ResearchParticipant[]>(`/participants${query}`);
  }

  async getParticipant(id: string): Promise<ResearchParticipant> {
    return this.request<ResearchParticipant>(`/participants/${id}`);
  }

  async createParticipant(data: {
    research_participant_code: string;
    display_name?: string;
    age?: number;
    sex?: string;
    consent_status?: boolean;
    notes?: string;
  }): Promise<ResearchParticipant> {
    return this.request<ResearchParticipant>('/participants', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteParticipant(id: string): Promise<void> {
    return this.request<void>(`/participants/${id}`, {
      method: 'DELETE',
    });
  }

  // --- Predictions ---
  async getPredictions(params?: {
    participant_id?: string;
    model_name?: string;
    predicted_class?: string;
    search?: string;
  }): Promise<Prediction[]> {
    const urlParams = new URLSearchParams();
    if (params?.participant_id) urlParams.append('participant_id', params.participant_id);
    if (params?.model_name) urlParams.append('model_name', params.model_name);
    if (params?.predicted_class) urlParams.append('predicted_class', params.predicted_class);
    if (params?.search) urlParams.append('search', params.search);

    const query = urlParams.toString() ? `?${urlParams.toString()}` : '';
    return this.request<Prediction[]>(`/predictions${query}`);
  }

  async getPrediction(id: string): Promise<Prediction> {
    return this.request<Prediction>(`/predictions/${id}`);
  }

  async createPrediction(payload: {
    participant_id: string;
    model_type: 'sts_clinical' | 'uci_benchmark';
    sts_features?: Record<string, any>;
    uci_features?: Record<string, any>;
  }): Promise<Prediction> {
    return this.request<Prediction>('/predictions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async deletePrediction(id: string): Promise<void> {
    return this.request<void>(`/predictions/${id}`, {
      method: 'DELETE',
    });
  }

  // --- Models & Analytics ---
  async getModelInfo(): Promise<any> {
    return this.request('/model/info');
  }

  async getModelMetrics(modelId: 'sts_clinical' | 'uci_benchmark'): Promise<ModelMetrics> {
    return this.request<ModelMetrics>(`/model/metrics?model_id=${modelId}`);
  }

  // --- Dataset ---
  async getDatasetSummary(): Promise<DatasetSummary> {
    return this.request<DatasetSummary>('/dataset/summary');
  }

  getExportUrl(): string {
    return `${API_BASE}/research/export?anonymize=true`;
  }
}

export const api = new ApiService();
