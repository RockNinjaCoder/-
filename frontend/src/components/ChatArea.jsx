import React, { useState, useRef, useEffect } from 'react'
import { Input, Button, Empty } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, LoadingOutlined } from '@ant-design/icons'
import useChatStore from '../store/chatStore'
import useSessionStore from '../store/sessionStore'
import useQueryResultStore from '../store/queryResultStore'
import useChartStore from '../store/chartStore'
import { sendMessage, getMessages } from '../api/chat'
import { fetchStream } from '../api/stream'
import { executeQuery } from '../api/query'
import './ChatArea.css'

function ChatArea() {
  const { messages, setMessages, addMessage, updateMessage, clearMessages } = useChatStore()
  const { currentSession } = useSessionStore()
  const { setQueryResult, setSqlQuery } = useQueryResultStore()
  const { setChartData, setChartOptions } = useChartStore()
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [streaming, setStreaming] = useState(false)
  const messageListRef = useRef(null)
  const streamControllerRef = useRef(null)
  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
      if (streamControllerRef.current) {
        streamControllerRef.current.abort()
      }
    }
  }, [])

  useEffect(() => {
    if (currentSession?.id) {
      loadMessages(currentSession.id)
    } else {
      clearMessages()
    }
  }, [currentSession?.id])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadMessages = async (sessionId) => {
    setLoading(true)
    try {
      const data = await getMessages(sessionId)
      if (isMountedRef.current) {
        setMessages(data)
      }
    } catch (error) {
      console.error('Load messages error:', error)
    } finally {
      if (isMountedRef.current) {
        setLoading(false)
      }
    }
  }

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight
    }
  }

  const isDataQuery = (message) => {
    const keywords = ['查询', '统计', '多少', '数量', '总额', '金额', '订单', '用户', '产品', '销售', '所有', '列出', '获取']
    return keywords.some(k => message.includes(k))
  }

  const parseResult = (resultData) => {
    if (!resultData) return null

    if (typeof resultData === 'string') {
      try {
        const parsed = JSON.parse(resultData)
        if (Array.isArray(parsed)) {
          return parsed
        }
        return [parsed]
      } catch {
        return null
      }
    } else if (Array.isArray(resultData)) {
      return resultData
    } else if (typeof resultData === 'object') {
      return [resultData]
    }

    return null
  }

  const updateChartWithResult = (parsedResult, sql) => {
    if (!parsedResult || !Array.isArray(parsedResult) || parsedResult.length === 0) {
      console.warn('No valid data to display in chart:', parsedResult)
      return
    }

    try {
      const firstRow = parsedResult[0]
      if (!firstRow || typeof firstRow !== 'object') {
        console.warn('Invalid first row:', firstRow)
        return
      }

      const keys = Object.keys(firstRow)
      if (keys.length === 0) {
        console.warn('No keys in first row')
        return
      }

      if (keys.length === 1) {
        const key = keys[0]
        const value = firstRow[key]
        const allValues = parsedResult.map(r => r[key]).filter(v => v !== undefined)

        setChartOptions({
          title: { text: sql || '查询结果', left: 'center' },
          tooltip: { trigger: 'item' },
          xAxis: { type: 'category', data: ['结果'] },
          yAxis: { type: 'value', name: '数值' },
          series: [{ name: key.replace('_', ' '), type: 'bar', data: allValues }]
        })
      } else {
        setChartOptions({
          title: { text: sql || '查询结果', left: 'center' },
          tooltip: { trigger: 'axis' },
          xAxis: { type: 'category', data: parsedResult.map(r => r[keys[0]] || '') },
          yAxis: { type: 'value', name: '数值' },
          series: keys.slice(1).map(k => ({
            name: k.replace('_', ' '),
            type: 'bar',
            data: parsedResult.map(r => r[k])
          }))
        })
      }
      setChartData(parsedResult)
    } catch (err) {
      console.error('Chart update error:', err)
    }
  }

  const handleDataQuery = async (queryText, assistantMsgId) => {
    console.log('执行 NL2SQL 查询:', queryText)

    try {
      const result = await executeQuery(currentSession.id, queryText)
      console.log('NL2SQL 结果:', result)

      if (result.success && result.result !== undefined && result.result !== null) {
        const parsedResult = parseResult(result.result)
        console.log('解析后的数据:', parsedResult)

        if (parsedResult && parsedResult.length > 0) {
          setQueryResult(parsedResult)
          setSqlQuery(result.sql || '')
          updateChartWithResult(parsedResult, result.sql)

          const summaryText = parsedResult.length === 1
            ? JSON.stringify(parsedResult[0], null, 2)
            : `${parsedResult.length} 条记录`

          updateMessage(assistantMsgId, (prevMsg) => ({
            ...prevMsg,
            content: (prevMsg?.content || '') +
              `\n\n📊 **查询结果**\n\`\`\`sql\n${result.sql || ''}\n\`\`\`\n结果: ${summaryText}\n数据已同步到右侧表格和图表`
          }))
          return true
        }
      }

      if (result.error) {
        updateMessage(assistantMsgId, (prevMsg) => ({
          ...prevMsg,
          content: (prevMsg?.content || '') + `\n\n⚠️ 查询出错: ${result.error}`
        }))
      } else if (!result.success) {
        updateMessage(assistantMsgId, (prevMsg) => ({
          ...prevMsg,
          content: (prevMsg?.content || '') + `\n\n⚠️ 查询未成功`
        }))
      }
    } catch (err) {
      console.error('NL2SQL 查询失败:', err)
      updateMessage(assistantMsgId, (prevMsg) => ({
        ...prevMsg,
        content: (prevMsg?.content || '') + `\n\n❌ 查询失败: ${err.message}`
      }))
    }

    return false
  }

  const handleSend = async () => {
    if (!inputValue.trim() || !currentSession) return
    if (streaming) return

    const userMsg = {
      id: `temp-${Date.now()}-${Math.random()}`,
      session_id: currentSession.id,
      role: 'user',
      content: inputValue,
      created_at: new Date().toISOString()
    }

    addMessage(userMsg)
    const currentMessage = inputValue
    setInputValue('')
    setLoading(true)
    setStreaming(true)

    const assistantMsgId = `temp-assistant-${Date.now()}`

    addMessage({
      id: assistantMsgId,
      session_id: currentSession.id,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString()
    })

    const isQuery = isDataQuery(currentMessage)
    console.log('消息类型判断:', { currentMessage, isQuery })

    if (isQuery) {
      await handleDataQuery(currentMessage, assistantMsgId)
    }

    try {
      const controller = await fetchStream(
        currentSession.id,
        currentMessage,
        (data) => {
          if (!isMountedRef.current) return
          if (data.content !== undefined) {
            updateMessage(assistantMsgId, (prevMsg) => ({
              ...prevMsg,
              content: (prevMsg?.content || '') + data.content
            }))
          }
        },
        (error) => {
          console.error('Stream error:', error)
          if (isMountedRef.current) {
            updateMessage(assistantMsgId, (prevMsg) => ({
              ...prevMsg,
              content: (prevMsg?.content || '') + '\n\n[网络错误: ' + error.message + ']'
            }))
          }
        },
        () => {
          if (isMountedRef.current) {
            setStreaming(false)
            setLoading(false)
          }
        }
      )

      streamControllerRef.current = controller
    } catch (error) {
      console.error('Send message error:', error)
    } finally {
      if (isMountedRef.current) {
        setStreaming(false)
        setLoading(false)
      }
    }
  }

  const handleStopStream = () => {
    if (streamControllerRef.current) {
      streamControllerRef.current.abort()
      streamControllerRef.current = null
    }
    setStreaming(false)
    setLoading(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const renderMessage = (msg, index) => {
    const isUser = msg.role === 'user'
    const isLastAssistant = index === messages.length - 1 && msg.role === 'assistant'

    return (
      <div
        key={msg.id}
        className={`message-item ${isUser ? 'user' : 'assistant'} ${isLastAssistant && streaming ? 'streaming' : ''}`}
      >
        <div className="message-avatar">
          {isUser ? <UserOutlined /> : (isLastAssistant && streaming ? <LoadingOutlined /> : <RobotOutlined />)}
        </div>
        <div className="message-content">
          <div className="message-text" style={{ whiteSpace: 'pre-wrap' }}>
            {msg.content}
            {isLastAssistant && streaming && <span className="typing-cursor">|</span>}
          </div>
          <div className="message-time">
            {new Date(msg.created_at).toLocaleTimeString()}
          </div>
        </div>
      </div>
    )
  }

  if (!currentSession) {
    return (
      <div className="chat-area">
        <div className="chat-header">
          <h2>智能数据分析助手</h2>
        </div>
        <div className="message-list empty">
          <Empty description="请先选择一个会话或创建新会话" />
        </div>
      </div>
    )
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h2>智能数据分析助手</h2>
        {streaming && (
          <Button size="small" onClick={handleStopStream}>
            停止生成
          </Button>
        )}
      </div>

      <div className="message-list" ref={messageListRef}>
        {messages.length === 0 && !loading ? (
          <Empty description="开始对话吧！询问数据相关问题会自动执行查询" />
        ) : (
          messages.map((msg, index) => renderMessage(msg, index))
        )}
        {loading && !streaming && messages.length > 0 && (
          <div className="message-item assistant loading">
            <div className="message-avatar"><LoadingOutlined spin /></div>
            <div className="message-content">
              <span>AI 正在分析...</span>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <Input.TextArea
          placeholder="请输入您的问题... (Enter发送，Shift+Enter换行)"
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyPress}
          autoSize={{ minRows: 1, maxRows: 4 }}
          disabled={streaming}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!inputValue.trim() || streaming}
          loading={loading && !streaming}
        >
          发送
        </Button>
      </div>
    </div>
  )
}

export default ChatArea