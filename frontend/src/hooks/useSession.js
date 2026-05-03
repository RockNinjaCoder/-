import { useState, useCallback } from 'react'
import { getSessions, createSession, deleteSession, updateSession } from '../api/session'
import useSessionStore from '../store/sessionStore'

export function useSession() {
  const { sessions, currentSession, setSessions, setCurrentSession, addSession, updateSession: updateInStore, deleteSession: deleteFromStore } = useSessionStore()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchSessions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getSessions()
      setSessions(data)
    } catch (err) {
      setError(err.message)
      console.error('Fetch sessions error:', err)
    } finally {
      setLoading(false)
    }
  }, [setSessions])

  const create = useCallback(async (title) => {
    setLoading(true)
    setError(null)
    try {
      const newSession = await createSession(title)
      addSession(newSession)
      return newSession
    } catch (err) {
      setError(err.message)
      console.error('Create session error:', err)
      throw err
    } finally {
      setLoading(false)
    }
  }, [addSession])

  const update = useCallback(async (sessionId, updates) => {
    setError(null)
    try {
      const updated = await updateSession(sessionId, updates)
      updateInStore(sessionId, updated)
      return updated
    } catch (err) {
      setError(err.message)
      console.error('Update session error:', err)
      throw err
    }
  }, [updateInStore])

  const remove = useCallback(async (sessionId) => {
    setError(null)
    try {
      await deleteSession(sessionId)
      deleteFromStore(sessionId)
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
      }
    } catch (err) {
      setError(err.message)
      console.error('Delete session error:', err)
      throw err
    }
  }, [deleteFromStore, currentSession, setCurrentSession])

  const select = useCallback((session) => {
    setCurrentSession(session)
  }, [setCurrentSession])

  return {
    sessions,
    currentSession,
    loading,
    error,
    fetchSessions,
    create,
    update,
    remove,
    select
  }
}

export default useSession