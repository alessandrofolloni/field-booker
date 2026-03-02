<script setup>
import { ref, watch } from 'vue'
import { useFieldsStore } from '@/stores/fields'
import { useAnalytics } from '@/composables/useAnalytics'
import AIChatAssistant from './AIChatAssistant.vue'

const fieldsStore = useFieldsStore()
const { trackEvent } = useAnalytics()
const suggestionTimeout = ref(null)
const skipNextSuggestion = ref(false)
const activeTab = ref('list') // 'list' or 'ai'

const applyFilters = () => {
  trackEvent('filter_applied', null, {
    radius_km: fieldsStore.radiusKm,
    sport_ids: fieldsStore.selectedSportIds,
  })
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

const handleFieldSelect = (field) => {
  trackEvent('field_viewed', field.id, { field_name: field.name })
  fieldsStore.selectField(field)
}

const handleSuggestionSelect = (sug) => {
  skipNextSuggestion.value = true
  trackEvent('search_performed', null, { query: sug.display_name })
  fieldsStore.selectSuggestion(sug)
}

const handleBookingClick = () => {
  const field = fieldsStore.selectedField
  if (field) {
    trackEvent('booking_clicked', field.id, {
      field_name: field.name,
      booking_url: field.booking_url,
    })
  }
}

// Watch for address changes to fetch suggestions (debounced)
watch(() => fieldsStore.searchAddress, (newVal) => {
  if (suggestionTimeout.value) clearTimeout(suggestionTimeout.value)
  if (skipNextSuggestion.value) {
    skipNextSuggestion.value = false
    return
  }
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

    <!-- Tabs (only when no field selected) -->
    <div v-if="!fieldsStore.selectedField" class="sidebar-tabs animate-fade-in">
      <button :class="{ active: activeTab === 'list' }" @click="activeTab = 'list'">
        📋 Esplora
      </button>
      <button :class="{ active: activeTab === 'ai' }" @click="activeTab = 'ai'">
        🤖 AI Assistant
      </button>
    </div>

    <!-- DETAILS VIEW -->
    <transition name="slide">
      <div v-if="fieldsStore.selectedField" key="details" class="details-view">
        <button class="back-btn" @click="fieldsStore.selectField(null)">
          <span class="back-icon-circle">←</span>
          <span class="back-label">Torna alla lista</span>
        </button>

        <div class="field-details animate-fade-in">
          <!-- Title -->
          <h2
            class="field-title"
            :style="{ color: fieldsStore.selectedField.sports?.[0]?.color || 'var(--color-text-primary, #f8fafc)' }"
          >
            {{ fieldsStore.selectedField.name }}
          </h2>

          <!-- Rating -->
          <div class="rating-row" v-if="fieldsStore.selectedField.avg_rating">
            <span class="rating-stars">⭐ {{ fieldsStore.selectedField.avg_rating.toFixed(1) }}</span>
            <span class="rating-count">{{ fieldsStore.selectedField.review_count }} recensioni</span>
          </div>

          <!-- Description -->
          <p class="field-desc" v-if="fieldsStore.selectedField.description">
            {{ fieldsStore.selectedField.description }}
          </p>

          <!-- Info grid -->
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
                <label>Sito Web</label>
                <a :href="fieldsStore.selectedField.website" target="_blank" class="c-link">
                  Visita sito
                </a>
              </div>
            </div>
          </div>

          <!-- Sport tags -->
          <div class="sport-tags-container">
            <span
              v-for="sport in fieldsStore.selectedField.sports"
              :key="sport.id"
              class="tag-pill"
              :style="{ background: sport.color + '22', color: sport.color, borderColor: sport.color + '55' }"
            >
              {{ sport.icon }} {{ sport.name }}
            </span>
          </div>

          <div class="section-divider"></div>

          <!-- Actions -->
          <div class="action-section animate-fade-in">
            <a
              v-if="fieldsStore.selectedField.booking_url"
              :href="fieldsStore.selectedField.booking_url"
              target="_blank"
              class="btn-accent booking-btn"
              @click="handleBookingClick"
            >
              📅 Prenota Ora
            </a>

            <button
              class="btn-secondary suggest-btn"
              @click="$router.push({ name: 'submit-field', query: { field_id: fieldsStore.selectedField.id } })"
            >
              🛠️ Suggerisci correzione
            </button>
          </div>

          <!-- Price -->
          <div class="price-section" v-if="fieldsStore.selectedField.price_info">
            <h3>Tariffe</h3>
            <div class="price-card">
              <p>{{ fieldsStore.selectedField.price_info }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- AI VIEW -->
      <div v-else-if="activeTab === 'ai'" key="ai" class="ai-view-container">
        <AIChatAssistant />
      </div>

      <!-- LIST VIEW -->
      <div v-else key="list" class="list-view">
        <div class="search-section">
          <div class="search-header">
            <h2>Esplora Campi</h2>
            <div class="results-count" v-if="!fieldsStore.isLoading">
              {{ fieldsStore.fields.length }} risultati
            </div>
          </div>

          <!-- Address search -->
          <div class="address-search-container">
            <div class="search-box">
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
                {{ fieldsStore.isGeocoding ? '…' : 'Vai' }}
              </button>

              <!-- Suggestions dropdown -->
              <div
                v-if="fieldsStore.addressSuggestions.length > 0"
                class="suggestions-dropdown glass-panel animate-fade-in"
              >
                <div
                  v-for="(sug, idx) in fieldsStore.addressSuggestions"
                  :key="idx"
                  class="suggestion-item"
                  @mousedown="handleSuggestionSelect(sug)"
                >
                  <span class="sug-icon">📍</span>
                  <span class="sug-text">{{ sug.display_name }}</span>
                </div>
              </div>
            </div>

            <button
              class="btn-my-pos"
              @click="fieldsStore.getUserLocation"
              title="Usa la mia posizione"
            >
              📍
            </button>
          </div>

          <!-- Filters -->
          <div class="filters-panel">
            <div class="filter-group">
              <div class="label-row">
                <span>Raggio di ricerca</span>
                <span class="value">{{ fieldsStore.radiusKm }} km</span>
              </div>
              <input
                type="range"
                v-model.number="fieldsStore.radiusKm"
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
                  :style="fieldsStore.selectedSportIds.includes(sport.id)
                    ? { background: sport.color + '22', color: sport.color, borderColor: sport.color }
                    : {}"
                >
                  <span>{{ sport.icon }}</span>
                  <span class="chip-name">{{ sport.name }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Results -->
        <div class="results-container">
          <!-- Skeleton loading -->
          <template v-if="fieldsStore.isLoading">
            <div v-for="i in 5" :key="i" class="result-card-skeleton">
              <div class="skeleton" style="height:14px; width:55%; margin-bottom:10px;"></div>
              <div class="skeleton" style="height:12px; width:80%; margin-bottom:18px;"></div>
              <div class="skeleton" style="height:10px; width:35%;"></div>
            </div>
          </template>

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
            class="result-card hover-lift"
            :style="{ borderLeftColor: field.sports?.[0]?.color || 'transparent' }"
            @click="handleFieldSelect(field)"
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
/* ─── Layout ─── */
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

.ai-view-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
}

/* ─── Tabs ─── */
.sidebar-tabs {
  display: flex;
  margin: 0 1.5rem 1.5rem;
  background: rgba(255, 255, 255, 0.04);
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
  background: rgba(255, 255, 255, 0.04);
}

.sidebar-tabs button.active {
  background: var(--primary-color);
  color: white;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
}

/* ─── Back button ─── */
.back-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1.25rem 1.5rem;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.9rem;
  border-bottom: 1px solid var(--glass-border);
  transition: all 0.2s;
}

.back-btn:hover {
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.04);
}

.back-icon-circle {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--glass-bg);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.back-btn:hover .back-icon-circle {
  background: rgba(255,255,255,0.08);
  border-color: var(--color-border-hover, rgba(255,255,255,0.18));
}

/* ─── Field Details ─── */
.field-details { padding: 2rem; }

.field-title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 0.75rem;
  line-height: 1.15;
}

.rating-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 1.25rem;
}

.rating-stars {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: var(--accent-color);
  padding: 3px 12px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 0.85rem;
}

.rating-count {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.field-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.65;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.info-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
  margin-top: 2px;
}

.info-text label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--text-muted);
  font-weight: 700;
  margin-bottom: 2px;
  display: block;
}

.info-text p {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.c-link {
  color: var(--primary-color);
  font-weight: 500;
  font-size: 0.9rem;
}

.sport-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 2rem;
}

.tag-pill {
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid transparent;
}

.section-divider {
  height: 1px;
  background: var(--glass-border);
  margin: 1.5rem 0;
}

h3 {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 0.75rem;
}

/* ─── Actions ─── */
.action-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.booking-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  border-radius: var(--border-radius, 12px);
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  background: var(--gradient-accent, linear-gradient(135deg, #22c55e, #16a34a));
  color: #000;
  box-shadow: var(--shadow-accent, 0 4px 20px rgba(34, 197, 94, 0.25));
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.booking-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 28px rgba(34, 197, 94, 0.4);
}

.suggest-btn {
  width: 100%;
}

.price-card {
  background: rgba(255,255,255,0.03);
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.6;
}

/* ─── Search section ─── */
.search-section {
  padding: 2rem;
  background: linear-gradient(to bottom, var(--glass-bg), transparent);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.results-count {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  background: var(--glass-bg);
  padding: 4px 10px;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
}

.address-search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 2rem;
}

.search-box {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  padding: 4px 8px 4px 14px;
  border-radius: 12px;
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-icon { font-size: 0.9rem; opacity: 0.6; flex-shrink: 0; }

.search-box input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 0.95rem;
  padding: 8px 0;
  outline: none;
  min-width: 0;
}

.btn-go {
  background: var(--primary-color);
  color: white;
  padding: 6px 14px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.82rem;
  flex-shrink: 0;
  transition: all 0.2s;
}

.btn-go:hover:not(:disabled) {
  background: var(--secondary-color, #4f46e5);
}

.btn-my-pos {
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  width: 46px;
  height: 46px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.2s;
  flex-shrink: 0;
}

.btn-my-pos:hover {
  background: rgba(255,255,255,0.1);
  transform: translateY(-2px);
}

/* ─── Suggestions dropdown ─── */
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
  box-shadow: var(--shadow-2xl, 0 25px 50px rgba(0,0,0,0.5));
  border-radius: 12px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}

.suggestion-item:hover {
  background: rgba(255,255,255,0.07);
}

.sug-icon { font-size: 0.9rem; opacity: 0.6; }

.sug-text {
  font-size: 0.83rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-item:hover .sug-text { color: var(--text-primary); }

/* ─── Filters ─── */
.filters-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.label-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.88rem;
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
  font-size: 0.83rem;
  font-weight: 500;
  transition: all 0.2s;
}

.chip:hover { border-color: var(--color-border-hover, rgba(255,255,255,0.18)); }

.chip.active {
  font-weight: 700;
}

/* ─── Results ─── */
.results-container {
  flex: 1;
  padding: 0 1rem 2rem;
}

/* Skeleton cards */
.result-card-skeleton {
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1rem;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  background: rgba(255,255,255,0.02);
}

/* Field result cards */
.result-card {
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1rem;
  border: 1px solid var(--glass-border);
  border-left: 3px solid transparent;
  cursor: pointer;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(255, 255, 255, 0.02);
}

.result-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.05);
  box-shadow: var(--shadow-card, 0 8px 32px rgba(0,0,0,0.4));
  border-color: rgba(99, 102, 241, 0.35);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 4px;
}

.card-title {
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.3;
}

.card-dist {
  font-size: 0.73rem;
  font-weight: 700;
  color: var(--primary-color);
  flex-shrink: 0;
  margin-left: 8px;
}

.card-addr {
  font-size: 0.83rem;
  color: var(--text-muted);
  margin-bottom: 1rem;
  line-height: 1.4;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sport-dot { font-size: 1.05rem; margin-right: 4px; }

.card-rating {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--accent-color);
}

/* ─── States ─── */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--text-muted);
}

.empty-icon { font-size: 3rem; margin-bottom: 1rem; opacity: 0.4; }
.mt-2 { margin-top: 1rem; }

/* ─── Transitions ─── */
.slide-enter-active, .slide-leave-active { transition: all 0.28s ease; }
.slide-enter-from, .slide-leave-to { opacity: 0; transform: translateX(-16px); }
</style>
