import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const chatApi = axios.create({
  baseURL: `${API_BASE_URL}/chat`,
  headers: {
    'Content-Type': 'application/json'
  }
})

chatApi.interceptors.response.use(
  response => response,
  error => {
    console.error('Chat API Error:', error)
    return Promise.reject(error)
  }
)

export const sendMessage = async (sessionId, content, role = 'user') => {
  const response = await chatApi.post('/', { session_id: sessionId, content, role })
  return response.data
}

export const getMessages = async (sessionId, limit = 50, offset = 0) => {
  const response = await chatApi.get(`/session/${sessionId}?limit=${limit}&offset=${offset}`)
  return response.data
}

export default chatApi