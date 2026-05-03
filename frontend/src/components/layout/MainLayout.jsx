import React from 'react'
import ChatSidebar from '../ChatSidebar'
import ChatArea from '../ChatArea'
import VisualizationPanel from '../VisualizationPanel'
import './MainLayout.css'

function MainLayout() {
  return (
    <div className="main-layout">
      <div className="sidebar">
        <ChatSidebar />
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