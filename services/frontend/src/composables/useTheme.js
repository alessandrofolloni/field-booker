import { ref, watch } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'dark')

const applyTheme = (t) => {
  document.documentElement.setAttribute('data-theme', t)
  localStorage.setItem('theme', t)
}

// Apply immediately on module load
applyTheme(theme.value)

export function useTheme() {
  const toggleTheme = () => {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    applyTheme(theme.value)
  }

  return { theme, toggleTheme }
}
