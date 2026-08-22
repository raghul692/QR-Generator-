import axios from 'axios'

const API_BASE_URL = 'https://qr-generator-2-8sv7.onrender.com'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// ===== QR Generation =====
export const qrAPI = {
  getTypes: () => api.get('/qr/types'),
  getType: (type) => api.get(`/qr/types/${type}`),
  preview: (data) => api.post('/qr/preview', data),
  generate: (data) => api.post('/qr/generate', data),
  regenerate: (id) => api.post(`/qr/regenerate/${id}`),
  download: (id, fmt) => api.get(`/qr/download/${id}`, { params: { fmt }, responseType: 'blob' }),
}

// ===== QR History =====
export const historyAPI = {
  list: (params) => api.get('/history/', { params }),
  get: (id) => api.get(`/history/${id}`),
  update: (id, data) => api.patch(`/history/${id}`, data),
  delete: (id) => api.delete(`/history/${id}`),
  toggleFavorite: (id) => api.post(`/history/${id}/favorite`),
}

// ===== Categories =====
export const categoryAPI = {
  list: () => api.get('/categories/'),
  get: (id) => api.get(`/categories/${id}`),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`),
}

// ===== Scanner =====
export const scannerAPI = {
  scan: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/scanner/scan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ===== Dashboard & Analytics =====
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getCharts: () => api.get('/dashboard/charts'),
  getAnalytics: () => api.get('/dashboard/analytics'),
}

// ===== Bulk =====
export const bulkAPI = {
  list: () => api.get('/bulk/'),
  get: (id) => api.get(`/bulk/${id}`),
  upload: (formData) => api.post('/bulk/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  }),
  download: (id) => api.get(`/bulk/${id}/download`, { responseType: 'blob' }),
}

// ===== Export =====
export const exportAPI = {
  csv: () => api.get('/export/history/csv', { responseType: 'blob' }),
  excel: () => api.get('/export/history/excel', { responseType: 'blob' }),
  pdf: () => api.get('/export/history/pdf', { responseType: 'blob' }),
  stickerSheet: () => api.post('/export/sticker-sheet', {}, { responseType: 'blob' }),
}

// ===== Dynamic QR =====
export const dynamicAPI = {
  create: (data) => api.post('/dynamic', data),
  getAnalytics: (id) => api.get(`/dynamic/${id}/analytics`),
  update: (id, data) => api.put(`/dynamic/${id}`, data),
}

// ===== API Keys =====
export const apiKeyAPI = {
  list: () => api.get('/keys'),
  create: (data) => api.post('/keys', data),
  revoke: (id) => api.delete(`/keys/${id}`),
}

// ===== Backup =====
export const backupAPI = {
  list: () => api.get('/backup/'),
  create: (data) => api.post('/backup/', data),
  restore: (id) => api.post(`/backup/${id}/restore`),
  download: (id) => api.get(`/backup/${id}/download`, { responseType: 'blob' }),
}

// ===== Settings =====
export const settingsAPI = {
  list: () => api.get('/settings/'),
  getDict: () => api.get('/settings/dict'),
  getByCategory: (cat) => api.get(`/settings/${cat}`),
  update: (key, value) => api.put(`/settings/${key}`, { value }),
  bulkUpdate: (settings) => api.put('/settings/', { settings }),
}

export default api
