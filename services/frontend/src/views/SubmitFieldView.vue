<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFieldsStore } from '@/stores/fields'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const fieldsStore = useFieldsStore()

const fieldId = route.query.field_id
const isUpdateMode = computed(() => !!fieldId)

const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const form = ref({
  name: '',
  description: '',
  address: '',
  city: '',
  latitude: null,
  longitude: null,
  phone: '',
  email: '',
  website: '',
  booking_url: '',
  price_info: '',
  sport_ids: []
})

onMounted(async () => {
  if (fieldsStore.sports.length === 0) {
    await fieldsStore.fetchSports()
  }
  
  if (isUpdateMode.value) {
    // If we have fieldId, try to find it in store or fetch details
    try {
      // For simplicity, find in already loaded fields or fetch specifically
      const existingField = fieldsStore.fields.find(f => f.id === fieldId)
      if (existingField) {
        fillForm(existingField)
      } else {
        // Fetch specific field if not in list
        const { data } = await api.get(`/fields/${fieldId}`)
        fillForm(data)
      }
    } catch (err) {
      console.error("Failed to load field for correction", err)
      errorMessage.value = "Impossibile caricare i dati del campo originale."
    }
  } else if (fieldsStore.userLocation.lat) {
    form.value.latitude = fieldsStore.userLocation.lat
    form.value.longitude = fieldsStore.userLocation.lng
  }
})

const fillForm = (data) => {
  form.value = {
    name: data.name,
    description: data.description || '',
    address: data.address,
    city: data.city,
    latitude: data.latitude,
    longitude: data.longitude,
    phone: data.phone || '',
    email: data.email || '',
    website: data.website || '',
    booking_url: data.booking_url || '',
    price_info: data.price_info || '',
    sport_ids: data.sports ? data.sports.map(s => s.id) : []
  }
}

const submitField = async () => {
  if (form.value.sport_ids.length === 0) {
    errorMessage.value = "Seleziona almeno uno sport."
    return
  }
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    await api.post('/submissions/', {
      field_data: form.value,
      field_id: fieldId || null,
      submission_type: isUpdateMode.value ? 'update' : 'new'
    })
    
    successMessage.value = isUpdateMode.value 
      ? "Grazie! La tua correzione è stata inviata ed è in attesa di revisione."
      : "Grazie! Il nuovo campo è stato segnalato ed è in attesa di approvazione."
    
    setTimeout(() => {
      router.push('/')
    }, 3000)
    
  } catch (err) {
    console.error(err)
    errorMessage.value = "Errore durante l'invio. Riprova più tardi."
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="submit-container animate-fade-in">
    <div class="submit-card glass-panel">
      <h1>{{ isUpdateMode ? '🛠️ Suggerisci una Correzione' : '🏟️ Segnala un Nuovo Campo' }}</h1>
      <p class="subtitle">
        {{ isUpdateMode 
          ? 'Hai notato un errore? Inviaci i dati corretti e un admin li verificherà.' 
          : 'Aiutaci a migliorare la mappa segnalando un campo sportivo che conosci.' 
        }}
      </p>
      
      <div v-if="successMessage" class="alert success">{{ successMessage }}</div>
      <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>
      
      <form @submit.prevent="submitField" v-if="!successMessage" class="modern-form">
        
        <div class="form-grid">
          <div class="form-section glass-card">
            <h3>📝 Informazioni di Base</h3>
            <div class="form-group">
              <label>Nome del Campo *</label>
              <input type="text" v-model="form.name" required placeholder="Es. Centro Sportivo Roma" class="glass-input">
            </div>
            
            <div class="form-group">
              <label>Descrizione</label>
              <textarea v-model="form.description" rows="3" placeholder="Dettagli sul campo..." class="glass-input"></textarea>
            </div>
          </div>

          <div class="form-section glass-card">
            <h3>📍 Ubicazione</h3>
            <div class="form-group">
              <label>Indirizzo *</label>
              <input type="text" v-model="form.address" required placeholder="Es. Via Garibaldi 10" class="glass-input">
            </div>
            <div class="form-group">
              <label>Città *</label>
              <input type="text" v-model="form.city" required placeholder="Es. Roma" class="glass-input">
            </div>
            <div class="form-row">
               <div class="form-group half">
                <label>Latitudine *</label>
                <input type="number" step="any" v-model="form.latitude" required class="glass-input">
              </div>
              <div class="form-group half">
                <label>Longitudine *</label>
                <input type="number" step="any" v-model="form.longitude" required class="glass-input">
              </div>
            </div>
          </div>

          <div class="form-section glass-card full-width">
            <h3>🎾 Sport Disponibili *</h3>
            <div class="sports-grid">
              <label v-for="sport in fieldsStore.sports" :key="sport.id" 
                     class="sport-checkbox" :class="{ active: form.sport_ids.includes(sport.id) }">
                <input type="checkbox" :value="sport.id" v-model="form.sport_ids">
                <span class="s-icon">{{ sport.icon }}</span>
                <span class="s-name">{{ sport.name }}</span>
              </label>
            </div>
          </div>

          <div class="form-section glass-card full-width">
            <h3>📞 Contatti e Tariffe</h3>
            <div class="form-row">
              <div class="form-group third">
                <label>Telefono</label>
                <input type="tel" v-model="form.phone" class="glass-input">
              </div>
              <div class="form-group third">
                <label>Sito Web</label>
                <input type="url" v-model="form.website" class="glass-input">
              </div>
              <div class="form-group third">
                <label>Link Prenotazione</label>
                <input type="url" v-model="form.booking_url" class="glass-input" placeholder="Es. Playtomic...">
              </div>
            </div>
            <div class="form-group">
              <label>Info Tariffe</label>
              <input type="text" v-model="form.price_info" class="glass-input" placeholder="Es. 10€ l'ora, noleggio racchette incluso">
            </div>
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Inviando...' : (isUpdateMode ? 'Invia Correzione' : 'Crea Segnalazione') }}
          </button>
          <button type="button" class="btn-secondary" @click="router.push('/')">Annulla</button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.submit-container {
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  min-height: calc(100vh - 80px);
}

.submit-card {
  padding: 2.5rem;
  border-radius: 24px;
}

h1 {
  margin-bottom: 0.5rem;
  font-size: 2rem;
  background: linear-gradient(to right, #fff, var(--text-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--text-muted);
  margin-bottom: 2.5rem;
  font-size: 1.1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.full-width {
  grid-column: span 2;
}

.form-section {
  padding: 1.5rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
}

h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  font-weight: 700;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.half { flex: 1; }
.third { flex: 1; }

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.glass-input {
  width: 100%;
  padding: 12px 16px;
}

.sports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.sport-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.sport-checkbox:hover {
  background: rgba(255, 255, 255, 0.07);
}

.sport-checkbox.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--primary-color);
  color: var(--text-primary);
}

.sport-checkbox input { display: none; }

.actions {
  margin-top: 3rem;
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.actions button {
  min-width: 200px;
  padding: 14px;
  font-size: 1rem;
}

.alert {
  padding: 1.25rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  font-weight: 600;
}

.success {
  background: rgba(34, 197, 94, 0.1);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.error {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

@media (max-width: 768px) {
  .form-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: auto; }
  .form-row { flex-direction: column; }
}
</style>
