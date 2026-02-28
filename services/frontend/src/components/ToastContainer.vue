<script setup>
import { useToast } from '@/composables/useToast'

const { toasts, remove } = useToast()

const icons = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ'
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="toast"
          :class="`toast-${toast.type}`"
          @click="remove(toast.id)"
        >
          <span class="toast-icon">{{ icons[toast.type] }}</span>
          <span class="toast-msg">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 88px;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 260px;
  max-width: 420px;
  cursor: pointer;
  pointer-events: all;
  backdrop-filter: blur(12px);
  border: 1px solid transparent;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.toast-success {
  background: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
  color: #4ade80;
}

.toast-error {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}

.toast-warning {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}

.toast-info {
  background: rgba(99, 102, 241, 0.15);
  border-color: rgba(99, 102, 241, 0.4);
  color: #a5b4fc;
}

.toast-icon {
  font-size: 1rem;
  font-weight: 800;
  flex-shrink: 0;
}

.toast-msg {
  flex: 1;
  line-height: 1.4;
}

/* Transitions */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
