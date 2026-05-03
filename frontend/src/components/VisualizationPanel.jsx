import React, { useState } from 'react'
import ReactECharts from 'echarts-for-react'
import { Select, Card, Empty } from 'antd'
import './VisualizationPanel.css'

const CHART_OPTIONS = {
  sales: {
    title: { text: '销售数据分析', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['销售额'], bottom: 0 },
    xAxis: { type: 'category', data: ['Product A', 'Product B', 'Product C'] },
    yAxis: { type: 'value', name: '金额 (¥)' },
    series: [{ name: '销售额', type: 'bar', data: [499.95, 149.99, 199.99] }]
  },
  orders: {
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
  trend: {
    title: { text: '销售趋势', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value' },
    series: [{ name: '销售额', type: 'line', data: [120, 200, 150, 300, 250, 180, 220] }]
  }
}

function VisualizationPanel() {
  const [chartType, setChartType] = useState('sales')

  const handleChartChange = (value) => {
    setChartType(value)
  }

  const currentChart = CHART_OPTIONS[chartType] || CHART_OPTIONS.sales

  return (
    <div className="visualization-panel">
      <div className="panel-header">
        <h3>数据可视化</h3>
        <Select
          value={chartType}
          onChange={handleChartChange}
          style={{ width: 150 }}
          options={[
            { value: 'sales', label: '销售额统计' },
            { value: 'orders', label: '订单量分布' },
            { value: 'trend', label: '销售趋势' }
          ]}
        />
      </div>

      <div className="chart-container">
        {chartType ? (
          <ReactECharts option={currentChart} style={{ height: '100%', width: '100%' }} />
        ) : (
          <Empty description="暂无可视化数据" />
        )}
      </div>

      <div className="chart-info">
        <Card size="small" title="数据概览">
          <p>总销售额：¥549.95</p>
          <p>总订单数：7</p>
          <p>平均订单金额：¥78.56</p>
        </Card>
      </div>
    </div>
  )
}

export default VisualizationPanel