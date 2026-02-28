<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ToastContainer from '@/components/ToastContainer.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.checkAuth()
})
</script>

<template>
  <div class="app-container">
    <header class="navbar glass-panel">
      <div class="logo">
        <router-link to="/">
          <div class="logo-icon">🏟️</div>
          <div class="logo-text">
            <span class="brand">Field</span>
            <span class="sub">Booker</span>
          </div>
        </router-link>
      </div>

      <nav class="nav-links">
        <div v-if="authStore.isLoading" class="loading-auth">
          <div class="shimmer"></div>
        </div>

        <template v-else-if="authStore.isAuthenticated">
          <div class="user-profile">
            <div class="user-info">
              <span class="user-name">{{ authStore.user?.name }}</span>
              <span v-if="authStore.isAdmin" class="admin-badge">ADMIN</span>
            </div>
            
            <div class="nav-actions">
              <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link admin-link">
                Dashboard
              </router-link>
              
              <router-link :to="{ name: 'submit-field' }" class="btn-primary">
                <span>Segnala Campo</span>
              </router-link>
              
              <button @click="authStore.logout" class="btn-icon" title="Esci">
                🚪
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <GoogleLogin :callback="authStore.handleGoogleLogin" prompt>
            <button class="btn-google">
              <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google" width="18" height="18">
              <span>Accedi con Google</span>
            </button>
          </GoogleLogin>
        </template>
      </nav>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <ToastContainer />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: var(--background-color);
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: var(--nav-height);
  z-index: 1000;
  border-bottom: 1px solid var(--glass-border);
}

.logo a {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
}

.logo-icon {
  font-size: 1.75rem;
  filter: drop-shadow(0 0 8px rgba(99, 102, 241, 0.3));
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.brand {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.sub {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.admin-badge {
  font-size: 0.65rem;
  font-weight: 800;
  background: var(--accent-color);
  color: #000;
  padding: 1px 4px;
  border-radius: 4px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-google {
  background: white;
  color: #1e293b;
  padding: 10px 18px;
  border-radius: var(--border-radius);
  font-weight: 600;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: var(--shadow-md);
  transition: all 0.2s ease;
}

.btn-google:hover {
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

.btn-icon {
  font-size: 1.25rem;
  padding: 8px;
  border-radius: 50%;
  background: var(--glass-bg);
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
}

.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* Page Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
