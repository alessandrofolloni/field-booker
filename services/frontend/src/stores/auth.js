import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
    const router = useRouter()

    const token = ref(localStorage.getItem('token') || null)
    const user = ref(null)
    const isLoading = ref(true)

    const isAuthenticated = computed(() => !!token.value)
    const isAdmin = computed(() => user.value?.role === 'admin')

    // Decode basic user info from JWT for immediate use
    const setUserFromToken = (jwtStr) => {
        if (!jwtStr) return
        try {
            const decoded = jwtDecode(jwtStr)
            user.value = {
                id: decoded.sub,
                email: decoded.email,
                name: decoded.name,
                role: decoded.role
            }
        } catch (e) {
            console.error('Failed to decode JWT:', e)
            logout()
        }
    }

    const checkAuth = () => {
        isLoading.value = true
        if (token.value) {
            setUserFromToken(token.value)
        }
        isLoading.value = false
    }

    const handleGoogleLogin = async (response) => {
        try {
            isLoading.value = true

            const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
            const res = await axios.post(`${API_BASE_URL}/auth/login/google`, {
                credential: response.credential
            })

            const { access_token } = res.data
            token.value = access_token
            localStorage.setItem('token', access_token)
            setUserFromToken(access_token)

        } catch (error) {
            console.error('Google login failed:', error)
            alert("Login failed. Please try again.")
        } finally {
            isLoading.value = false
        }
    }

    const logout = () => {
        token.value = null
        user.value = null
        localStorage.removeItem('token')
        if (router) router.push('/')
    }

    return {
        token,
        user,
        isLoading,
        isAuthenticated,
        isAdmin,
        checkAuth,
        handleGoogleLogin,
        logout
    }
})
