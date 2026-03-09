import axios from 'axios'

// Prefer Vite env var. If missing, fallback to backend local port.
const raw = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'
export const API_BASE = raw.replace(/\/+$/, '')

console.log('%c📡 API Connected To:', 'color: #00bfa5; font-weight: bold;', API_BASE)

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Cache-Control': 'no-cache',
  }
})

// ---- Upload PDF ----
export const ingestPdf = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  
  return api.post('/ingest/pdf', fd)  // don't manually set content-type
}

// ---- Teaching routes ----
export const getPlan = (doc_id) => api.get(`/teach/plan/${doc_id}`)

export const nextSlides = (payload) => api.post('/teach/next', payload)

export const sendFeedback = (payload) => api.post('/teach/feedback', payload)
