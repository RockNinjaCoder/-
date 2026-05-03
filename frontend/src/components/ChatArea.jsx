import React, { useState } from 'react'
import { Input, Button, Spin, Empty } from 'antd'
import { SendOutlined, RobotOutlined, UserOutlined } from '@ant-design/icons'
import './ChatArea.css'

const MOCK_MESSAGES = [
  { id: '1', role: 'user', content: '你好，我想查询一下上个月的销售数据' },
  { id: '2', role: 'assistant', content: '好的，我来帮您查询上个月的销售数据。请问您想查看哪方面的数据？比如总体销售额、产品销量还是用户分析？' },
  { id: '3', role: 'user', content: '看看总体销售额吧' },
  { id: '4', role: 'assistant', content: '根据数据库中的数据，上个月（2026年4月）的总体销售额为 ¥549.95，其中 Product A 销量最高共5件，Product B 1件，Product C 1件。详细数据已生成可视化图表展示在右侧。' }
]

function ChatArea() {
  const [messages, setMessages] = useState(MOCK_MESSAGES)
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = () => {
    if (!inputValue.trim()) return

    const newMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue
    }
    setMessages([...messages, newMessage])
    setInputValue('')
    setLoading(true)

    setTimeout(() => {
      const response = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '感谢您的提问！我正在分析您的问题，请稍候...'
      }
      setMessages(prev => [...prev, response])
      setLoading(false)
    }, 1000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-area">
      <div className="chat-header">
        <h2>智能数据分析助手</h2>
      </div>

      <div className="message-list">
        {messages.length === 0 ? (
          <Empty description="开始对话吧！" />
        ) : (
          messages.map(msg => (
            <div 
              key={msg.id} 
              className={`message-item ${msg.role === 'user' ? 'user' : 'assistant'}`}
            >
              <div className="message-avatar">
                {msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
              </div>
              <div className="message-content">
                <div className="message-text">{msg.content}</div>
                <div className="message-time">
                  {new Date().toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="message-item assistant">
            <div className="message-avatar"><RobotOutlined /></div>
            <div className="message-content">
              <Spin size="small" />
              <span style={{ marginLeft: 8 }}>AI 正在分析...</span>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <Input.TextArea
          placeholder="请输入您的问题..."
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          autoSize={{ minRows: 1, maxRows: 4 }}
        />
        <Button 
          type="primary" 
          icon={<SendOutlined />}
          onClick={handleSend}
          disabled={!inputValue.trim()}
        >
          发送
        </Button>
      </div>
    </div>
  )
}

export default ChatArea