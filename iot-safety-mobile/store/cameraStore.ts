import { create } from 'zustand';
import { Camera, Detection } from '../types/api';
import { apiService } from '../services/api';

interface CameraStore {
  cameras: Camera[];
  detections: Detection[];
  loading: boolean;
  error: string | null;
  selectedSeverity: 'all' | 'low' | 'medium' | 'high' | 'critical';
  fetchCameras: () => Promise<void>;
  fetchDetections: () => Promise<void>;
  acknowledgeDetection: (detectionId: number) => Promise<void>;
  setSelectedSeverity: (severity: 'all' | 'low' | 'medium' | 'high' | 'critical') => void;
  getFilteredDetections: () => Detection[];
  clearError: () => void;
}

export const useCameraStore = create<CameraStore>((set, get) => ({
  cameras: [],
  detections: [],
  loading: false,
  error: null,
  selectedSeverity: 'all',

  fetchCameras: async () => {
    set({ loading: true, error: null });
    try {
      const cameras = await apiService.getCameras();
      set({ cameras, loading: false });
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch cameras',
      });
    }
  },

  fetchDetections: async () => {
    set({ loading: true, error: null });
    try {
      const detections = await apiService.getDetections();
      set({ detections, loading: false });
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch detections',
      });
    }
  },

  acknowledgeDetection: async (detectionId: number) => {
    try {
      await apiService.acknowledgeDetection(detectionId);
      const state = get();
      const updatedDetections = state.detections.map((detection) =>
        detection.id === detectionId
          ? { ...detection, acknowledged: true }
          : detection
      );
      set({ detections: updatedDetections });
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to acknowledge detection',
      });
    }
  },

  setSelectedSeverity: (severity) => set({ selectedSeverity: severity }),

  getFilteredDetections: () => {
    const state = get();
    if (state.selectedSeverity === 'all') {
      return state.detections;
    }
    return state.detections.filter((d) => d.severity === state.selectedSeverity);
  },

  clearError: () => set({ error: null }),
}));
