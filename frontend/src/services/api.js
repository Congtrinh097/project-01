import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for file uploads
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(
      `Making ${config.method?.toUpperCase()} request to ${config.url}`
    );
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const uploadCV = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload-cv", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const getCVs = async () => {
  const response = await api.get("/cv");
  return response.data;
};

export const getCV = async (cvId) => {
  const response = await api.get(`/cv/${cvId}`);
  return response.data;
};

export const deleteCV = async (cvId) => {
  const response = await api.delete(`/cv/${cvId}`);
  return response.data;
};

export const downloadCV = (cvId) => {
  return `${API_BASE_URL}/download-cv/${cvId}`;
};

export const healthCheck = async () => {
  const response = await api.get("/health");
  return response.data;
};

// Resume generation API calls
export const generateResume = async (inputText) => {
  const response = await api.post("/generate-resume", {
    input_text: inputText,
  });
  return response.data;
};

export const getResumes = async () => {
  const response = await api.get("/resumes");
  return response.data;
};

export const getResume = async (resumeId) => {
  const response = await api.get(`/resumes/${resumeId}`);
  return response.data;
};

export const downloadResume = (resumeId) => {
  return `${API_BASE_URL}/download-resume/${resumeId}`;
};

export const deleteResume = async (resumeId) => {
  const response = await api.delete(`/resumes/${resumeId}`);
  return response.data;
};

// Chatbot API calls
export const sendChatMessage = async (message, conversationHistory = []) => {
  const response = await api.post("/chatbot", {
    message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const sendChatMessageWithAudio = async (
  message,
  conversationHistory = []
) => {
  const response = await api.post("/chatbot/audio", {
    message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const getTTSStatus = async () => {
  const response = await api.get("/chatbot/tts-status");
  return response.data;
};

export const chatbotHealthCheck = async () => {
  const response = await api.get("/chatbot/health");
  return response.data;
};

// Main Bot API calls
export const sendMainBotMessage = async (message, conversationHistory = []) => {
  const response = await api.post("/main-bot", {
    message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const sendMainBotMessageWithAudio = async (
  message,
  conversationHistory = []
) => {
  const response = await api.post("/main-bot/audio", {
    message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const getMainBotTTSStatus = async () => {
  const response = await api.get("/main-bot/tts-status");
  return response.data;
};

export const mainBotHealthCheck = async () => {
  const response = await api.get("/main-bot/health");
  return response.data;
};

// CV Recommendation API calls
export const recommendCVs = async (query, limit = 5) => {
  const response = await api.post("/cv/recommend", {
    query,
    limit,
  });
  return response.data;
};

// Job Recommendation API calls
export const recommendJobs = async (query, limit = 5) => {
  const response = await api.post("/job/recommend", {
    query,
    limit,
  });
  return response.data;
};

export const recommendJobsFromCV = async (file, limit = 5) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("limit", limit);

  const response = await api.post("/job/recommend-from-cv", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

// Job Management API calls
export const getJobs = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.company) params.append("company", filters.company);
  if (filters.location) params.append("location", filters.location);
  if (filters.working_type) params.append("working_type", filters.working_type);
  if (filters.limit) params.append("limit", filters.limit);

  const response = await api.get(`/jobs?${params.toString()}`);
  return response.data;
};

export const getJob = async (jobId) => {
  const response = await api.get(`/jobs/${jobId}`);
  return response.data;
};

export const deleteJob = async (jobId) => {
  const response = await api.delete(`/jobs/${jobId}`);
  return response.data;
};

export const searchJobs = async (query, limit = 20) => {
  const response = await api.get(
    `/jobs/search?q=${encodeURIComponent(query)}&limit=${limit}`
  );
  return response.data;
};

// Job Extraction API calls
export const extractJobs = async (urls) => {
  const response = await api.post("/extract-jobs", {
    urls,
  });
  return response.data;
};

export const getJobExtractionHealth = async () => {
  const response = await api.get("/extract-jobs/health");
  return response.data;
};
