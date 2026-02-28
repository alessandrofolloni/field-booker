<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const { toast } = useToast()

const submissions = ref([])
const isLoading = ref(true)

// Two-step confirm state: stores the id + action being confirmed
const confirmingId = ref(null)
const confirmingStatus = ref(null)

const fetchPendingSubmissions = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get('/submissions/pending')
    submissions.value = data.items
  } catch (error) {
    console.error('Failed to fetch pending submissions:', error)
    toast.error('Impossibile caricare le segnalazioni.')
  } finally {
    isLoading.value = false
  }
}

// Step 1: arm the confirmation inline UI
const requestConfirm = (id, status) => {
  confirmingId.value = id
  confirmingStatus.value = status
}

// Step 2: user confirmed → execute
const confirmAction = async () => {
  const id = confirmingId.value
  const status = confirmingStatus.value
  confirmingId.value = null
  confirmingStatus.value = null

  try {
    await api.post(`/submissions/${id}/review`, {
      status,
      admin_notes: `Revisionato il ${new Date().toLocaleDateString('it-IT')} alle ${new Date().toLocaleTimeString('it-IT')}`
    })
    await fetchPendingSubmissions()
  } catch (error) {
    console.error(`Failed to ${status} submission:`, error)
    toast.error("Errore durante l'operazione. Verifica i permessi admin.")
  }
}

// Cancel two-step confirm
const cancelConfirm = () => {
  confirmingId.value = null
  confirmingStatus.value = null
}

onMounted(() => {
  fetchPendingSubmissions()
})
</script>

<template>
  <div class="admin-view-wrapper animate-fade-in">
    <div class="admin-container">

      <!-- Page Header -->
      <header class="admin-page-header">
        <div class="header-content">
          <span class="view-badge">ADMIN AREA</span>
          <h1>Dashboard Segnalazioni</h1>
          <p class="description">Gestisci i nuovi campi inseriti dalla community</p>
        </div>
        <button class="btn-refresh" @click="fetchPendingSubmissions" :disabled="isLoading" title="Aggiorna">
          <span :class="{ spinning: isLoading }">🔄</span>
        </button>
      </header>

      <main class="admin-main">

        <!-- Loading State — skeletons -->
        <div v-if="isLoading" class="skeleton-list">
          <div v-for="i in 3" :key="i" class="sub-card glass-panel skeleton-card">
            <div class="card-status-indicator" style="background: var(--color-surface-3)"></div>
            <div class="sk-line sk-title"></div>
            <div class="sk-line sk-sub"></div>
            <div class="sk-grid">
              <div class="sk-line sk-block"></div>
              <div class="sk-line sk-block"></div>
            </div>
            <div class="sk-actions">
              <div class="sk-line sk-btn"></div>
              <div class="sk-line sk-btn-wide"></div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="submissions.length === 0" class="empty-container glass-panel">
          <div class="empty-art">✅</div>
          <h2>Tutto in ordine!</h2>
          <p>Non ci sono nuove segnalazioni da revisionare al momento.</p>
        </div>

        <!-- Submission Cards -->
        <div v-else class="submission-grid">
          <div
            v-for="sub in submissions"
            :key="sub.id"
            class="sub-card glass-panel"
            :class="{ 'is-confirming': confirmingId === sub.id }"
          >
            <!-- Status stripe — green for updates, indigo for new -->
            <div
              class="card-status-indicator"
              :style="{
                background: sub.submission_type === 'update'
                  ? 'var(--color-accent, #22c55e)'
                  : 'var(--primary-color, #6366f1)'
              }"
            ></div>

            <!-- Card Head -->
            <div class="card-head">
              <div class="field-main-info">
                <div class="type-badge" :class="sub.submission_type">
                  {{ sub.submission_type === 'update' ? '🛠️ CORREZIONE' : '🏟️ NUOVO CAMPO' }}
                </div>
                <h3>{{ sub.field_data.name }}</h3>
                <div class="sub-meta">
                  <span>👤 {{ sub.user_name }}</span>
                  <span class="dot">•</span>
                  <span>📅 {{ new Date(sub.created_at).toLocaleDateString('it-IT') }}</span>
                  <span v-if="sub.submission_type === 'update'" class="field-ref">
                    Ref: {{ sub.field_id.substring(0, 8) }}…
                  </span>
                </div>
              </div>
            </div>

            <!-- Card Body -->
            <div class="card-body">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Posizione</label>
                  <p>{{ sub.field_data.address }}, {{ sub.field_data.city }}</p>
                </div>
                <div class="detail-item">
                  <label>Coordinate</label>
                  <p class="mono">
                    {{ sub.field_data.latitude.toFixed(5) }},
                    {{ sub.field_data.longitude.toFixed(5) }}
                  </p>
                </div>
                <div class="detail-item full">
                  <label>Sport</label>
                  <div class="sports-preview">
                    <span v-for="sportId in sub.field_data.sport_ids" :key="sportId" class="sport-badge-mini">
                      {{ sportId.substring(0, 8) }}…
                    </span>
                  </div>
                </div>
                <div class="detail-item full" v-if="sub.field_data.description">
                  <label>Messaggio</label>
                  <p class="desc-text">{{ sub.field_data.description }}</p>
                </div>
              </div>
            </div>

            <!-- Card Actions — two-step confirm -->
            <div class="card-actions">

              <!-- Normal state -->
              <template v-if="confirmingId !== sub.id">
                <button class="btn-reject-sub" @click="requestConfirm(sub.id, 'rejected')">
                  Scarta
                </button>
                <button class="btn-approve-sub btn-accent" @click="requestConfirm(sub.id, 'approved')">
                  ✓ Approva &amp; Pubblica
                </button>
              </template>

              <!-- Confirmation state -->
              <template v-else>
                <div class="confirm-row">
                  <span class="confirm-label">
                    {{ confirmingStatus === 'approved' ? '✅ Confermi l\'approvazione?' : '🗑️ Confermi lo scarto?' }}
                  </span>
                  <button class="btn-cancel-confirm" @click="cancelConfirm">Annulla</button>
                  <button
                    class="btn-do-confirm"
                    :class="confirmingStatus === 'approved' ? 'btn-accent' : 'btn-confirm-reject'"
                    @click="confirmAction"
                  >
                    Sì, conferma
                  </button>
                </div>
              </template>

            </div>
          </div>
        </div>

      </main>
    </div>
  </div>
</template>

<style scoped>
/* ─── Layout ─── */
.admin-view-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: 3rem 2rem;
  background: var(--background-color);
}

.admin-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* ─── Header ─── */
.admin-page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 3rem;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.view-badge {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  color: var(--color-accent, #22c55e);
  background: var(--color-accent-muted, rgba(34, 197, 94, 0.12));
  border: 1px solid rgba(34, 197, 94, 0.2);
  padding: 4px 12px;
  border-radius: 20px;
  display: inline-block;
  width: fit-content;
}

h1 {
  font-size: 2.4rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  margin: 0;
}

.description {
  color: var(--text-secondary);
  font-size: 1rem;
  margin: 0;
}

.btn-refresh {
  padding: 11px 13px;
  background: var(--glass-bg);
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  border-radius: 12px;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  flex-shrink: 0;
}

.btn-refresh:hover:not(:disabled) {
  background: rgba(255,255,255,0.06);
  border-color: var(--color-border-hover, rgba(255,255,255,0.16));
}

.spinning {
  display: inline-block;
  animation: spin 0.9s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* ─── Skeleton Loading ─── */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.skeleton-card {
  padding: 2rem;
  pointer-events: none;
}

.sk-line {
  background: rgba(255,255,255,0.06);
  border-radius: 6px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.35; }
  50%       { opacity: 0.65; }
}

.sk-title  { height: 22px; width: 55%; margin-bottom: 10px; }
.sk-sub    { height: 14px; width: 38%; margin-bottom: 24px; border-radius: 4px; }
.sk-grid   { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 24px; }
.sk-block  { height: 52px; border-radius: 8px; }
.sk-actions { display: flex; justify-content: flex-end; gap: 1rem; }
.sk-btn      { height: 42px; width: 100px; border-radius: 10px; }
.sk-btn-wide { height: 42px; width: 160px; border-radius: 10px; }

/* ─── Empty State ─── */
.empty-container {
  padding: 5rem 2rem;
  text-align: center;
  margin-top: 2rem;
}

.empty-art {
  font-size: 4rem;
  margin-bottom: 1rem;
  filter: drop-shadow(0 0 20px rgba(34, 197, 94, 0.3));
}

.empty-container h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.empty-container p {
  color: var(--text-secondary);
}

/* ─── Submission Grid ─── */
.submission-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sub-card {
  position: relative;
  overflow: hidden;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  transition: box-shadow 0.25s;
}

.sub-card.is-confirming {
  box-shadow: 0 0 0 2px var(--color-accent, #22c55e), var(--shadow-card, 0 8px 32px rgba(0,0,0,0.4));
}

/* Status stripe */
.card-status-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  transition: background 0.3s;
}

/* ─── Card Head ─── */
.sub-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--text-muted);
  font-size: 0.82rem;
  margin-top: 0.6rem;
}

.type-badge {
  font-size: 0.62rem;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 0.6rem;
  letter-spacing: 0.06em;
}

.type-badge.new {
  background: rgba(99, 102, 241, 0.12);
  color: var(--primary-color, #6366f1);
  border: 1px solid rgba(99, 102, 241, 0.22);
}

.type-badge.update {
  background: var(--color-accent-muted, rgba(34, 197, 94, 0.12));
  color: var(--color-accent, #22c55e);
  border: 1px solid rgba(34, 197, 94, 0.22);
}

.sub-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
}

.field-ref {
  background: rgba(255,255,255,0.05);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.75rem;
  color: var(--text-muted);
  border: 1px solid rgba(255,255,255,0.08);
}

.dot { font-size: 1.4rem; line-height: 0; opacity: 0.4; }

/* ─── Card Body ─── */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.detail-item.full { grid-column: span 2; }

.detail-item label {
  display: block;
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 0.4rem;
}

.detail-item p {
  color: var(--text-primary);
  font-weight: 500;
  font-size: 0.92rem;
  margin: 0;
}

.mono {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 0.82rem !important;
  color: var(--text-secondary) !important;
}

.desc-text {
  background: rgba(255,255,255,0.03);
  padding: 0.85rem 1rem;
  border-radius: 8px;
  font-style: italic;
  font-size: 0.88rem;
  color: var(--text-secondary);
  border: 1px solid rgba(255,255,255,0.05);
  margin: 0;
  line-height: 1.6;
}

.sports-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sport-badge-mini {
  background: var(--glass-bg);
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  font-family: 'SF Mono', 'Fira Code', monospace;
  color: var(--text-secondary);
}

/* ─── Card Actions ─── */
.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  align-items: center;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(255,255,255,0.04);
}

/* Reject button */
.btn-reject-sub {
  background: transparent;
  color: var(--error, #ef4444);
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.88rem;
  border: 1px solid rgba(239, 68, 68, 0.25);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.btn-reject-sub:hover {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.45);
}

/* Approve button — uses global .btn-accent (green gradient) */
.btn-approve-sub {
  padding: 10px 22px;
  font-size: 0.88rem;
  font-weight: 700;
}

/* ─── Two-step Confirm Row ─── */
.confirm-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.confirm-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-right: auto;
}

.btn-cancel-confirm {
  background: transparent;
  color: var(--text-secondary);
  padding: 9px 18px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid var(--color-border, rgba(255,255,255,0.08));
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.btn-cancel-confirm:hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
}

.btn-do-confirm {
  padding: 9px 20px;
  border-radius: 10px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s;
}

/* Confirm approve — inherits .btn-accent from global style */

/* Confirm reject */
.btn-confirm-reject {
  background: rgba(239, 68, 68, 0.15);
  color: var(--error, #ef4444);
  border: 1px solid rgba(239, 68, 68, 0.4);
}

.btn-confirm-reject:hover {
  background: rgba(239, 68, 68, 0.25);
}
</style>
