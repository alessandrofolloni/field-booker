import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/submit',
            name: 'submit-field',
            component: () => import('../views/SubmitFieldView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/admin',
            name: 'admin',
            component: () => import('../views/AdminDashboardView.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        },
        {
            path: '/analytics',
            name: 'analytics',
            component: () => import('../views/AnalyticsDashboardView.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        }
    ]
})

// Navigation Guards
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()
    const toast = useToast()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        toast.warning("Devi effettuare l'accesso per visualizzare questa pagina.")
        next('/')
        return
    }

    if (to.meta.requiresAdmin && !authStore.isAdmin) {
        toast.error("Accesso negato. Questa pagina è riservata agli amministratori.")
        next('/')
        return
    }

    next()
})

export default router
