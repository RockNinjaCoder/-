import { create } from 'zustand'

const useSessionStore = create((set, get) => ({
  sessions: [],
  currentSession: null,
  loading: false,
  error: null,

  setSessions: (sessions) => set({ sessions }),

  setCurrentSession: (session) => set({ currentSession: session }),

  addSession: (session) => set((state) => ({
    sessions: [session, ...state.sessions]
  })),

  updateSession: (sessionId, updates) => set((state) => ({
    sessions: state.sessions.map(s =>
      s.id === sessionId ? { ...s, ...updates } : s
    ),
    currentSession: state.currentSession?.id === sessionId
      ? { ...state.currentSession, ...updates }
      : state.currentSession
  })),

  deleteSession: (sessionId) => set((state) => ({
    sessions: state.sessions.filter(s => s.id !== sessionId),
    currentSession: state.currentSession?.id === sessionId
      ? null
      : state.currentSession
  })),

  reset: () => set({ sessions: [], currentSession: null, loading: false, error: null })
}))

export default useSessionStore