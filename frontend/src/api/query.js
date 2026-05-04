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

export const getQueryHistory = async (sessionId, limit = 20) => {
  const response = await queryApi.get(`/history/${sessionId}?limit=${limit}`)
  return response.data
}

export const getSchemas = async () => {
  const response = await queryApi.get('/schemas')
  return response.data
}

export const registerSchema = async (tableName, columns) => {
  const response = await queryApi.post('/schemas/register', {
    table_name: tableName,
    columns: columns
  })
  return response.data
}

export const validateSql = async (sql) => {
  const response = await queryApi.get('/sql/validate', { params: { sql } })
  return response.data
}

export const executeSqlDirect = async (sessionId, sql) => {
  const response = await queryApi.post('/sql/execute', { session_id: sessionId, sql })
  return response.data
}

export default queryApi