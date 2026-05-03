import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          console.error('Unauthorized - please login again')
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          console.error('Forbidden - access denied')
          break
        case 404:
          console.error('Not found')
          break
        case 500:
          console.error('Server error')
          break
        default:
          console.error('API Error:', error.message)
      }
    } else if (error.request) {
      console.error('Network error - please check your connection')
    }
    return Promise.reject(error)
  }
)

export default api