import { describe, it, expect, beforeEach, vi } from 'vitest';
import { authService } from '../services/authService';
import { apiClient } from '../services/apiClient';

describe('authService Unit Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('login stores tokens in localStorage and returns response', async () => {
    const mockTokens = {
      access_token: 'acc_123',
      refresh_token: 'ref_123',
      token_type: 'bearer',
      expires_in: 1800,
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: mockTokens });

    const result = await authService.login('dr.karim@clinic.com', 'Password123!');

    expect(apiClient.post).toHaveBeenCalledWith('/auth/login', {
      email: 'dr.karim@clinic.com',
      password: 'Password123!',
    });
    expect(result).toEqual(mockTokens);
    expect(localStorage.getItem('rawd_access_token')).toBe('acc_123');
    expect(localStorage.getItem('rawd_refresh_token')).toBe('ref_123');
  });

  it('getMe retrieves current user profile', async () => {
    const mockUser = {
      id: 1,
      email: 'dr.karim@clinic.com',
      full_name: 'Dr. Karim B.',
      role: 'doctor',
      is_active: true,
      text_size: 100,
      theme: 'light',
      high_contrast: false,
    };
    vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockUser });

    const result = await authService.getMe();
    expect(apiClient.get).toHaveBeenCalledWith('/auth/me');
    expect(result.email).toBe('dr.karim@clinic.com');
    expect(result.role).toBe('doctor');
  });

  it('logout invalidates refresh token and clears localStorage', async () => {
    localStorage.setItem('rawd_access_token', 'acc_123');
    localStorage.setItem('rawd_refresh_token', 'ref_123');
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: { message: 'Logged out' } });

    await authService.logout();

    expect(apiClient.post).toHaveBeenCalledWith('/auth/logout', { refresh_token: 'ref_123' });
    expect(localStorage.getItem('rawd_access_token')).toBeNull();
    expect(localStorage.getItem('rawd_refresh_token')).toBeNull();
  });

  it('register posts payload to /auth/register', async () => {
    const payload: any = {
      email: 'new.patient@email.com',
      password: 'Password123!',
      full_name: 'New Patient',
      phone: '+213555000000',
      role: 'patient',
    };
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: { id: 10, ...payload } });

    const result = await authService.register(payload);
    expect(apiClient.post).toHaveBeenCalledWith('/auth/register', payload);
    expect(result.id).toBe(10);
  });

  it('forgotPassword posts email to /auth/forgot-password', async () => {
    vi.spyOn(apiClient, 'post').mockResolvedValueOnce({
      data: { message: 'Password reset link sent' },
    });

    const res = await authService.forgotPassword('dr.karim@clinic.com');
    expect(apiClient.post).toHaveBeenCalledWith('/auth/forgot-password', {
      email: 'dr.karim@clinic.com',
    });
    expect(res.message).toBe('Password reset link sent');
  });

  it('isAuthenticated correctly checks localStorage token presence', () => {
    expect(authService.isAuthenticated()).toBe(false);
    localStorage.setItem('rawd_access_token', 'jwt_test');
    expect(authService.isAuthenticated()).toBe(true);
  });
});

