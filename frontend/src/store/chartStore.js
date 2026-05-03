import { create } from 'zustand'

const useChartStore = create((set) => ({
  chartType: 'bar',
  chartData: null,
  chartOptions: null,
  loading: false,
  error: null,

  setChartType: (chartType) => set({ chartType }),

  setChartData: (chartData) => set({ chartData }),

  setChartOptions: (chartOptions) => set({ chartOptions }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  reset: () => set({ chartType: 'bar', chartData: null, chartOptions: null, loading: false, error: null })
}))

export default useChartStore