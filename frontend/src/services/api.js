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

// Resume generation API calls
export const generateResume = async (inputText) => {
  const response = await api.post('/generate-resume', {
    input_text: inputText,
  })
  return response.data
}

export const getResumes = async () => {
  const response = await api.get('/resumes')
  return response.data
}

export const getResume = async (resumeId) => {
  const response = await api.get(`/resumes/${resumeId}`)
  return response.data
}

export const downloadResume = (resumeId) => {
  return `${API_BASE_URL}/download-resume/${resumeId}`
}

export const deleteResume = async (resumeId) => {
  const response = await api.delete(`/resumes/${resumeId}`)
  return response.data
}

// Chatbot API calls
export const sendChatMessage = async (message, conversationHistory = []) => {
  const response = await api.post('/chatbot', {
    message,
    conversation_history: conversationHistory,
  })
  return response.data
}

export const chatbotHealthCheck = async () => {
  const response = await api.get('/chatbot/health')
  return response.data
}

