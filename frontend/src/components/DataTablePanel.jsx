import React, { useState, useEffect } from 'react'
import { Table, Card, Empty, Button, Tooltip, Tag } from 'antd'
import { DownloadOutlined, ReloadOutlined, TableOutlined } from '@ant-design/icons'
import useQueryResultStore from '../store/queryResultStore'
import './DataTablePanel.css'

function DataTablePanel() {
  const {
    queryResult,
    sqlQuery,
    columns,
    loading,
    error,
    setQueryResult,
    setSqlQuery,
    clearResult,
    setError
  } = useQueryResultStore()

  const [pageSize, setPageSize] = useState(10)
  const [currentPage, setCurrentPage] = useState(1)

  const hasData = queryResult && Array.isArray(queryResult) && queryResult.length > 0

  const handleExport = () => {
    if (!hasData) return

    const csvContent = [
      columns.join(','),
      ...queryResult.map(row =>
        columns.map(col => {
          const value = row[col]
          if (value === null || value === undefined) return ''
          const str = String(value)
          return str.includes(',') || str.includes('"') || str.includes('\n')
            ? `"${str.replace(/"/g, '""')}"`
            : str
        }).join(',')
      )
    ].join('\n')

    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `query_result_${Date.now()}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  const handleRefresh = () => {
    setCurrentPage(1)
  }

  const handleClear = () => {
    clearResult()
    setCurrentPage(1)
  }

  const tableColumns = columns.map(col => ({
    title: col,
    dataIndex: col,
    key: col,
    width: 150,
    ellipsis: true,
    render: (text) => {
      if (text === null || text === undefined) {
        return <span style={{ color: '#999' }}>NULL</span>
      }
      return String(text)
    }
  }))

  return (
    <div className="data-table-panel">
      <div className="panel-header">
        <div className="header-title">
          <TableOutlined style={{ marginRight: 8 }} />
          <span>数据表格</span>
          {hasData && (
            <Tag color="blue" style={{ marginLeft: 8 }}>
              {queryResult.length} 条
            </Tag>
          )}
        </div>
        <div className="header-actions">
          <Tooltip title="刷新">
            <Button
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleRefresh}
              disabled={!hasData}
            />
          </Tooltip>
          <Tooltip title="导出 CSV">
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={handleExport}
              disabled={!hasData}
            />
          </Tooltip>
          <Tooltip title="清除数据">
            <Button
              size="small"
              onClick={handleClear}
              disabled={!hasData}
            >
              清除
            </Button>
          </Tooltip>
        </div>
      </div>

      {sqlQuery && (
        <div className="sql-query-display">
          <code>{sqlQuery}</code>
        </div>
      )}

      <div className="table-container">
        {loading ? (
          <div className="table-loading">
            <span>加载中...</span>
          </div>
        ) : error ? (
          <div className="table-error">
            <Empty description={<span style={{ color: '#ff4d4f' }}>{error}</span>} />
          </div>
        ) : hasData ? (
          <Table
            columns={tableColumns}
            dataSource={queryResult}
            rowKey={(record, index) => index}
            pagination={{
              current: currentPage,
              pageSize: pageSize,
              total: queryResult.length,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50', '100'],
              showTotal: (total, range) =>
                `${range[0]}-${range[1]} / ${total} 条`,
              onChange: (page, size) => {
                setCurrentPage(page)
                setPageSize(size)
              }
            }}
            scroll={{ x: columns.length * 150 }}
            size="small"
          />
        ) : (
          <div className="table-empty">
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <span style={{ color: '#999' }}>
                  暂无数据
                  <br />
                  <span style={{ fontSize: 12 }}>
                    执行查询后将在这里展示结果
                  </span>
                </span>
              }
            />
          </div>
        )}
      </div>

      {hasData && (
        <div className="table-info">
          <Card size="small">
            <div className="info-row">
              <span className="info-label">总行数：</span>
              <span className="info-value">{queryResult.length}</span>
            </div>
            <div className="info-row">
              <span className="info-label">总列数：</span>
              <span className="info-value">{columns.length}</span>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}

export default DataTablePanel