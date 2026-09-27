import axios from 'axios'
import toast from 'react-hot-toast'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 180000,  // 3 minutes — AI generation can take 30-60s on free tier
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.detail || err.message || 'Something went wrong'
    toast.error(msg)
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: (userId) => api.get(`/auth/profile/${userId}`),
  updateProfile: (userId, data) => api.put(`/auth/profile/${userId}`, data),
}

// ── Resume ────────────────────────────────────────────────────────────────
export const resumeAPI = {
  upload: (formData) =>
    api.post('/resume/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  get: (resumeId) => api.get(`/resume/${resumeId}`),
  getUserResumes: (userId) => api.get(`/resume/user/${userId}`),
  improve: (data) => api.post('/resume/improve', data),
}

// ── Skill Gap ─────────────────────────────────────────────────────────────
export const skillGapAPI = {
  analyze: (data) => api.post('/skill-gap/analyze', data),
  get: (id) => api.get(`/skill-gap/${id}`),
  getUserGaps: (userId) => api.get(`/skill-gap/user/${userId}`),
}

// ── Plan ──────────────────────────────────────────────────────────────────
export const planAPI = {
  generate: (data) => api.post('/plan/generate', data),
  get: (planId) => api.get(`/plan/${planId}`),
  getUserPlans: (userId) => api.get(`/plan/user/${userId}`),
  completeDay: (planId, data) => api.post(`/plan/${planId}/complete-day`, data),
}

// ── Questions ─────────────────────────────────────────────────────────────
export const questionsAPI = {
  generate: (data) => api.post('/questions/generate', data),
  attempt: (data) => api.post('/questions/attempt', data),
  getCategories: () => api.get('/questions/categories'),
}

// ── Performance ───────────────────────────────────────────────────────────
export const performanceAPI = {
  logSession: (data) => api.post('/performance/session', data),
  getReadiness: (userId) => api.get(`/performance/readiness/${userId}`),
  getWeakness: (userId) => api.get(`/performance/weakness/${userId}`),
  getHistory: (userId) => api.get(`/performance/history/${userId}`),
  getTopics: (userId) => api.get(`/performance/topics/${userId}`),
}

// ── Mock Interview ────────────────────────────────────────────────────────
export const interviewAPI = {
  start: (data) => api.post('/interview/start', data),
  message: (data) => api.post('/interview/message', data),
  end: (interviewId) => api.post(`/interview/${interviewId}/end`),
  get: (interviewId) => api.get(`/interview/${interviewId}`),
  getUserInterviews: (userId) => api.get(`/interview/user/${userId}`),
}

// ── RAG ───────────────────────────────────────────────────────────────────
export const ragAPI = {
  query: (data) => api.post('/rag/query', data),
  seed: () => api.post('/rag/seed'),
}

// ── Dashboard ─────────────────────────────────────────────────────────────
export const dashboardAPI = {
  get: (userId) => api.get(`/dashboard/${userId}`),
}

export default api
