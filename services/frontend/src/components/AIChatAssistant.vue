<script setup>
import { ref, watch, onUpdated, nextTick } from 'vue'
import api from '@/services/api'
import { useFieldsStore } from '@/stores/fields'

const fieldsStore = useFieldsStore()
const messages = ref([
  { role: 'model', parts: [{ text: "Ciao! Sono il tuo assistente AI. Chiedimi pure dove trovare un campo o cercane uno per sport o città!" }] }
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
  messages.value.push({ role: 'user', parts: [{ text: userText }] })
  newMessage.value = ''
  isLoading.value = true
  
  scrollToBottom()

  try {
    // History format for Gemini service
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      parts: m.parts
    }))

    const { data } = await api.post('/ai/chat', {
      message: userText,
      history: history
    })

    messages.value.push({ role: 'model', parts: [{ text: data.response }] })
    
    // Proactive update: AI might have called tools that changed filters
    // We should refresh the fields list if the AI says it found something
    fieldsStore.fetchNearbyFields()
    
  } catch (error) {
    console.error("AI Error:", error)
    messages.value.push({ 
      role: 'model', 
      parts: [{ text: "Scusa, ho avuto un problema tecnico. Assicurati che l'API Key di Gemini sia configurata correttamente." }] 
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}
</script>

<template>
  <div class="ai-assistant-wrapper">
    <div class="chat-container" ref="chatContainer">
      <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
        <div class="message-content glass-card">
          <span class="avatar" v-if="msg.role === 'model'">🤖</span>
          <span class="avatar" v-else>👤</span>
          <p>{{ msg.parts[0].text }}</p>
        </div>
      </div>
      
      <div v-if="isLoading" class="message model">
        <div class="message-content glass-card thinking">
          <span class="avatar">🤖</span>
          <div class="typing-dots">
            <span>.</span><span>.</span><span>.</span>
          </div>
        </div>
      </div>
    </div>

    <div class="input-area glass-input">
      <input 
        v-model="newMessage" 
        @keyup.enter="sendMessage" 
        placeholder="Chiedimi qualcosa... es: Cerco padel a Reggio"
        :disabled="isLoading"
      />
      <button @click="sendMessage" :disabled="isLoading || !newMessage.trim()">
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
  background: rgba(15, 23, 42, 0.2);
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
}

.message.model {
  align-self: flex-start;
}

.message-content {
  padding: 1rem;
  border-radius: 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.user .message-content {
  background: rgba(99, 102, 241, 0.2);
  border-bottom-right-radius: 4px;
}

.model .message-content {
  background: rgba(255, 255, 255, 0.05);
  border-bottom-left-radius: 4px;
}

.avatar { font-size: 1.2rem; line-height: 1.5; }

p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.input-area {
  margin: 1rem;
  display: flex;
  gap: 10px;
  padding: 6px 16px;
}

input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  padding: 10px 0;
  outline: none;
}

button {
  background: var(--primary-color);
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: transform 0.2s;
}

button:hover:not(:disabled) {
  transform: scale(1.1);
}

/* Typing animation */
.thinking { opacity: 0.7; }
.typing-dots span {
  animation: blink 1.4s infinite both;
  font-size: 1.5rem;
  font-weight: bold;
}
.typing-dots span:nth-child(2) { animation-delay: .2s; }
.typing-dots span:nth-child(3) { animation-delay: .4s; }

@keyframes blink {
  0% { opacity: .2; }
  20% { opacity: 1; }
  100% { opacity: .2; }
}
</style>
