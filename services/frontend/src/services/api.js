import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// Request interceptor to add JWT token
api.interceptors.request.use(
    (config) => {
        const authStore = useAuthStore()
        const token = authStore.token

        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }

        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor to handle 401s (token expiration)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const authStore = useAuthStore()

        if (error.response && error.response.status === 401) {
            // Auto logout if 401 and not already logging out
            authStore.logout()
        }

        return Promise.reject(error)
    }
)

export default api
