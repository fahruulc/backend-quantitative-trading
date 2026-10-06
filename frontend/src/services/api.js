import axios from 'axios'

const api = axios.create({
  // Default: relative '/api/v1' → proxied by Vite to localhost:8000 (no CORS, port-independent).
  // Override with VITE_API_BASE_URL env for direct backend access.
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 300000,  // Increased to 2-5 minutes for first load
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now()
    }
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
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.status, error.response.data)
    } else if (error.request) {
      // No response received
      console.error('Network Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Market Analysis APIs
export const marketAPI = {
  // Analysis endpoints
  getMacro: () => api.get('/macro'),
  getSectors: () => api.get('/sectors'),
  getStocks: () => api.get('/stocks'),
  getFullReport: () => api.get('/full-report'),

  // Admin endpoints
  getTokenUsage: () => api.get('/admin/token-usage'),
  getTokenHistory: (days = 7) => api.get('/admin/token-usage/history', { params: { days } }),
  getCacheStats: () => api.get('/admin/cache-stats'),
  getHealth: () => api.get('/admin/health'),
  toggleDemoMode: (enabled) => api.post('/admin/toggle-demo-mode', null, { params: { enabled } }),
  triggerPrefetch: () => api.post('/admin/prefetch-now')
}

export default api
