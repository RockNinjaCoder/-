import React, { useState } from 'react'
import ChatSidebar from '../ChatSidebar'
import ChatArea from '../ChatArea'
import VisualizationPanel from '../VisualizationPanel'
import useSessionStore from '../../store/sessionStore'
import './MainLayout.css'

function MainLayout() {
  const { currentSession, setCurrentSession } = useSessionStore()

  const handleSelectSession = (session) => {
    setCurrentSession(session)
  }

  return (
    <div className="main-layout">
      <div className="sidebar">
        <ChatSidebar onSelectSession={handleSelectSession} />
      </div>
      <div className="chat-area">
        <ChatArea />
      </div>
      <div className="visualization">
        <VisualizationPanel />
      </div>
    </div>
  )
}

export default MainLayout