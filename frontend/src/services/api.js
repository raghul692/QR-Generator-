import axios from 'axios'

const rawBase = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').trim()
const cleanBase = rawBase.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '')
const API_BASE_URL = `${cleanBase}/api/v1`

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor injecting Auth token and Workspace header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('qrm_auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const workspaceId = localStorage.getItem('qrm_current_workspace')
  if (workspaceId) {
    config.headers['X-Workspace-Id'] = workspaceId
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

// ===== Authentication & Identity =====
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  demoLogin: (role = 'admin') => api.post('/auth/demo', { role }),
  getMe: () => api.get('/auth/me'),
}

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
  duplicate: (id) => api.post(`/history/${id}/duplicate`),
  archive: (id) => api.post(`/history/${id}/archive`),
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
  cancel: (id) => api.post(`/bulk/${id}/cancel`),
  getStreamUrl: (id) => `${API_BASE_URL}/bulk/${id}/stream`,
}

// ===== Export =====
export const exportAPI = {
  csv: () => api.get('/export/history/csv', { responseType: 'blob' }),
  excel: () => api.get('/export/history/excel', { responseType: 'blob' }),
  pdf: () => api.get('/export/history/pdf', { responseType: 'blob' }),
  stickerSheet: (layout = '3x7') => api.post('/export/sticker-sheet', {}, { params: { layout }, responseType: 'blob' }),
}

// ===== Templates =====
export const templateAPI = {
  list: () => api.get('/templates'),
  get: (id) => api.get(`/templates/${id}`),
  create: (data) => api.post('/templates', data),
  delete: (id) => api.delete(`/templates/${id}`),
}

// ===== Dynamic QR =====
export const dynamicAPI = {
  list: () => api.get('/dynamic'),
  create: (data) => api.post('/dynamic', data),
  getAnalytics: (id) => api.get(`/dynamic/${id}/analytics`),
  update: (id, data) => api.put(`/dynamic/${id}`, data),
  delete: (id) => api.delete(`/dynamic/${id}`),
  duplicate: (id) => api.post(`/dynamic/${id}/duplicate`),
}

// ===== Landing Pages =====
export const landingPagesAPI = {
  list: () => api.get('/landing-pages'),
  get: (id) => api.get(`/landing-pages/${id}`),
  create: (data) => api.post('/landing-pages', data),
  update: (id, data) => api.put(`/landing-pages/${id}`, data),
  delete: (id) => api.delete(`/landing-pages/${id}`),
  getPublic: (slug) => api.get(`/landing-pages/public/${slug}`),
}

// ===== Digital Menu =====
export const menuAPI = {
  list: () => api.get('/menus'),
  get: (id) => api.get(`/menus/${id}`),
  create: (data) => api.post('/menus', data),
  update: (id, data) => api.put(`/menus/${id}`, data),
  delete: (id) => api.delete(`/menus/${id}`),
  getPublic: (id) => api.get(`/menus/public/${id}`),
}

// ===== vCard Plus =====
export const vcardAPI = {
  generate: (data) => api.post('/vcard/generate', data),
  download: (data) => api.post('/vcard/download', data, { responseType: 'blob' }),
}

// ===== Workspaces & RBAC =====
export const workspaceAPI = {
  list: () => api.get('/workspaces'),
  get: (id) => api.get(`/workspaces/${id}`),
  create: (data) => api.post('/workspaces', data),
  update: (id, data) => api.put(`/workspaces/${id}`, data),
  delete: (id) => api.delete(`/workspaces/${id}`),
  listMembers: (id) => api.get(`/workspaces/${id}/members`),
  addMember: (id, data) => api.post(`/workspaces/${id}/members`, data),
  updateMemberRole: (id, userId, data) => api.patch(`/workspaces/${id}/members/${userId}`, data),
  removeMember: (id, userId) => api.delete(`/workspaces/${id}/members/${userId}`),
}

// ===== Custom Branded Domains =====
export const domainAPI = {
  list: () => api.get('/domains'),
  create: (data) => api.post('/domains', data),
  verify: (id) => api.post(`/domains/${id}/verify`),
  delete: (id) => api.delete(`/domains/${id}`),
}

// ===== Webhooks (Phase 4) =====
export const webhookAPI = {
  list: () => api.get('/webhooks'),
  create: (data) => api.post('/webhooks', data),
  get: (id) => api.get(`/webhooks/${id}`),
  delete: (id) => api.delete(`/webhooks/${id}`),
  test: (id) => api.post(`/webhooks/${id}/test`),
  getDeliveries: (id, limit = 20) => api.get(`/webhooks/${id}/deliveries`, { params: { limit } }),
}

// ===== Retention & GDPR =====
export const retentionAPI = {
  getSummary: () => api.get('/retention/summary'),
  purgeScanLogs: (retentionDays = 90) => api.post('/retention/purge-scan-logs', { retention_days: retentionDays }),
  anonymizeIPs: (days = 30) => api.post('/retention/anonymize-ips', {}, { params: { days } }),
  purgeWorkspace: (confirmId) => api.post('/retention/purge-workspace', { confirm_workspace_id: confirmId }),
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
