import { useState, useCallback } from 'react'
import useChartStore from '../store/chartStore'

export function useChart() {
  const { chartType, chartData, chartOptions, setChartType, setChartData, setChartOptions, setLoading, setError, reset } = useChartStore()
  const [loading, setLocalLoading] = useState(false)
  const [error, setLocalError] = useState(null)

  const changeChartType = useCallback((type) => {
    setChartType(type)
  }, [setChartType])

  const updateChartData = useCallback((data) => {
    setChartData(data)
  }, [setChartData])

  const updateChartOptions = useCallback((options) => {
    setChartOptions(options)
  }, [setChartOptions])

  const refresh = useCallback(async () => {
    setLocalLoading(true)
    setLocalError(null)
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (err) {
      setLocalError(err.message)
    } finally {
      setLocalLoading(false)
    }
  }, [])

  const exportChart = useCallback(() => {
    const chartInstance = document.querySelector('.chart-container .echarts-instance')
    if (chartInstance) {
      const base64 = chartInstance.getAttribute('data-url')
      if (base64) {
        const link = document.createElement('a')
        link.download = `chart-${Date.now()}.png`
        link.href = base64
        link.click()
      }
    }
  }, [])

  return {
    chartType,
    chartData,
    chartOptions,
    loading,
    error,
    changeChartType,
    updateChartData,
    updateChartOptions,
    refresh,
    exportChart,
    reset
  }
}

export default useChart