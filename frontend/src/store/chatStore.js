import { create } from 'zustand'

const useChatStore = create((set, get) => ({
  messages: [],
  loading: false,
  streaming: false,
  error: null,

  setMessages: (messages) => set({ messages }),

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  updateMessage: (messageId, updates) => set((state) => ({
    messages: state.messages.map(m => {
      if (m.id !== messageId) return m
      if (typeof updates === 'function') {
        return updates(m)
      }
      return { ...m, ...updates }
    })
  })),

  clearMessages: () => set({ messages: [] }),

  setLoading: (loading) => set({ loading }),

  setStreaming: (streaming) => set({ streaming }),

  setError: (error) => set({ error }),

  reset: () => set({ messages: [], loading: false, streaming: false, error: null })
}))

export default useChatStore