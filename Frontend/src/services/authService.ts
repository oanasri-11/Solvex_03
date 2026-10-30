import { apiClient } from './apiClient';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in?: number;
}

export interface UserMe {
  id: number;
  email: string;
  phone?: string;
  full_name: string;
  role: 'doctor' | 'patient' | 'admin' | 'caregiver';
  is_active: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  locale?: string;
  timezone?: string;
  text_size: number;
  theme: string;
  high_contrast: boolean;
  created_at: string;
  linked_patients?: number[];
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
  phone: string;
  role: 'doctor' | 'patient';
  enrolment_code?: string;
}

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', {
      email,
      password,
    });
    const tokens = response.data;
    localStorage.setItem('rawd_access_token', tokens.access_token);
    localStorage.setItem('rawd_refresh_token', tokens.refresh_token);
    return tokens;
  },

  async getMe(): Promise<UserMe> {
    const response = await apiClient.get<UserMe>('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem('rawd_refresh_token');
    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken });
      }
    } catch {
      // Ignore logout backend error
    } finally {
      localStorage.removeItem('rawd_access_token');
      localStorage.removeItem('rawd_refresh_token');
    }
  },

  async register(payload: RegisterPayload) {
    const response = await apiClient.post('/auth/register', payload);
    return response.data;
  },

  async forgotPassword(email: string): Promise<{ message: string }> {
    const response = await apiClient.post('/auth/forgot-password', { email });
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!localStorage.getItem('rawd_access_token');
  },
};

