/**
 * useAnalytics — fire-and-forget analytics event tracking composable.
 * Never throws, never blocks the UX. Safe to call anywhere.
 */

import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

// Session ID: persists for the browser session, resets on tab close
const getSessionId = () => {
  const KEY = 'fb_session_id'
  let sid = sessionStorage.getItem(KEY)
  if (!sid) {
    sid = 'sess_' + Math.random().toString(36).slice(2) + Date.now().toString(36)
    sessionStorage.setItem(KEY, sid)
  }
  return sid
}

export function useAnalytics() {
  /**
   * Track a user interaction event.
   * @param {string} eventType - e.g. 'field_viewed', 'booking_clicked'
   * @param {string|null} fieldId - UUID of the related field, if any
   * @param {object} metadata - additional context (field_name, url, etc.)
   */
  const trackEvent = (eventType, fieldId = null, metadata = {}) => {
    const authStore = useAuthStore()

    const payload = {
      event_type: eventType,
      field_id: fieldId || null,
      session_id: getSessionId(),
      metadata: {
        ...metadata,
        user_id: authStore.user?.id || null,
      },
    }

    // Fire and forget — errors are silently swallowed
    api.post('/fields/analytics/event', payload).catch(() => {})
  }

  return { trackEvent }
}
