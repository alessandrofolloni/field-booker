import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
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
            name: 'submit',
            component: () => import('../views/SubmitFieldView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/admin',
            name: 'admin',
            component: () => import('../views/AdminDashboardView.vue'),
            meta: { requiresAuth: true, requiresAdmin: true }
        }
    ]
})

// Navigation Guards
router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    // If route requires authentication
    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        alert("Devi effettuare l'accesso per visualizzare questa pagina.")
        next('/')
        return
    }

    // If route requires admin
    if (to.meta.requiresAdmin && !authStore.isAdmin) {
        alert("Accesso negato. Questa pagina è riservata agli amministratori.")
        next('/')
        return
    }

    next()
})

export default router
