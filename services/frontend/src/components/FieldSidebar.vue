<script setup>
import { ref, watch } from 'vue'
import { useFieldsStore } from '@/stores/fields'
import AIChatAssistant from './AIChatAssistant.vue'

const fieldsStore = useFieldsStore()
const suggestionTimeout = ref(null)
const activeTab = ref('list') // 'list' or 'ai'

const applyFilters = () => {
  fieldsStore.fetchNearbyFields()
}

const toggleSport = (sportId) => {
  const index = fieldsStore.selectedSportIds.indexOf(sportId)
  if (index > -1) {
    fieldsStore.selectedSportIds.splice(index, 1)
  } else {
    fieldsStore.selectedSportIds.push(sportId)
  }
  applyFilters()
}

// Watch for address changes to fetch suggestions (debounced)
watch(() => fieldsStore.searchAddress, (newVal) => {
  if (suggestionTimeout.value) clearTimeout(suggestionTimeout.value)
  
  if (newVal && newVal.length >= 3) {
    suggestionTimeout.value = setTimeout(() => {
      fieldsStore.fetchAddressSuggestions(newVal)
    }, 400)
  } else {
    fieldsStore.addressSuggestions = []
  }
})

const handleBlur = () => {
  setTimeout(() => {
    fieldsStore.addressSuggestions = []
  }, 200)
}
</script>

<template>
  <div class="sidebar-container glass-panel">
    
    <!-- Navigation Tabs (Only if no field selected) -->
    <div v-if="!fieldsStore.selectedField" class="sidebar-tabs animate-fade-in">
      <button 
        :class="{ active: activeTab === 'list' }" 
        @click="activeTab = 'list'"
      >
        📋 Esplora
      </button>
      <button 
        :class="{ active: activeTab === 'ai' }" 
        @click="activeTab = 'ai'"
      >
        🤖 AI Assistant
      </button>
    </div>

    <!-- IF A FIELD IS SELECTED (DETAILS VIEW) -->
    <transition name="slide">
      <div v-if="fieldsStore.selectedField" class="details-view">
        <button class="back-btn" @click="fieldsStore.selectField(null)">
          <span class="back-icon">←</span>
          <span>Torna alla lista</span>
        </button>
        
        <div class="field-details animate-fade-in">
          <h2 class="field-title">{{ fieldsStore.selectedField.name }}</h2>
          
          <div class="rating-row" v-if="fieldsStore.selectedField.avg_rating">
            <span class="rating-stars">⭐ {{ fieldsStore.selectedField.avg_rating.toFixed(1) }}</span>
            <span class="rating-count">({{ fieldsStore.selectedField.review_count }} recensioni)</span>
          </div>
          
          <p class="field-desc">{{ fieldsStore.selectedField.description }}</p>

          <div class="info-grid">
            <div class="info-item" v-if="fieldsStore.selectedField.address">
              <span class="info-icon">📍</span>
              <div class="info-text">
                <label>Indirizzo</label>
                <p>{{ fieldsStore.selectedField.address }}, {{ fieldsStore.selectedField.city }}</p>
              </div>
            </div>
            
            <div class="info-item" v-if="fieldsStore.selectedField.phone">
              <span class="info-icon">📞</span>
              <div class="info-text">
                <label>Telefono</label>
                <p>{{ fieldsStore.selectedField.phone }}</p>
              </div>
            </div>

            <div class="info-item" v-if="fieldsStore.selectedField.website">
              <span class="info-icon">🌐</span>
              <div class="info-text">
                <label>Sito</label>
                <a :href="fieldsStore.selectedField.website" target="_blank" class="c-link">Sito Web</a>
              </div>
            </div>
          </div>
          
          <div class="sport-tags-container">
            <span 
              v-for="sport in fieldsStore.selectedField.sports" 
              :key="sport.id" 
              class="tag-pill"
              :style="{ background: sport.color + '22', color: sport.color, borderColor: sport.color + '44' }"
            >
              {{ sport.icon }} {{ sport.name }}
            </span>
          </div>

          <div class="section-divider"></div>

          <div class="action-section animate-fade-in" style="animation-delay: 0.1s">
            <h3 v-if="fieldsStore.selectedField.booking_url">Prenotazioni</h3>
            <a 
              v-if="fieldsStore.selectedField.booking_url"
              :href="fieldsStore.selectedField.booking_url" 
              target="_blank" 
              class="btn-primary booking-btn"
            >
              Prenota Ora
            </a>
            
            <div class="fix-section mt-2">
              <button 
                class="btn-secondary w-full" 
                @click="$router.push({ name: 'submit-field', query: { field_id: fieldsStore.selectedField.id } })"
              >
                🛠️ Suggerisci correzione
              </button>
            </div>
          </div>
          
          <div class="price-section" v-if="fieldsStore.selectedField.price_info">
            <h3>Tariffe</h3>
            <div class="price-card">
              <p>{{ fieldsStore.selectedField.price_info }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ELSE IF: AI ASSISTANT -->
      <div v-else-if="activeTab === 'ai'" class="ai-view-container">
        <AIChatAssistant />
      </div>

      <!-- ELSE: FILTERS & LIST VIEW -->
      <div v-else class="list-view">
        <div class="search-section">
          <div class="search-header">
            <h2>Esplora Campi</h2>
            <div class="results-count" v-if="!fieldsStore.isLoading">
              {{ fieldsStore.fields.length }} risultati
            </div>
          </div>

          <!-- NEW: Address Search Box -->
          <div class="address-search-container">
            <div class="search-box glass-input">
              <span class="search-icon">🔍</span>
              <input 
                type="text" 
                v-model="fieldsStore.searchAddress" 
                placeholder="Città o indirizzo..."
                @keyup.enter="fieldsStore.searchLocationByAddress"
                @blur="handleBlur"
                :disabled="fieldsStore.isGeocoding"
              />
              <button 
                class="btn-go" 
                @click="fieldsStore.searchLocationByAddress"
                :disabled="fieldsStore.isGeocoding"
              >
                {{ fieldsStore.isGeocoding ? '...' : 'Vai' }}
              </button>

              <!-- Suggestions Dropdown -->
              <div v-if="fieldsStore.addressSuggestions.length > 0" class="suggestions-dropdown glass-panel animate-fade-in">
                <div 
                  v-for="(sug, idx) in fieldsStore.addressSuggestions" 
                  :key="idx" 
                  class="suggestion-item"
                  @mousedown="fieldsStore.selectSuggestion(sug)"
                >
                  <span class="sug-icon">📍</span>
                  <span class="sug-text">{{ sug.display_name }}</span>
                </div>
              </div>
            </div>
            
            <button 
              class="btn-my-pos" 
              @click="fieldsStore.getUserLocation" 
              title="Usa la mia posizione attuale"
            >
              📍
            </button>
          </div>
          
          <div class="filters-panel">
            <div class="filter-group">
              <div class="label-row">
                <span>Raggio di ricerca</span>
                <span class="value">{{ fieldsStore.radiusKm }} km</span>
              </div>
              <input 
                type="range" 
                v-model="fieldsStore.radiusKm" 
                min="1" max="100" step="1" 
                @change="applyFilters" 
                class="modern-slider"
              />
            </div>

            <div class="filter-group">
              <label>Sport</label>
              <div class="sport-chips">
                <button 
                  v-for="sport in fieldsStore.sports" 
                  :key="sport.id"
                  class="chip"
                  :class="{ active: fieldsStore.selectedSportIds.includes(sport.id) }"
                  @click="toggleSport(sport.id)"
                  :style="fieldsStore.selectedSportIds.includes(sport.id) ? { background: sport.color + '22', color: sport.color, borderColor: sport.color } : {}"
                >
                  <span class="chip-icon">{{ sport.icon }}</span>
                  <span class="chip-name">{{ sport.name }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="results-container">
          <div v-if="fieldsStore.isLoading" class="loading-state">
            <div class="spinner"></div>
            <p>Ricerca in corso...</p>
          </div>
          
          <div v-else-if="fieldsStore.fields.length === 0" class="empty-state">
            <div class="empty-icon">🏟️</div>
            <p>Nessun campo trovato entro {{ fieldsStore.radiusKm }}km.</p>
            <button class="btn-secondary mt-2" @click="fieldsStore.radiusKm = 50; applyFilters()">
              Aumenta raggio
            </button>
          </div>

          <div 
            v-else
            v-for="field in fieldsStore.fields" 
            :key="field.id" 
            class="result-card"
            @click="fieldsStore.selectField(field)"
          >
            <div class="card-header">
              <h4 class="card-title">{{ field.name }}</h4>
              <div class="card-dist">{{ field.distance_km }} km</div>
            </div>
            <p class="card-addr">{{ field.address }}</p>
            <div class="card-footer">
              <div class="card-sports">
                <span v-for="s in field.sports" :key="s.id" class="sport-dot" :title="s.name">{{ s.icon }}</span>
              </div>
              <div class="card-rating" v-if="field.avg_rating">
                ⭐ {{ field.avg_rating.toFixed(1) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
/* Tabs Navigation */
.sidebar-tabs {
  display: flex;
  margin: 0 1.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 14px;
  border: 1px solid var(--glass-border);
}

.sidebar-tabs button {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-tabs button:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.03);
}

.sidebar-tabs button.active {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.ai-view-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
}

.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  border-right: 1px solid var(--glass-border);
  position: relative;
  z-index: 100;
}

.details-view, .list-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
}

/* Actions & Buttons */
.back-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1.5rem;
  color: var(--text-secondary);
  font-weight: 600;
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.2s;
}

.back-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.05);
}

.back-icon {
  font-size: 1.25rem;
}

/* Field Details */
.field-details {
  padding: 2rem;
}

.field-title {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 1.5rem;
}

.rating-stars {
  background: rgba(245, 158, 11, 0.2);
  color: var(--accent-color);
  padding: 2px 10px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
}

.rating-count {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.field-meta {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.meta-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.meta-icon { font-size: 1.1rem; }

.sport-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 2rem;
}

.tag-pill {
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.section-divider {
  height: 1px;
  background: var(--glass-border);
  margin: 2rem 0;
}

h3 {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.description-section p {
  color: var(--text-secondary);
  font-size: 1rem;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.c-text, .c-link {
  color: var(--text-primary);
  font-weight: 500;
}

.c-link { color: var(--primary-color); }

.booking-btn {
  width: 100%;
}

.price-card {
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
}

/* List View */
.search-section {
  padding: 2rem;
  background: linear-gradient(to bottom, rgba(30, 41, 59, 0.4), transparent);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-count {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--glass-bg);
  padding: 4px 10px;
  border-radius: 20px;
}

.filters-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.label-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.label-row .value {
  color: var(--primary-color);
  font-weight: 700;
}

.modern-slider {
  width: 100%;
  accent-color: var(--primary-color);
}

.sport-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 0.75rem;
}

.chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
}

.chip.active {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--primary-color);
  color: var(--text-primary);
}

/* Address Search Styling */
.address-search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 2rem;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  padding: 4px 8px 4px 16px;
  border-radius: 12px;
}

.search-box input {
  background: transparent;
  border: none;
  color: var(--text-primary);
  width: 100%;
  font-size: 0.95rem;
  padding: 8px 0;
}

.search-box input:focus {
  outline: none;
}

.btn-go {
  background: var(--primary-color);
  color: white;
  padding: 6px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.85rem;
}

.btn-my-pos {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.2s;
}

.btn-my-pos:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

/* Suggestions Dropdown */
.search-box {
  position: relative; /* Context for dropdown */
}

.suggestions-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  z-index: 2000;
  max-height: 250px;
  overflow-y: auto;
  padding: 8px;
  background: var(--surface-color);
  backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-2xl);
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.sug-icon {
  font-size: 1rem;
  opacity: 0.7;
}

.sug-text {
  font-size: 0.85rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-transform: capitalize;
  text-overflow: ellipsis;
}

.suggestion-item:hover .sug-text {
  color: var(--text-primary);
}

/* Result Cards */
.results-container {
  flex: 1;
  padding: 0 1rem 2rem;
}

.result-card {
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1rem;
  border: 1px solid var(--glass-border);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.02);
}

.result-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: var(--shadow-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
}

.card-dist {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--primary-color);
}

.card-addr {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sport-dot { font-size: 1.1rem; margin-right: 4px; }

.card-rating {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--accent-color);
}

/* Transitions */
.slide-enter-active, .slide-leave-active { transition: all 0.3s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateX(-20px); }

/* States */
.loading-state, .empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(99, 102, 241, 0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: rotate 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes rotate { to { transform: rotate(360deg); } }

.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.5; }

.mt-2 { margin-top: 1rem; }
</style>
