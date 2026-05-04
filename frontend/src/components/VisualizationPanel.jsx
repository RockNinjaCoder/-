import React, { useState, useEffect } from 'react'
import ReactECharts from 'echarts-for-react'
import { Select, Card, Empty, Button, Spin } from 'antd'
import { DownloadOutlined, FullscreenOutlined, ReloadOutlined } from '@ant-design/icons'
import useChartStore from '../store/chartStore'
import './VisualizationPanel.css'

const DEMO_DATA = {
  bar: {
    title: { text: '销售数据分析', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额'], bottom: 0 },
    xAxis: { type: 'category', data: ['Product A', 'Product B', 'Product C'] },
    yAxis: { type: 'value', name: '金额 (¥)' },
    series: [{ name: '销售额', type: 'bar', data: [499.95, 149.99, 199.99] }]
  },
  line: {
    title: { text: '销售趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [{ name: '销售额', type: 'line', data: [120, 200, 150, 300, 250, 180, 220] }]
  },
  pie: {
    title: { text: '订单量统计', left: 'center' },
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      name: '订单量',
      type: 'pie',
      radius: '60%',
      data: [
        { value: 5, name: 'Product A' },
        { value: 1, name: 'Product B' },
        { value: 1, name: 'Product C' }
      ]
    }]
  },
  scatter: {
    title: { text: '价格与销量关系', left: 'center' },
    tooltip: { trigger: 'item' },
    xAxis: { type: 'value', name: '价格' },
    yAxis: { type: 'value', name: '销量' },
    series: [{
      name: '产品',
      type: 'scatter',
      data: [[99.99, 5], [149.99, 1], [199.99, 1]]
    }]
  }
}

function VisualizationPanel() {
  const { chartType, chartData, chartOptions, setChartType, setChartOptions } = useChartStore()
  const [localLoading, setLocalLoading] = useState(false)

  const hasQueryData = chartOptions && typeof chartOptions === 'object' && Object.keys(chartOptions).length > 0

  const currentOption = hasQueryData ? chartOptions : (DEMO_DATA[chartType] || DEMO_DATA.bar)

  const chartTypeLabels = {
    bar: '柱状图',
    line: '折线图',
    pie: '饼图',
    scatter: '散点图'
  }

  const handleChartTypeChange = (value) => {
    setChartType(value)
  }

  const handleRefresh = () => {
    setLocalLoading(true)
    setTimeout(() => setLocalLoading(false), 500)
  }

  const handleExport = () => {
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
  }

  return (
    <div className="visualization-panel">
      <div className="panel-header">
        <h3>数据可视化</h3>
        <div className="header-actions">
          <Button size="small" icon={<ReloadOutlined />} onClick={handleRefresh} />
          <Button size="small" icon={<FullscreenOutlined />} />
          <Button size="small" icon={<DownloadOutlined />} onClick={handleExport} />
        </div>
      </div>

      <div className="chart-controls">
        <Select
          value={chartType}
          onChange={handleChartTypeChange}
          style={{ width: 120 }}
          options={[
            { value: 'bar', label: '柱状图' },
            { value: 'line', label: '折线图' },
            { value: 'pie', label: '饼图' },
            { value: 'scatter', label: '散点图' }
          ]}
        />
        <Select
          value={hasQueryData ? 'query' : 'demo'}
          style={{ width: 120 }}
          options={[
            { value: 'demo', label: '示例数据' },
            { value: 'query', label: '查询结果' }
          ]}
        />
      </div>

      <div className="chart-container">
        {localLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Spin size="large" tip="加载中..." />
          </div>
        ) : (
          <ReactECharts
            option={currentOption}
            style={{ height: '100%', width: '100%' }}
          />
        )}
      </div>

      <div className="chart-info">
        <Card size="small" title="数据概览">
          <div className="info-row">
            <span className="info-label">图表类型：</span>
            <span className="info-value">{chartTypeLabels[chartType] || '柱状图'}</span>
          </div>
          <div className="info-row">
            <span className="info-label">数据来源：</span>
            <span className="info-value">{hasQueryData ? '查询结果' : '示例数据'}</span>
          </div>
          {chartData && chartData.length > 0 && (
            <div className="info-row">
              <span className="info-label">数据条数：</span>
              <span className="info-value">{chartData.length}</span>
            </div>
          )}
          {!hasQueryData && (
            <>
              <div className="info-row">
                <span className="info-label">总销售额：</span>
                <span className="info-value">¥549.95</span>
              </div>
              <div className="info-row">
                <span className="info-label">总订单数：</span>
                <span className="info-value">7</span>
              </div>
            </>
          )}
        </Card>
      </div>

      <div className="chart-actions">
        <Button type="primary" block disabled={!hasQueryData}>
          生成分析报告
        </Button>
      </div>
    </div>
  )
}

export default VisualizationPanel