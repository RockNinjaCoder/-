import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const sessionApi = axios.create({
  baseURL: `${API_BASE_URL}/sessions`,
  headers: {
    'Content-Type': 'application/json'
  }
})

sessionApi.interceptors.response.use(
  response => response,
  error => {
    console.error('Session API Error:', error)
    return Promise.reject(error)
  }
)

export const getSessions = async () => {
  const response = await sessionApi.get('/')
  return response.data
}

export const createSession = async (title) => {
  const response = await sessionApi.post('/', { title })
  return response.data
}

export const getSession = async (sessionId) => {
  const response = await sessionApi.get(`/${sessionId}`)
  return response.data
}

export const updateSession = async (sessionId, updates) => {
  const response = await sessionApi.put(`/${sessionId}`, updates)
  return response.data
}

export const deleteSession = async (sessionId) => {
  const response = await sessionApi.delete(`/${sessionId}`)
  return response.data
}

export default sessionApi