import { useState, useCallback, useRef } from 'react'
import { sendMessage, getMessages } from '../api/chat'
import { fetchStream } from '../api/stream'
import useChatStore from '../store/chatStore'
import useSessionStore from '../store/sessionStore'

export function useChat() {
  const { messages, setMessages, addMessage, updateMessage, clearMessages, setLoading, setStreaming } = useChatStore()
  const { currentSession } = useSessionStore()
  const [loading, setLocalLoading] = useState(false)
  const [streaming, setLocalStreaming] = useState(false)
  const [error, setError] = useState(null)
  const streamControllerRef = useRef(null)

  const loadMessages = useCallback(async (sessionId) => {
    setLocalLoading(true)
    setError(null)
    try {
      const data = await getMessages(sessionId)
      setMessages(data)
    } catch (err) {
      setError(err.message)
      console.error('Load messages error:', err)
    } finally {
      setLocalLoading(false)
    }
  }, [setMessages])

  const send = useCallback(async (content) => {
    if (!currentSession) {
      setError('No active session')
      return
    }

    if (!content.trim()) {
      setError('Empty message')
      return
    }

    setError(null)
    setLocalLoading(true)

    const userMessage = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.id,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }

    addMessage(userMessage)

    try {
      const response = await sendMessage(currentSession.id, content)
      addMessage(response)
      setLocalLoading(false)

      setLocalStreaming(true)
      setStreaming(true)

      streamControllerRef.current = fetchStream(
        currentSession.id,
        (data) => {
          if (data.type === 'message' && data.content) {
            const msgs = useChatStore.getState().messages
            const lastMsg = msgs[msgs.length - 1]
            if (lastMsg?.role === 'assistant' && !lastMsg.id.startsWith('temp')) {
              updateMessage(lastMsg.id, { content: lastMsg.content + data.content })
            }
          }
        },
        (err) => {
          console.error('Stream error:', err)
          setError(err.message)
          setLocalStreaming(false)
          setStreaming(false)
        },
        () => {
          setLocalStreaming(false)
          setStreaming(false)
        }
      )
    } catch (err) {
      setError(err.message)
      console.error('Send message error:', err)
      setLocalLoading(false)
      setLocalStreaming(false)
      setStreaming(false)
    }
  }, [currentSession, addMessage, updateMessage, setStreaming])

  const stopStream = useCallback(() => {
    if (streamControllerRef.current) {
      streamControllerRef.current.abort()
      streamControllerRef.current = null
    }
    setLocalStreaming(false)
    setStreaming(false)
  }, [setStreaming])

  const clear = useCallback(() => {
    clearMessages()
  }, [clearMessages])

  return {
    messages,
    loading,
    streaming,
    error,
    loadMessages,
    send,
    stopStream,
    clear
  }
}

export default useChat