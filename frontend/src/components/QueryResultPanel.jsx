import React, { useState } from 'react'
import { Select, Button, Empty, Spin } from 'antd'
import { TableOutlined, BarChartOutlined } from '@ant-design/icons'
import useQueryResultStore from '../store/queryResultStore'
import { executeQuery } from '../api/query'
import './QueryResultPanel.css'

function QueryResultPanel() {
  const {
    queryResult,
    sqlQuery,
    columns,
    loading,
    error,
    setQueryResult,
    setSqlQuery,
    clearResult,
    setError,
    setLoading
  } = useQueryResultStore()

  const [queryType, setQueryType] = useState('table')

  const hasData = queryResult && Array.isArray(queryResult) && queryResult.length > 0

  const handleQuickQuery = async (queryText) => {
    setLoading(true)
    setError(null)

    try {
      const result = await executeQuery('quick-query-session', queryText)

      if (result.success && result.result) {
        let parsedResult = null

        if (typeof result.result === 'string') {
          try {
            parsedResult = JSON.parse(result.result)
          } catch {
            parsedResult = [{ result: result.result }]
          }
        } else if (Array.isArray(result.result)) {
          parsedResult = result.result
        } else if (typeof result.result === 'object') {
          parsedResult = [result.result]
        }

        if (parsedResult && Array.isArray(parsedResult)) {
          setQueryResult(parsedResult)
          setSqlQuery(result.sql || '')
        } else {
          setError('无法解析查询结果')
        }
      } else if (result.error) {
        setError(result.error)
      }
    } catch (err) {
      setError(err.message || '查询失败')
    } finally {
      setLoading(false)
    }
  }

  const sampleQueries = [
    { value: 'users', label: '查询用户' },
    { value: 'orders', label: '查询订单' },
    { value: 'count', label: '统计数量' }
  ]

  const handleSampleQuery = async (type) => {
    const queryMap = {
      'users': '查询所有用户的信息',
      'orders': '查询最近10条订单',
      'count': '查询总用户数'
    }

    await handleQuickQuery(queryMap[type])
  }

  const tableColumns = columns.map(col => ({
    title: col,
    dataIndex: col,
    key: col,
    width: 150,
    ellipsis: true
  }))

  return (
    <div className="query-result-panel">
      <div className="panel-header">
        <span className="panel-title">
          <TableOutlined style={{ marginRight: 8 }} />
          查询结果
        </span>
        <Select
          size="small"
          value={queryType}
          onChange={setQueryType}
          style={{ width: 100 }}
          options={[
            { value: 'table', label: '表格' },
            { value: 'chart', label: '图表' }
          ]}
        />
      </div>

      <div className="quick-actions">
        <span className="action-label">快捷查询：</span>
        <Button size="small" onClick={() => handleSampleQuery('users')}>
          用户
        </Button>
        <Button size="small" onClick={() => handleSampleQuery('orders')}>
          订单
        </Button>
        <Button size="small" onClick={() => handleSampleQuery('count')}>
          统计
        </Button>
      </div>

      {sqlQuery && (
        <div className="sql-display">
          <code>{sqlQuery}</code>
        </div>
      )}

      <div className="result-container">
        {loading ? (
          <div className="loading-state">
            <Spin tip="查询中..." />
          </div>
        ) : error ? (
          <div className="error-state">
            <Empty
              description={
                <span style={{ color: '#ff4d4f' }}>{error}</span>
              }
            />
          </div>
        ) : hasData ? (
          <Table
            columns={tableColumns}
            dataSource={queryResult}
            rowKey={(record, index) => index}
            size="small"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total) => `共 ${total} 条`
            }}
            scroll={{ x: 'max-content' }}
          />
        ) : (
          <div className="empty-state">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <span style={{ color: '#999' }}>
                  暂无查询结果
                  <br />
                  <span style={{ fontSize: 12 }}>
                    点击快捷查询或发送自然语言问题
                  </span>
                </span>
              }
            />
          </div>
        )}
      </div>

      {hasData && (
        <div className="result-info">
          <span>共 {queryResult.length} 条结果，{columns.length} 列</span>
          <Button size="small" type="text" onClick={clearResult}>
            清除
          </Button>
        </div>
      )}
    </div>
  )
}

export default QueryResultPanel