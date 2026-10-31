import { apiClient } from './apiClient';

export interface UserPreferencesPayload {
  locale?: string;
  timezone?: string;
  text_size?: number; // 100, 125, 150
  theme?: string; // light, calm_dark
  high_contrast?: boolean;
  phone?: string;
}

export interface UserOut {
  id: number;
  email: string;
  phone?: string | null;
  full_name: string;
  role: string;
  is_active: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  locale?: string | null;
  timezone?: string | null;
  text_size: number;
  theme: string;
  high_contrast: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface PasswordChangePayload {
  current_password: string;
  new_password: string;
}

export const userService = {
  /**
   * Update preferences for current user (locale, text_size, theme, high_contrast)
   */
  async updatePreferences(prefs: UserPreferencesPayload): Promise<UserOut> {
    const response = await apiClient.patch<UserOut>('/users/me', prefs);
    return response.data;
  },

  /**
   * Change password for current user
   */
  async changePassword(data: PasswordChangePayload): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>('/users/me/change-password', data);
    return response.data;
  },

  /**
   * Get user by ID (admin only)
   */
  async getUser(id: number): Promise<UserOut> {
    const response = await apiClient.get<UserOut>(`/users/${id}`);
    return response.data;
  },
};

