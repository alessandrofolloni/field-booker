<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useFieldsStore } from '@/stores/fields'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'
import L from 'leaflet'

const router = useRouter()
const route = useRoute()
const fieldsStore = useFieldsStore()
const toast = useToast()

const fieldId = route.query.field_id
const isUpdateMode = computed(() => !!fieldId)

const isSubmitting = ref(false)
const isGeocoding = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Map refs
const mapContainer = ref(null)
let mapInstance = null
let markerInstance = null

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
  surface_type: '',
  is_indoor: null,
  notes: '',
  sport_ids: []
})

const surfaceTypes = [
  { value: 'grass', label: '🌿 Erba naturale' },
  { value: 'artificial_grass', label: '🟢 Erba sintetica' },
  { value: 'hard', label: '🔵 Cemento / Hard' },
  { value: 'clay', label: '🟠 Terra rossa' },
  { value: 'parquet', label: '🪵 Parquet' },
  { value: 'sand', label: '🏖️ Sabbia' },
  { value: 'other', label: '⚙️ Altro' },
]

const initMap = async (lat, lng) => {
  await nextTick()
  if (!mapContainer.value) return

  const center = [lat || 41.9028, lng || 12.4964]

  if (!mapInstance) {
    mapInstance = L.map(mapContainer.value, { center, zoom: 15, zoomControl: true })

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '© OpenStreetMap contributors © CARTO',
      maxZoom: 19,
    }).addTo(mapInstance)

    markerInstance = L.marker(center, { draggable: true }).addTo(mapInstance)
    markerInstance.bindPopup('<b>Trascina per precisare la posizione</b>').openPopup()

    markerInstance.on('dragend', (e) => {
      const pos = e.target.getLatLng()
      form.value.latitude = parseFloat(pos.lat.toFixed(6))
      form.value.longitude = parseFloat(pos.lng.toFixed(6))
    })

    mapInstance.on('click', (e) => {
      markerInstance.setLatLng(e.latlng)
      form.value.latitude = parseFloat(e.latlng.lat.toFixed(6))
      form.value.longitude = parseFloat(e.latlng.lng.toFixed(6))
    })
  } else {
    mapInstance.setView(center, 15)
    markerInstance.setLatLng(center)
  }
}

const geocodeAndShow = async () => {
  if (!form.value.address && !form.value.city) {
    toast.warning('Inserisci almeno un indirizzo o una città per trovare la posizione.')
    return
  }
  const query = [form.value.address, form.value.city].filter(Boolean).join(', ')
  isGeocoding.value = true
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`,
      { headers: { 'User-Agent': 'FieldBooker/1.0' } }
    )
    const data = await res.json()
    if (data && data.length > 0) {
      const { lat, lon } = data[0]
      form.value.latitude = parseFloat(parseFloat(lat).toFixed(6))
      form.value.longitude = parseFloat(parseFloat(lon).toFixed(6))
      await initMap(form.value.latitude, form.value.longitude)
      toast.success('Posizione trovata! Trascina il marker per precisare.')
    } else {
      toast.error(`Indirizzo non trovato: "${query}". Prova con una città o indirizzo più generico.`)
    }
  } catch {
    toast.error('Errore durante la geocodifica. Controlla la connessione.')
  } finally {
    isGeocoding.value = false
  }
}

const useGPSLocation = () => {
  if (!navigator.geolocation) {
    toast.error('La geolocalizzazione non è supportata dal browser.')
    return
  }
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      form.value.latitude = parseFloat(pos.coords.latitude.toFixed(6))
      form.value.longitude = parseFloat(pos.coords.longitude.toFixed(6))
      await initMap(form.value.latitude, form.value.longitude)
      toast.success('Posizione GPS acquisita!')
    },
    () => toast.error('Impossibile ottenere la posizione GPS.')
  )
}

onMounted(async () => {
  if (fieldsStore.sports.length === 0) {
    await fieldsStore.fetchSports()
  }

  if (isUpdateMode.value) {
    try {
      const existingField = fieldsStore.fields.find(f => f.id === fieldId)
      if (existingField) {
        await fillForm(existingField)
      } else {
        const { data } = await api.get(`/fields/${fieldId}`)
        await fillForm(data)
      }
    } catch (err) {
      console.error('Failed to load field for correction', err)
      toast.error('Impossibile caricare i dati del campo originale.')
    }
  } else if (fieldsStore.userLocation.lat) {
    form.value.latitude = fieldsStore.userLocation.lat
    form.value.longitude = fieldsStore.userLocation.lng
    await initMap(form.value.latitude, form.value.longitude)
  }
})

const fillForm = async (data) => {
  form.value = {
    name: data.name || '',
    description: data.description || '',
    address: data.address || '',
    city: data.city || '',
    latitude: data.latitude || null,
    longitude: data.longitude || null,
    phone: data.phone || '',
    email: data.email || '',
    website: data.website || '',
    booking_url: data.booking_url || '',
    price_info: data.price_info || '',
    surface_type: data.surface_type || '',
    is_indoor: data.is_indoor ?? null,
    notes: data.notes || '',
    sport_ids: data.sports ? data.sports.map(s => s.id) : []
  }
  if (form.value.latitude && form.value.longitude) {
    await initMap(form.value.latitude, form.value.longitude)
  }
}

const submitField = async () => {
  if (form.value.sport_ids.length === 0) {
    errorMessage.value = 'Seleziona almeno uno sport.'
    return
  }
  if (!form.value.latitude || !form.value.longitude) {
    errorMessage.value = 'Imposta la posizione del campo sulla mappa prima di inviare.'
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
      ? 'Grazie! La tua correzione è stata inviata ed è in attesa di revisione.'
      : 'Grazie! Il nuovo campo è stato segnalato ed è in attesa di approvazione.'

    setTimeout(() => router.push('/'), 3000)
  } catch (err) {
    const detail = err.response?.data?.detail
    if (Array.isArray(detail)) {
      errorMessage.value = detail.map(d => d.msg).join(', ')
    } else {
      errorMessage.value = detail || "Errore durante l'invio. Riprova più tardi."
    }
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
          : 'Aiutaci a migliorare la mappa segnalando un campo sportivo che conosci.' }}
      </p>

      <div v-if="successMessage" class="alert success">{{ successMessage }}</div>
      <div v-if="errorMessage" class="alert error">{{ errorMessage }}</div>

      <form @submit.prevent="submitField" v-if="!successMessage" class="modern-form">
        <div class="form-grid">

          <!-- Basic Info -->
          <div class="form-section glass-card">
            <h3>📝 Informazioni di Base</h3>
            <div class="form-group">
              <label>Nome del Campo *</label>
              <input type="text" v-model="form.name" required placeholder="Es. Centro Sportivo Roma" class="glass-input">
            </div>
            <div class="form-group">
              <label>Descrizione</label>
              <textarea v-model="form.description" rows="3" placeholder="Dettagli sul campo, strutture disponibili..." class="glass-input"></textarea>
            </div>
            <div class="form-group">
              <label>Note aggiuntive</label>
              <textarea v-model="form.notes" rows="2" placeholder="Orari, parcheggio, spogliatoi, accesso disabili..." class="glass-input"></textarea>
            </div>
          </div>

          <!-- Location with Map Picker -->
          <div class="form-section glass-card">
            <h3>📍 Ubicazione</h3>
            <div class="form-row">
              <div class="form-group two-thirds">
                <label>Indirizzo *</label>
                <input type="text" v-model="form.address" required placeholder="Es. Via Garibaldi 10" class="glass-input">
              </div>
              <div class="form-group one-third">
                <label>Città *</label>
                <input type="text" v-model="form.city" required placeholder="Es. Roma" class="glass-input">
              </div>
            </div>

            <div class="location-actions">
              <button type="button" class="btn-locate" @click="geocodeAndShow" :disabled="isGeocoding">
                {{ isGeocoding ? '⏳ Ricerca...' : '🔍 Trova sulla mappa' }}
              </button>
              <button type="button" class="btn-gps" @click="useGPSLocation">
                📍 Usa GPS
              </button>
            </div>

            <div class="map-wrapper">
              <div ref="mapContainer" class="mini-map"></div>
              <div v-if="!form.latitude" class="map-placeholder">
                <span>🗺️</span>
                <p>Cerca l'indirizzo o usa il GPS<br>per posizionare il campo</p>
              </div>
            </div>

            <div v-if="form.latitude" class="coords-display">
              <span class="coord-badge">📌 {{ form.latitude }}, {{ form.longitude }}</span>
              <span class="coord-hint">Trascina il marker o clicca per spostarlo</span>
            </div>
          </div>

          <!-- Sports -->
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

          <!-- Field Characteristics -->
          <div class="form-section glass-card">
            <h3>🏗️ Caratteristiche</h3>
            <div class="form-group">
              <label>Tipo di superficie</label>
              <select v-model="form.surface_type" class="glass-input glass-select">
                <option value="">— Non specificato —</option>
                <option v-for="s in surfaceTypes" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Struttura</label>
              <div class="radio-group">
                <label class="radio-label" :class="{ active: form.is_indoor === false }">
                  <input type="radio" :value="false" v-model="form.is_indoor">
                  ☀️ Scoperta
                </label>
                <label class="radio-label" :class="{ active: form.is_indoor === true }">
                  <input type="radio" :value="true" v-model="form.is_indoor">
                  🏠 Coperta
                </label>
                <label class="radio-label" :class="{ active: form.is_indoor === null }">
                  <input type="radio" :value="null" v-model="form.is_indoor">
                  ❓ Non so
                </label>
              </div>
            </div>
          </div>

          <!-- Contact & Tariffs -->
          <div class="form-section glass-card">
            <h3>📞 Contatti e Tariffe</h3>
            <div class="form-group">
              <label>Telefono</label>
              <input type="tel" v-model="form.phone" class="glass-input" placeholder="+39 06 1234567">
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="form.email" class="glass-input" placeholder="info@campo.it">
            </div>
            <div class="form-group">
              <label>Sito Web</label>
              <input type="url" v-model="form.website" class="glass-input" placeholder="https://...">
            </div>
            <div class="form-group">
              <label>Link Prenotazione</label>
              <input type="url" v-model="form.booking_url" class="glass-input" placeholder="Es. Playtomic, WeAre8...">
            </div>
            <div class="form-group">
              <label>Info Tariffe</label>
              <input type="text" v-model="form.price_info" class="glass-input" placeholder="Es. 10€/ora, noleggio racchette incluso">
            </div>
          </div>
        </div>

        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? 'Invio in corso...' : (isUpdateMode ? 'Invia Correzione' : 'Crea Segnalazione') }}
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
  max-width: 1100px;
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
  font-size: 1.05rem;
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
}

h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 1.25rem;
  color: var(--primary-color);
  font-weight: 800;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.two-thirds { flex: 2; }
.one-third { flex: 1; }

label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.glass-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%2394a3b8' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 36px;
  cursor: pointer;
}

.glass-select option {
  background: #1e293b;
  color: #f8fafc;
}

/* Location */
.location-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.btn-locate {
  flex: 1;
  padding: 10px 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-locate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-gps {
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #4ade80;
  font-weight: 700;
  font-size: 0.85rem;
}

.btn-gps:hover {
  background: rgba(16, 185, 129, 0.25);
}

/* Mini Map */
.map-wrapper {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--glass-border);
  height: 240px;
  background: rgba(0, 0, 0, 0.3);
  margin-bottom: 0.75rem;
}

.mini-map {
  width: 100%;
  height: 100%;
}

.map-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
  pointer-events: none;
}

.map-placeholder span {
  font-size: 2.5rem;
  opacity: 0.4;
}

.map-placeholder p {
  font-size: 0.85rem;
  text-align: center;
  opacity: 0.6;
  line-height: 1.5;
}

.coords-display {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.coord-badge {
  font-size: 0.78rem;
  font-weight: 700;
  font-family: monospace;
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-color);
  padding: 4px 10px;
  border-radius: 8px;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.coord-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Sports */
.sports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
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
}

.sport-checkbox input { display: none; }
.s-icon { font-size: 1.1rem; }
.s-name { font-size: 0.85rem; font-weight: 600; }

/* Radio Group */
.radio-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.2s;
  color: var(--text-secondary);
}

.radio-label.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--primary-color);
  color: var(--text-primary);
}

.radio-label input { display: none; }

/* Actions */
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
  .submit-container { padding: 1rem; }
  .submit-card { padding: 1.5rem; }
  .form-grid { grid-template-columns: 1fr; }
  .full-width { grid-column: auto; }
  .form-row { flex-direction: column; }
  .location-actions { flex-direction: column; }
}
</style>
