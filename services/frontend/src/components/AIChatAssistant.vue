<script setup>
import { ref, nextTick } from 'vue'
import api from '@/services/api'
import { useFieldsStore } from '@/stores/fields'
import { useAuthStore } from '@/stores/auth'
import { useAnalytics } from '@/composables/useAnalytics'

const fieldsStore = useFieldsStore()
const authStore = useAuthStore()
const { trackEvent } = useAnalytics()

const messages = ref([
  {
    role: 'model',
    parts: [{ text: 'Ciao! Sono il tuo assistente AI per i campi sportivi. Chiedimi dove trovare un campo o cercane uno per sport e città!' }],
  },
])
const newMessage = ref('')
const isLoading = ref(false)
const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || isLoading.value) return

  const userText = newMessage.value
  trackEvent('ai_message_sent', null, { message_length: userText.length })

  messages.value.push({ role: 'user', parts: [{ text: userText }] })
  newMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role,
      parts: m.parts,
    }))

    const { data } = await api.post('/ai/chat', { message: userText, history })
    messages.value.push({ role: 'model', parts: [{ text: data.response }] })
    fieldsStore.fetchNearbyFields()
  } catch (error) {
    console.error('AI Error:', error)
    const status = error?.response?.status
    const detail = error?.response?.data?.detail || ''
    let errText = 'Scusa, si è verificato un problema tecnico. Riprova tra qualche istante.'
    if (status === 503 || detail.includes('GOOGLE_API_KEY')) {
      errText = '⚠️ Il servizio AI non è disponibile: chiave API non configurata sul server.'
    } else if (status === 401 || status === 403) {
      errText = 'Accesso negato. Prova ad effettuare il login per usare l\'assistente AI.'
    }
    messages.value.push({ role: 'model', parts: [{ text: errText }] })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

const setHint = (text) => {
  newMessage.value = text
}

const userInitial = () => authStore.user?.name?.[0]?.toUpperCase() || '?'
</script>

<template>
  <div class="ai-assistant-wrapper">
    <div class="chat-container" ref="chatContainer">

      <!-- Empty state (only initial greeting message) -->
      <div v-if="messages.length <= 1 && !isLoading" class="empty-state">
        <div class="empty-icon">🤖</div>
        <p class="empty-text">Chiedimi dove trovare un campo per il tuo sport preferito!</p>
        <div class="hint-chips">
          <span class="hint-chip" @click="setHint('Campi da padel vicino a me')">🎾 Padel vicino a me</span>
          <span class="hint-chip" @click="setHint('Cerco un campo da calcio a Roma')">⚽ Calcio a Roma</span>
          <span class="hint-chip" @click="setHint('Campi da basket a Milano')">🏀 Basket a Milano</span>
        </div>
      </div>

      <!-- Messages -->
      <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
        <div class="avatar-bubble" :class="msg.role === 'model' ? 'avatar-ai' : 'avatar-user'">
          <span v-if="msg.role === 'model'">AI</span>
          <span v-else>{{ userInitial() }}</span>
        </div>
        <div class="message-content" :class="msg.role">
          <p>{{ msg.parts[0].text }}</p>
        </div>
      </div>

      <!-- Typing indicator -->
      <div v-if="isLoading" class="message model">
        <div class="avatar-bubble avatar-ai">AI</div>
        <div class="message-content model thinking">
          <div class="typing-dots">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

    </div>

    <!-- Input bar -->
    <div class="input-area">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="Chiedimi qualcosa… es: Cerco padel a Reggio"
        :disabled="isLoading"
      />
      <button
        class="send-btn"
        @click="sendMessage"
        :disabled="isLoading || !newMessage.trim()"
        title="Invia"
      >
        ➔
      </button>
    </div>
  </div>
</template>

<style scoped>
.ai-assistant-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(15, 23, 42, 0.25);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* ─── Empty state ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  gap: 0.75rem;
  text-align: center;
  padding: 2rem;
  margin: auto;
}

.empty-icon { font-size: 2.5rem; opacity: 0.35; }

.empty-text {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 220px;
}

.hint-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 0.5rem;
}

.hint-chip {
  padding: 7px 14px;
  border-radius: 20px;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-secondary);
  background: var(--glass-bg);
}

.hint-chip:hover {
  border-color: var(--primary-color);
  color: var(--text-primary);
  background: rgba(99, 102, 241, 0.08);
}

/* ─── Messages ─── */
.message {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  max-width: 90%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.model {
  align-self: flex-start;
}

/* Avatars */
.avatar-bubble {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.65rem;
  font-weight: 800;
  flex-shrink: 0;
  letter-spacing: 0.02em;
}

.avatar-ai {
  background: var(--gradient-accent, linear-gradient(135deg, #22c55e, #16a34a));
  color: #000;
}

.avatar-user {
  background: var(--primary-color, #6366f1);
  color: white;
}

/* Bubbles */
.message-content {
  padding: 0.9rem 1.1rem;
  border-radius: 16px;
  max-width: 100%;
}

.message-content.user {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.22), rgba(99, 102, 241, 0.12));
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-bottom-right-radius: 4px;
}

.message-content.model {
  background: var(--color-surface-2, rgba(30, 41, 59, 0.85));
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-bottom-left-radius: 4px;
}

.message-content p {
  margin: 0;
  font-size: 0.93rem;
  line-height: 1.55;
  color: var(--text-primary);
  white-space: pre-wrap;
}

/* Typing indicator */
.thinking { opacity: 0.7; }

.typing-dots {
  display: flex;
  gap: 5px;
  align-items: center;
  padding: 2px 0;
}

.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: typing-dot 1.4s infinite both;
  display: block;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing-dot {
  0%   { opacity: 0.2; transform: scale(0.85); }
  40%  { opacity: 1;   transform: scale(1.1); }
  100% { opacity: 0.2; transform: scale(0.85); }
}

/* ─── Input bar ─── */
.input-area {
  margin: 0.75rem;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--color-surface-2, rgba(30,41,59,0.85));
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 14px;
  padding: 8px 8px 8px 16px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-area:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.input-area input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary, white);
  font-size: 0.93rem;
  padding: 6px 0;
  outline: none;
  min-width: 0;
}

.input-area input::placeholder { color: var(--text-muted); }

.send-btn {
  background: var(--gradient-accent, linear-gradient(135deg, #22c55e, #16a34a));
  color: #000;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 700;
  flex-shrink: 0;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 3px 12px rgba(34, 197, 94, 0.35);
}

.send-btn:disabled { opacity: 0.45; cursor: not-allowed; }
</style>
