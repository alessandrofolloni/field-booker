<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/services/api'

const stats = ref(null)
const isLoading = ref(true)
const periodDays = ref(30)

const fetchStats = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get(`/fields/analytics/stats?period_days=${periodDays.value}`)
    stats.value = data
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  } finally {
    isLoading.value = false
  }
}

const changePeriod = (days) => {
  periodDays.value = days
  fetchStats()
}

// For CSS bar chart scaling
const maxViews = computed(() => {
  if (!stats.value?.top_fields?.length) return 1
  return Math.max(...stats.value.top_fields.map((f) => f.view_count)) || 1
})

const barWidth = (count) => Math.max(2, Math.round((count / maxViews.value) * 100))

onMounted(fetchStats)
</script>

<template>
  <div class="analytics-wrapper animate-fade-in">
    <div class="analytics-container">

      <!-- Header -->
      <header class="analytics-header">
        <div>
          <span class="view-badge">ANALYTICS</span>
          <h1>Dashboard Analytics</h1>
          <p class="subtitle">Monitora l'utilizzo della piattaforma</p>
        </div>
        <div class="period-filters">
          <button
            v-for="d in [7, 30, 90]"
            :key="d"
            :class="['period-btn', { active: periodDays === d }]"
            @click="changePeriod(d)"
          >
            {{ d }}g
          </button>
        </div>
      </header>

      <!-- Loading -->
      <div v-if="isLoading" class="loading-state glass-panel">
        <div class="spinner"></div>
        <p>Caricamento statistiche…</p>
      </div>

      <template v-else-if="stats">

        <!-- Summary cards -->
        <div class="summary-grid">
          <div class="stat-card glass-panel">
            <div class="stat-icon">👁️</div>
            <div class="stat-body">
              <div class="stat-value">{{ stats.total_field_views.toLocaleString('it-IT') }}</div>
              <div class="stat-label">Visualizzazioni Campo</div>
            </div>
          </div>
          <div class="stat-card glass-panel">
            <div class="stat-icon">📅</div>
            <div class="stat-body">
              <div class="stat-value">{{ stats.total_booking_clicks.toLocaleString('it-IT') }}</div>
              <div class="stat-label">Click Prenotazione</div>
            </div>
          </div>
          <div class="stat-card glass-panel">
            <div class="stat-icon">🤖</div>
            <div class="stat-body">
              <div class="stat-value">{{ stats.total_ai_messages.toLocaleString('it-IT') }}</div>
              <div class="stat-label">Messaggi AI</div>
            </div>
          </div>
          <div class="stat-card glass-panel">
            <div class="stat-icon">🔍</div>
            <div class="stat-body">
              <div class="stat-value">{{ stats.total_searches.toLocaleString('it-IT') }}</div>
              <div class="stat-label">Ricerche</div>
            </div>
          </div>
        </div>

        <!-- Top fields table -->
        <div class="section glass-panel">
          <h2 class="section-title">Campi Più Visitati</h2>

          <div v-if="stats.top_fields.length === 0" class="empty-table">
            Nessun dato disponibile per questo periodo.
          </div>

          <div v-else class="top-fields-table">
            <div class="table-header">
              <span>Campo</span>
              <span>Visualizzazioni</span>
              <span>Prenotazioni</span>
              <span>Conversione</span>
            </div>

            <div
              v-for="(field, idx) in stats.top_fields"
              :key="field.field_id"
              class="table-row"
            >
              <div class="field-col">
                <span class="rank">{{ idx + 1 }}</span>
                <span class="field-name">{{ field.field_name }}</span>
              </div>

              <div class="bar-col">
                <div class="bar-track">
                  <div
                    class="bar-fill views-bar"
                    :style="{ width: barWidth(field.view_count) + '%' }"
                  ></div>
                </div>
                <span class="bar-count">{{ field.view_count }}</span>
              </div>

              <div class="bar-col">
                <div class="bar-track">
                  <div
                    class="bar-fill bookings-bar"
                    :style="{ width: barWidth(field.booking_clicks) + '%' }"
                  ></div>
                </div>
                <span class="bar-count">{{ field.booking_clicks }}</span>
              </div>

              <div class="conversion-col">
                <span
                  class="conversion-badge"
                  :class="field.conversion_rate > 10 ? 'good' : field.conversion_rate > 5 ? 'medium' : 'low'"
                >
                  {{ field.conversion_rate }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Secondary stats row -->
        <div class="secondary-stats glass-panel">
          <div class="secondary-item">
            <span class="secondary-icon">🔧</span>
            <div>
              <div class="secondary-value">{{ stats.total_field_submitted }}</div>
              <div class="secondary-label">Campi Segnalati</div>
            </div>
          </div>
          <div class="secondary-divider"></div>
          <div class="secondary-item">
            <span class="secondary-icon">🎯</span>
            <div>
              <div class="secondary-value">{{ stats.total_filter_applied }}</div>
              <div class="secondary-label">Filtri Applicati</div>
            </div>
          </div>
        </div>

      </template>

    </div>
  </div>
</template>

<style scoped>
.analytics-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: 3rem 2rem;
  background: var(--bg-color, #0f172a);
}

.analytics-container {
  max-width: 1100px;
  margin: 0 auto;
}

/* ─── Header ─── */
.analytics-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 3rem;
  gap: 1rem;
}

.view-badge {
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  color: var(--color-accent, #22c55e);
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-block;
  margin-bottom: 0.75rem;
}

h1 {
  font-size: 2.5rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin-bottom: 0.4rem;
}

.subtitle { color: var(--text-secondary); font-size: 0.95rem; }

.period-filters {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.period-btn {
  padding: 8px 18px;
  border-radius: 20px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-secondary);
  font-weight: 700;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}

.period-btn:hover { color: var(--text-primary); border-color: var(--color-border-hover, rgba(255,255,255,0.18)); }

.period-btn.active {
  background: var(--gradient-accent, linear-gradient(135deg, #22c55e, #16a34a));
  color: #000;
  border-color: transparent;
  box-shadow: 0 3px 12px rgba(34, 197, 94, 0.3);
}

/* ─── Loading ─── */
.loading-state {
  text-align: center;
  padding: 3rem;
  border-radius: 20px;
  color: var(--text-muted);
}

.spinner {
  width: 36px; height: 36px;
  border: 3px solid rgba(255,255,255,0.06);
  border-top-color: var(--color-accent, #22c55e);
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Summary cards ─── */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  padding: 1.5rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s;
}

.stat-card:hover { transform: translateY(-3px); }

.stat-icon { font-size: 1.8rem; }

.stat-value {
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ─── Table section ─── */
.section {
  padding: 2rem;
  border-radius: 20px;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}

.table-header {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2fr 1fr;
  gap: 1rem;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--glass-border);
  margin-bottom: 0.5rem;
}

.table-row {
  display: grid;
  grid-template-columns: 2.5fr 2fr 2fr 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  align-items: center;
}

.field-col {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
}

.rank {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  min-width: 20px;
  flex-shrink: 0;
}

.field-name {
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-col {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.bar-track {
  flex: 1;
  height: 6px;
  background: rgba(255,255,255,0.05);
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.55s cubic-bezier(0.4, 0, 0.2, 1);
}

.views-bar { background: var(--primary-color, #6366f1); }
.bookings-bar { background: var(--color-accent, #22c55e); }

.bar-count {
  font-size: 0.83rem;
  font-weight: 700;
  min-width: 28px;
  text-align: right;
  flex-shrink: 0;
}

.conversion-col { display: flex; justify-content: flex-start; }

.conversion-badge {
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 700;
}

.conversion-badge.good   { background: rgba(34,197,94,0.14);  color: #4ade80; }
.conversion-badge.medium { background: rgba(245,158,11,0.14); color: var(--accent-color, #f59e0b); }
.conversion-badge.low    { background: rgba(239,68,68,0.1);   color: #f87171; }

.empty-table {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* ─── Secondary stats ─── */
.secondary-stats {
  padding: 1.5rem 2rem;
  border-radius: 20px;
  display: flex;
  align-items: center;
  gap: 2rem;
}

.secondary-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.secondary-icon { font-size: 1.5rem; }

.secondary-value {
  font-size: 1.4rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 2px;
}

.secondary-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.secondary-divider {
  width: 1px;
  height: 40px;
  background: var(--glass-border);
}

/* ─── Responsive ─── */
@media (max-width: 900px) {
  .summary-grid { grid-template-columns: 1fr 1fr; }
  .table-header, .table-row { grid-template-columns: 2fr 1.5fr 1fr; }
  .bar-col:nth-child(3), .table-header span:nth-child(3) { display: none; }
}

@media (max-width: 600px) {
  .analytics-header { flex-direction: column; align-items: flex-start; }
  .summary-grid { grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  h1 { font-size: 1.8rem; }
}
</style>
