import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const queryApi = axios.create({
  baseURL: `${API_BASE_URL}/query`,
  headers: {
    'Content-Type': 'application/json'
  }
})

queryApi.interceptors.response.use(
  response => response,
  error => {
    console.error('Query API Error:', error)
    return Promise.reject(error)
  }
)

export const executeQuery = async (sessionId, query) => {
  const response = await queryApi.post('/', { session_id: sessionId, query })
  return response.data
}

export const getSchemas = async () => {
  const response = await queryApi.get('/schemas')
  return response.data
}

export const registerSchema = async (tableName, columns) => {
  const response = await queryApi.post('/schemas/register', null, {
    params: { table_name: tableName }
  })
  return response.data
}

export default queryApi