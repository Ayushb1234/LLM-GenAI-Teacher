import axios from 'axios'

const raw = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
const API_BASE = raw.replace(/\/+$/, '')

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

export const ingestPdf = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/ingest/pdf', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getPlan = (doc_id) => api.get(`/teach/plan/${doc_id}`)

export const nextSlides = (payload) => api.post('/teach/next', payload)

export const sendFeedback = (payload) => api.post('/teach/feedback', payload)
