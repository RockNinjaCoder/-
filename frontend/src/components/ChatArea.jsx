import React, { useState, useRef, useEffect } from 'react'
import { Input, Button, Spin, Empty, Avatar } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined, LoadingOutlined } from '@ant-design/icons'
import useChatStore from '../store/chatStore'
import useSessionStore from '../store/sessionStore'
import { sendMessage, getMessages } from '../api/chat'
import { fetchStream } from '../api/stream'
import './ChatArea.css'

const TYPING_SPEED = 30

function ChatArea() {
  const { messages, setMessages, addMessage, updateMessage, setLoading, setStreaming, clearMessages } = useChatStore()
  const { currentSession } = useSessionStore()
  const [inputValue, setInputValue] = useState('')
  const [loading, setLocalLoading] = useState(false)
  const [streaming, setLocalStreaming] = useState(false)
  const messageListRef = useRef(null)
  const streamControllerRef = useRef(null)

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
    setLocalLoading(true)
    try {
      const data = await getMessages(sessionId)
      setMessages(data)
    } catch (error) {
      console.error('Load messages error:', error)
    } finally {
      setLocalLoading(false)
    }
  }

  const scrollToBottom = () => {
    if (messageListRef.current) {
      messageListRef.current.scrollTop = messageListRef.current.scrollHeight
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || !currentSession) return

    const userMessage = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.id,
      role: 'user',
      content: inputValue,
      created_at: new Date().toISOString()
    }

    addMessage(userMessage)
    setInputValue('')
    setLocalLoading(true)

    try {
      const response = await sendMessage(currentSession.id, inputValue)
      addMessage(response)
      setLocalLoading(false)

      setLocalStreaming(true)
      setStreaming(true)

      streamControllerRef.current = fetchStream(
        currentSession.id,
        (data) => {
          if (data.type === 'message' && data.content) {
            const lastMsg = messages[messages.length - 1]
            if (lastMsg?.role === 'assistant' && !lastMsg.id.startsWith('temp')) {
              updateMessage(lastMsg.id, { content: lastMsg.content + data.content })
            }
          }
        },
        (error) => {
          console.error('Stream error:', error)
          setLocalStreaming(false)
          setStreaming(false)
        },
        () => {
          setLocalStreaming(false)
          setStreaming(false)
        }
      )
    } catch (error) {
      console.error('Send message error:', error)
      setLocalLoading(false)
      setLocalStreaming(false)
      setStreaming(false)
    }
  }

  const handleStopStream = () => {
    if (streamControllerRef.current) {
      streamControllerRef.current.abort()
      streamControllerRef.current = null
    }
    setLocalStreaming(false)
    setStreaming(false)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const renderMessage = (msg, index) => {
    const isUser = msg.role === 'user'
    const showAvatar = index === 0 || messages[index - 1]?.role !== msg.role

    return (
      <div 
        key={msg.id} 
        className={`message-item ${isUser ? 'user' : 'assistant'} ${showAvatar ? 'with-avatar' : ''}`}
      >
        <div className="message-avatar">
          {isUser ? <UserOutlined /> : (streaming && index === messages.length ? <LoadingOutlined spin /> : <RobotOutlined />)}
        </div>
        <div className="message-content">
          <div className="message-text">{msg.content}</div>
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
          <Empty description="开始对话吧！" />
        ) : (
          messages.map((msg, index) => renderMessage(msg, index))
        )}
        {loading && (
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
          placeholder="请输入您的问题... (Shift+Enter换行，Enter发送)"
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