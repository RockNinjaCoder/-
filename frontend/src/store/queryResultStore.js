import { create } from 'zustand'

const useQueryResultStore = create((set) => ({
  queryResult: null,
  sqlQuery: null,
  columns: [],
  loading: false,
  error: null,

  setQueryResult: (result) => set({
    queryResult: result,
    columns: result && result.length > 0 ? Object.keys(result[0]) : []
  }),

  setSqlQuery: (sql) => set({ sqlQuery: sql }),

  setColumns: (columns) => set({ columns }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  clearResult: () => set({
    queryResult: null,
    sqlQuery: null,
    columns: [],
    loading: false,
    error: null
  }),

  reset: () => set({
    queryResult: null,
    sqlQuery: null,
    columns: [],
    loading: false,
    error: null
  })
}))

export default useQueryResultStore