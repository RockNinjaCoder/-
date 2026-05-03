import React, { useState, useEffect } from 'react'
import { List, Button, Input, message } from 'antd'
import { PlusOutlined, SearchOutlined } from '@ant-design/icons'
import './ChatSidebar.css'

const MOCK_SESSIONS = [
  { id: '1', title: '数据分析会话 1', created_at: '2026-05-02 10:00:00', updated_at: '2026-05-02 10:30:00', is_active: 1 },
  { id: '2', title: '用户查询分析', created_at: '2026-05-02 09:00:00', updated_at: '2026-05-02 09:45:00', is_active: 0 },
]

function ChatSidebar() {
  const [sessions, setSessions] = useState(MOCK_SESSIONS)
  const [activeSession, setActiveSession] = useState('1')
  const [searchText, setSearchText] = useState('')

  const handleNewSession = () => {
    const newSession = {
      id: Date.now().toString(),
      title: '新会话',
      created_at: new Date().toLocaleString(),
      updated_at: new Date().toLocaleString(),
      is_active: 1
    }
    setSessions([newSession, ...sessions])
    setActiveSession(newSession.id)
    message.success('创建新会话成功')
  }

  const handleSelectSession = (sessionId) => {
    setActiveSession(sessionId)
  }

  const filteredSessions = sessions.filter(s => 
    s.title.toLowerCase().includes(searchText.toLowerCase())
  )

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleNewSession}
          block
        >
          新建会话
        </Button>
      </div>
      
      <div className="search-box">
        <Input 
          placeholder="搜索会话..." 
          prefix={<SearchOutlined />}
          value={searchText}
          onChange={e => setSearchText(e.target.value)}
        />
      </div>

      <div className="session-list">
        <List
          dataSource={filteredSessions}
          renderItem={item => (
            <List.Item 
              className={`session-item ${activeSession === item.id ? 'active' : ''}`}
              onClick={() => handleSelectSession(item.id)}
            >
              <List.Item.Meta
                title={item.title}
                description={item.updated_at}
              />
            </List.Item>
          )}
        />
      </div>
    </div>
  )
}

export default ChatSidebar