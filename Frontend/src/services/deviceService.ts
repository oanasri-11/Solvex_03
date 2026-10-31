import { apiClient } from './apiClient';

export interface ConnectedDeviceCreate {
  device_model: string;
  serial_number?: string;
  mac_address?: string;
  validation_status?: string;
}

export interface ConnectedDeviceOut {
  id: number;
  patient_id: number;
  device_model: string;
  serial_number?: string | null;
  mac_address?: string | null;
  validation_status: string;
  paired_at: string;
  last_sync_at?: string | null;
}

export const deviceService = {
  /**
   * Get paired devices for current patient
   */
  async getOwnDevices(): Promise<ConnectedDeviceOut[]> {
    const response = await apiClient.get<ConnectedDeviceOut[]>('/patients/me/devices');
    return response.data;
  },

  /**
   * Pair a Bluetooth / BLE blood pressure monitor
   */
  async pairDevice(data: ConnectedDeviceCreate): Promise<ConnectedDeviceOut> {
    const response = await apiClient.post<ConnectedDeviceOut>('/patients/me/devices', data);
    return response.data;
  },

  /**
   * Unpair a device
   */
  async unpairDevice(id: number): Promise<{ message: string }> {
    const response = await apiClient.delete<{ message: string }>(`/patients/me/devices/${id}`);
    return response.data;
  },
};

