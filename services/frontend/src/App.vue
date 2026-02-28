<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import ToastContainer from '@/components/ToastContainer.vue'

const authStore = useAuthStore()

onMounted(() => {
  authStore.checkAuth()
})

const userInitial = () => authStore.user?.name?.[0]?.toUpperCase() || '?'
</script>

<template>
  <div class="app-container">
    <header class="navbar glass-panel">
      <!-- Logo -->
      <div class="logo">
        <router-link to="/">
          <div class="logo-icon">🏟️</div>
          <div class="logo-text">
            <span class="brand">Field</span>
            <span class="sub">Booker</span>
          </div>
        </router-link>
      </div>

      <!-- Nav -->
      <nav class="nav-links">
        <div v-if="authStore.isLoading" class="loading-auth">
          <div class="shimmer"></div>
        </div>

        <template v-else-if="authStore.isAuthenticated">
          <div class="user-profile">
            <!-- Admin nav links -->
            <div class="admin-nav" v-if="authStore.isAdmin">
              <router-link to="/admin" class="nav-pill">Dashboard</router-link>
              <router-link to="/analytics" class="nav-pill analytics-pill">📊 Analytics</router-link>
            </div>

            <!-- Report field button -->
            <router-link :to="{ name: 'submit-field' }" class="btn-primary">
              <span>Segnala Campo</span>
            </router-link>

            <!-- User avatar + logout -->
            <div class="user-section">
              <div class="user-avatar" :title="authStore.user?.name">
                {{ userInitial() }}
              </div>
              <span v-if="authStore.isAdmin" class="admin-badge">ADMIN</span>
              <button @click="authStore.logout" class="btn-logout" title="Esci">🚪</button>
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

/* ─── Navbar ─── */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 1.75rem;
  height: 60px;
  z-index: 1000;
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 1px 0 rgba(255,255,255,0.04), 0 4px 24px rgba(0,0,0,0.25);
  flex-shrink: 0;
}

/* ─── Logo ─── */
.logo a {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none;
}

.logo-icon {
  font-size: 1.6rem;
  filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.35));
}

.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.brand {
  font-size: 1.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #fff 0%, var(--primary-color, #6366f1) 120%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.sub {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--primary-color);
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

/* ─── Nav links ─── */
.nav-links {
  display: flex;
  align-items: center;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.admin-nav {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-pill {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  background: var(--glass-bg);
}

.nav-pill:hover {
  color: var(--text-primary);
  border-color: var(--color-border-hover, rgba(255,255,255,0.18));
  background: rgba(255,255,255,0.06);
}

.nav-pill.router-link-active {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.analytics-pill.router-link-active {
  border-color: var(--color-accent, #22c55e);
  color: var(--color-accent, #22c55e);
  background: rgba(34, 197, 94, 0.08);
}

/* ─── User section ─── */
.user-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--gradient-accent, linear-gradient(135deg, #22c55e, #16a34a));
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.78rem;
  font-weight: 800;
  cursor: default;
  flex-shrink: 0;
}

.admin-badge {
  font-size: 0.58rem;
  font-weight: 800;
  background: var(--color-accent, #22c55e);
  color: #000;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.05em;
}

.btn-logout {
  font-size: 1.1rem;
  padding: 6px;
  border-radius: 8px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  transition: all 0.2s;
  cursor: pointer;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.08);
}

/* ─── Google login ─── */
.btn-google {
  background: white;
  color: #1e293b;
  padding: 9px 18px;
  border-radius: var(--border-radius, 12px);
  font-weight: 600;
  font-size: 0.88rem;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: var(--shadow-md);
  transition: all 0.2s;
}

.btn-google:hover {
  background: #f8fafc;
  transform: translateY(-1px);
  box-shadow: var(--shadow-lg);
}

/* ─── Loading shimmer ─── */
.loading-auth {
  width: 180px;
  height: 36px;
}

.shimmer {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, var(--glass-bg) 25%, rgba(255,255,255,0.05) 50%, var(--glass-bg) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 20px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ─── Main content ─── */
.main-content {
  flex: 1;
  overflow: hidden;
  position: relative;
}

/* ─── Page transitions ─── */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
