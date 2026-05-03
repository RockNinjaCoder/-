import React, { useState, useEffect } from 'react'
import { List, Button, Input, Popconfirm, message, Dropdown } from 'antd'
import { PlusOutlined, SearchOutlined, MoreOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons'
import useSessionStore from '../store/sessionStore'
import { getSessions, createSession, deleteSession, updateSession } from '../api/session'
import './ChatSidebar.css'

function ChatSidebar({ onSelectSession }) {
  const { sessions, currentSession, setSessions, setCurrentSession, addSession, deleteSession: deleteSessionFromStore } = useSessionStore()
  const [searchText, setSearchText] = useState('')
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [editingTitle, setEditingTitle] = useState('')

  useEffect(() => {
    loadSessions()
  }, [])

  const loadSessions = async () => {
    setLoading(true)
    try {
      const data = await getSessions()
      setSessions(data)
    } catch (error) {
      console.error('Load sessions error:', error)
      message.error('加载会话列表失败')
    } finally {
      setLoading(false)
    }
  }

  const handleNewSession = async () => {
    try {
      const newSession = await createSession('新会话')
      addSession(newSession)
      setCurrentSession(newSession)
      onSelectSession?.(newSession)
      message.success('创建新会话成功')
    } catch (error) {
      console.error('Create session error:', error)
      message.error('创建会话失败')
    }
  }

  const handleSelectSession = (session) => {
    setCurrentSession(session)
    onSelectSession?.(session)
  }

  const handleDeleteSession = async (sessionId) => {
    try {
      await deleteSession(sessionId)
      deleteSessionFromStore(sessionId)
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
      }
      message.success('删除会话成功')
    } catch (error) {
      console.error('Delete session error:', error)
      message.error('删除会话失败')
    }
  }

  const handleStartEdit = (session, e) => {
    e?.stopPropagation()
    setEditingId(session.id)
    setEditingTitle(session.title)
  }

  const handleSaveEdit = async () => {
    if (!editingId || !editingTitle.trim()) return

    try {
      const updated = await updateSession(editingId, { title: editingTitle.trim() })
      const { updateSession: updateInStore } = useSessionStore.getState()
      updateInStore(editingId, updated)
      setEditingId(null)
      setEditingTitle('')
      message.success('重命名成功')
    } catch (error) {
      console.error('Update session error:', error)
      message.error('重命名失败')
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditingTitle('')
  }

  const filteredSessions = sessions.filter(s => 
    s.title.toLowerCase().includes(searchText.toLowerCase())
  )

  const renderSessionItem = (session) => {
    const isActive = currentSession?.id === session.id
    const isEditing = editingId === session.id

    return (
      <List.Item
        className={`session-item ${isActive ? 'active' : ''}`}
        onClick={() => !isEditing && handleSelectSession(session)}
      >
        {isEditing ? (
          <Input
            size="small"
            value={editingTitle}
            onChange={e => setEditingTitle(e.target.value)}
            onPressEnter={handleSaveEdit}
            onBlur={handleSaveEdit}
            onClick={e => e.stopPropagation()}
            autoFocus
          />
        ) : (
          <>
            <List.Item.Meta
              title={
                <span onDoubleClick={(e) => handleStartEdit(session, e)}>
                  {session.title}
                </span>
              }
              description={session.updated_at || session.created_at}
            />
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'rename',
                    icon: <EditOutlined />,
                    label: '重命名',
                    onClick: (e) => handleStartEdit(session, e.domEvent)
                  },
                  {
                    key: 'delete',
                    icon: <DeleteOutlined />,
                    label: '删除',
                    danger: true
                  }
                ],
                onClick: ({ key }) => {
                  if (key === 'delete') {
                    handleDeleteSession(session.id)
                  }
                }
              }}
              trigger={['click']}
            >
              <Button
                type="text"
                size="small"
                icon={<MoreOutlined />}
                onClick={e => e.stopPropagation()}
              />
            </Dropdown>
          </>
        )}
      </List.Item>
    )
  }

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={handleNewSession}
          block
          loading={loading}
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
          allowClear
        />
      </div>

      <div className="session-list">
        <List
          loading={loading}
          dataSource={filteredSessions}
          renderItem={renderSessionItem}
          locale={{ emptyText: '暂无会话' }}
        />
      </div>
    </div>
  )
}

export default ChatSidebar