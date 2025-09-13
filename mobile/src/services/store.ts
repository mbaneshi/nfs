import {create} from 'zustand';

interface AppState {
  isLoading: boolean;
  user: any | null;
  workflows: any[];
  setLoading: (loading: boolean) => void;
  setUser: (user: any | null) => void;
  setWorkflows: (workflows: any[]) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isLoading: false,
  user: null,
  workflows: [],
  setLoading: (loading) => set({isLoading: loading}),
  setUser: (user) => set({user}),
  setWorkflows: (workflows) => set({workflows}),
}));
