import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import axios from 'axios';
import { apiClient, parseApiError } from '../services/apiClient';

describe('API Client & Interceptor Suite', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('Request Interceptor - Bearer Token Injection', () => {
    it('automatically attaches Bearer token when stored in localStorage', async () => {
      localStorage.setItem('rawd_access_token', 'mock_jwt_token_123');

      // Interceptor is synchronous on config
      const config: any = { headers: {} };
      // Call request interceptor
      const requestInterceptor = (apiClient.interceptors.request as any).handlers[0].fulfilled;
      const modifiedConfig = requestInterceptor(config);

      expect(modifiedConfig.headers.Authorization).toBe('Bearer mock_jwt_token_123');
    });

    it('leaves Authorization header unset when no token exists', () => {
      const config: any = { headers: {} };
      const requestInterceptor = (apiClient.interceptors.request as any).handlers[0].fulfilled;
      const modifiedConfig = requestInterceptor(config);

      expect(modifiedConfig.headers.Authorization).toBeUndefined();
    });
  });

  describe('parseApiError - Backend Error Normalization', () => {
    it('normalizes string detail from FastAPI 400/401/404 response', () => {
      const mockAxiosError: any = {
        isAxiosError: true,
        response: {
          status: 401,
          data: { detail: 'Incorrect email or password, or account is inactive' },
        },
      };
      vi.spyOn(axios, 'isAxiosError').mockReturnValue(true);

      const parsed = parseApiError(mockAxiosError);
      expect(parsed.status).toBe(401);
      expect(parsed.message).toBe('Incorrect email or password, or account is inactive');
    });

    it('normalizes validation error array from FastAPI 422 response', () => {
      const mockAxiosError: any = {
        isAxiosError: true,
        response: {
          status: 422,
          data: {
            detail: [
              { loc: ['body', 'systolic'], msg: 'Field required', type: 'value_error.missing' },
              { loc: ['body', 'diastolic'], msg: 'Input should be greater than 0', type: 'value_error.number.not_gt' },
            ],
          },
        },
      };
      vi.spyOn(axios, 'isAxiosError').mockReturnValue(true);

      const parsed = parseApiError(mockAxiosError);
      expect(parsed.status).toBe(422);
      expect(parsed.message).toBe('Field required; Input should be greater than 0');
    });

    it('handles unexpected non-Axios error with 500 status fallback', () => {
      vi.spyOn(axios, 'isAxiosError').mockReturnValue(false);
      const standardError = new Error('Connection refused');

      const parsed = parseApiError(standardError);
      expect(parsed.status).toBe(500);
      expect(parsed.message).toBe('Connection refused');
    });
  });

  describe('Response Interceptor - 401 Refresh Token Handling', () => {
    it('clears storage when refresh token is missing on 401', async () => {
      localStorage.setItem('rawd_access_token', 'expired_token');
      // No refresh token in storage

      const error: any = {
        config: { url: '/doctor/me/dashboard', headers: {} },
        response: { status: 401 },
      };

      const responseInterceptorReject = (apiClient.interceptors.response as any).handlers[0].rejected;

      await expect(responseInterceptorReject(error)).rejects.toBeDefined();
      expect(localStorage.getItem('rawd_access_token')).toBeNull();
      expect(localStorage.getItem('rawd_refresh_token')).toBeNull();
    });
  });
});

