/**
 * Empty mock datasets - all application state is now driven directly by the backend API.
 */
import type { Patient, DoctorAlert, PatientAlert, BPReading } from '../types';

export const initialPatients: Patient[] = [];
export const initialDoctorAlerts: DoctorAlert[] = [];
export const initialPatientAlerts: PatientAlert[] = [];
export const initialMarcDupuisReadings: BPReading[] = [];
export const initialAminaReadings: BPReading[] = [];
