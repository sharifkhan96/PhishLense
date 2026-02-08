import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle token refresh on 401
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return client(originalRequest);
        } catch (err) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export interface Threat {
  id: number;
  threat_type: 'email' | 'url' | 'text' | 'link';
  content: string;
  source: string;
  status: string;
  severity: 'low' | 'medium' | 'high' | 'critical' | '';
  ai_analysis: string;
  ai_explanation: string;
  risk_score: number | null;
  sandbox_executed: boolean;
  sandbox_results: any;
  actions_taken: string[];
  observations: string;
  recommendations: string;
  created_at: string;
  updated_at: string;
  analyzed_at: string | null;
  timeline_events: TimelineEvent[];
}

export interface TimelineEvent {
  id: number;
  event_type: string;
  description: string;
  timestamp: string;
  metadata: any;
}

export interface ThreatAnalysisRequest {
  threat_type: 'email' | 'url' | 'text' | 'link';
  content: string;
  source?: string;
  execute_in_sandbox?: boolean;
}

export interface TrafficEvent {
  id: number;
  source_ip: string;
  destination_ip: string | null;
  port: number | null;
  payload: string;
  payload_type: string;
  date_time: string;
  ml_prediction: string;
  ml_confidence: number | null;
  ai_analysis: string;
  ai_explanation: string;
  status: string;
  classification: 'normal' | 'malicious' | 'unknown';
  severity: 'low' | 'medium' | 'high' | 'critical' | '';
  risk_score: number | null;
  actions_taken: string[];
  sandbox_executed: boolean;
  sandbox_results: any;
  recommendations: string;
  organization: string;
  created_at: string;
  updated_at: string;
  analyzed_at: string | null;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  password: string;
  password2: string;
  email: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthResponse {
  user: User;
  access: string;
  refresh: string;
  message?: string;
}

export const threatAPI = {
  getAll: () => client.get<Threat[]>('/threats/'),
  getById: (id: number) => client.get<Threat>(`/threats/${id}/`),
  create: (data: ThreatAnalysisRequest) => client.post<Threat>('/threats/', data),
  execute: (id: number) => client.post<Threat>(`/threats/${id}/execute/`),
  reanalyze: (id: number) => client.post<Threat>(`/threats/${id}/reanalyze/`),
  getStats: () => client.get('/threats/stats/'),
};

export const authAPI = {
  register: (data: RegisterRequest) => client.post<AuthResponse>('/auth/register/', data),
  login: (data: LoginRequest) => client.post<AuthResponse>('/auth/login/', data),
  getCurrentUser: () => client.get<User>('/auth/me/'),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const trafficAPI = {
  getAll: (classification?: string) => {
    const params = classification ? { classification } : {};
    return client.get<PaginatedResponse<TrafficEvent>>('/traffic/', { params });
  },
  getById: (id: number) => client.get<TrafficEvent>(`/traffic/${id}/`),
  receive: (data: any) => client.post<TrafficEvent>('/traffic/receive/', data),
  getStats: () => client.get('/traffic/stats/'),
  executeSandbox: (id: number) => client.post<TrafficEvent>(`/traffic/${id}/execute_sandbox/`),
};

export interface MediaAnalysis {
  id: number;
  media_type: 'text' | 'image' | 'video' | 'audio';
  media_type_display: string;
  file: string | null;
  file_url: string | null;
  text_content: string;
  what_received: string;
  what_did: string;
  what_to_do_next: string;
  ai_analysis: string;
  risk_score: number | null;
  is_threat: boolean;
  threat_details: any;
  status: string;
  error_message: string;
  organization: string;
  created_at: string;
  updated_at: string;
  analyzed_at: string | null;
}

export interface MediaAnalysisRequest {
  media_type: 'text' | 'image' | 'video' | 'audio';
  text_content?: string;
  file_url?: string;
  organization?: string;
  file?: File;
}

export const mediaAPI = {
  getAll: () => client.get<PaginatedResponse<MediaAnalysis>>('/media/'),
  getById: (id: number) => client.get<MediaAnalysis>(`/media/${id}/`),
  analyze: (data: FormData) => client.post<MediaAnalysis>('/media/', data, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  getRateLimitStatus: () => client.get('/media/rate_limit_status/'),
};

export default client;

