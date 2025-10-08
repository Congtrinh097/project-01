import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for file uploads
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const uploadCV = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/upload-cv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  
  return response.data
}

export const getCVs = async () => {
  const response = await api.get('/cv')
  return response.data
}

export const getCV = async (cvId) => {
  const response = await api.get(`/cv/${cvId}`)
  return response.data
}

export const deleteCV = async (cvId) => {
  const response = await api.delete(`/cv/${cvId}`)
  return response.data
}

export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

