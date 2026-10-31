import { describe, it, expect, vi, beforeEach } from 'vitest';
import { deviceService } from '../services/deviceService';
import { userService } from '../services/userService';
import { apiClient } from '../services/apiClient';

describe('deviceService & userService Unit Tests', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  describe('deviceService', () => {
    it('getOwnDevices fetches paired hardware list', async () => {
      const mockDevices = [
        { id: 1, device_model: 'OMRON HEM-7361T-EBK', validation_status: 'stride_bp_validated' },
      ];
      vi.spyOn(apiClient, 'get').mockResolvedValueOnce({ data: mockDevices });

      const res = await deviceService.getOwnDevices();
      expect(apiClient.get).toHaveBeenCalledWith('/patients/me/devices');
      expect(res.length).toBe(1);
      expect(res[0].device_model).toBe('OMRON HEM-7361T-EBK');
    });

    it('pairDevice posts BLE monitor metadata', async () => {
      const payload = {
        device_model: 'Beurer BM 54 BLE',
        serial_number: 'BM-99212',
      };
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: { id: 3, ...payload } });

      const res = await deviceService.pairDevice(payload);
      expect(apiClient.post).toHaveBeenCalledWith('/patients/me/devices', payload);
      expect(res.id).toBe(3);
    });

    it('unpairDevice sends DELETE request for device', async () => {
      vi.spyOn(apiClient, 'delete').mockResolvedValueOnce({ data: { message: 'Device unpaired' } });

      const res = await deviceService.unpairDevice(3);
      expect(apiClient.delete).toHaveBeenCalledWith('/patients/me/devices/3');
      expect(res.message).toBe('Device unpaired');
    });
  });

  describe('userService', () => {
    it('updatePreferences patches /users/me', async () => {
      const prefs = {
        locale: 'ar',
        text_size: 150,
        theme: 'calm_dark',
        high_contrast: true,
      };
      vi.spyOn(apiClient, 'patch').mockResolvedValueOnce({ data: { id: 1, ...prefs } });

      const res = await userService.updatePreferences(prefs);
      expect(apiClient.patch).toHaveBeenCalledWith('/users/me', prefs);
      expect(res.locale).toBe('ar');
      expect(res.text_size).toBe(150);
    });

    it('changePassword posts to /users/me/change-password', async () => {
      const payload = {
        current_password: 'OldPassword123!',
        new_password: 'NewPassword123!',
      };
      vi.spyOn(apiClient, 'post').mockResolvedValueOnce({ data: { message: 'Password updated' } });

      const res = await userService.changePassword(payload);
      expect(apiClient.post).toHaveBeenCalledWith('/users/me/change-password', payload);
      expect(res.message).toBe('Password updated');
    });
  });
});

