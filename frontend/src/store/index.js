import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => set({ user, token, isAuthenticated: true }),
      logout: () => set({ user: null, token: null, isAuthenticated: false }),
      updateUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
    }
  )
);

export const useAgentStore = create((set) => ({
  runs: [],
  currentRun: null,
  isRunning: false,
  setRuns: (runs) => set({ runs }),
  addRun: (run) => set((state) => ({ runs: [run, ...state.runs] })),
  setCurrentRun: (run) => set({ currentRun: run }),
  setIsRunning: (isRunning) => set({ isRunning }),
  updateRun: (id, updates) =>
    set((state) => ({
      runs: state.runs.map((run) =>
        run.id === id ? { ...run, ...updates } : run
      ),
      currentRun:
        state.currentRun?.id === id
          ? { ...state.currentRun, ...updates }
          : state.currentRun,
    })),
}));
