<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const submissions = ref([])
const isLoading = ref(true)

const fetchPendingSubmissions = async () => {
  isLoading.value = true
  try {
    const { data } = await api.get('/submissions/pending')
    submissions.value = data.items
  } catch (error) {
    console.error("Failed to fetch pending submissions:", error)
  } finally {
    isLoading.value = false
  }
}

const reviewSubmission = async (id, status) => {
  const label = status === 'approved' ? 'approvare' : 'rifiutare'
  if (!confirm(`Sei sicuro di voler ${label} questa segnalazione?`)) return

  try {
    await api.post(`/submissions/${id}/review`, {
      status: status,
      admin_notes: `Revisionato il ${new Date().toLocaleDateString()} alle ${new Date().toLocaleTimeString()}`
    })
    
    // Refresh list
    await fetchPendingSubmissions()
  } catch (error) {
    console.error(`Failed to ${status} submission:`, error)
    alert("Errore durante l'operazione. Verifica i permessi admin.")
  }
}

onMounted(() => {
  fetchPendingSubmissions()
})
</script>

<template>
  <div class="admin-view-wrapper animate-fade-in">
    <div class="admin-container">
      <header class="admin-page-header">
        <div class="header-content">
          <span class="view-badge">ADMIN AREA</span>
          <h1>Dashboard Segnalazioni</h1>
          <p class="description">Gestisci i nuovi campi inseriti dalla community</p>
        </div>
        <button class="btn-refresh" @click="fetchPendingSubmissions" :disabled="isLoading">
          <span class="refresh-icon">🔄</span>
        </button>
      </header>

      <main class="admin-main">
        <div v-if="isLoading" class="loading-container glass-panel">
          <div class="spinner"></div>
          <p>Caricamento segnalazioni...</p>
        </div>
        
        <div v-else-if="submissions.length === 0" class="empty-container glass-panel">
          <div class="empty-art">✅</div>
          <h2>Tutto in ordine!</h2>
          <p>Non ci sono nuove segnalazioni da revisionare al momento.</p>
        </div>
        
        <div v-else class="submission-grid">
          <div v-for="sub in submissions" :key="sub.id" class="sub-card glass-panel">
            <div class="card-status-indicator"></div>
            
            <div class="card-head">
              <div class="field-main-info">
                <div class="type-badge" :class="sub.submission_type">
                  {{ sub.submission_type === 'update' ? '🛠️ CORREZIONE' : '🏟️ NUOVO CAMPO' }}
                </div>
                <h3>{{ sub.field_data.name }}</h3>
                <div class="sub-meta">
                  <span>👤 {{ sub.user_name }}</span>
                  <span class="dot">•</span>
                  <span>📅 {{ new Date(sub.created_at).toLocaleDateString() }}</span>
                  <span v-if="sub.submission_type === 'update'" class="field-ref">
                    Ref ID: {{ sub.field_id.substring(0, 8) }}...
                  </span>
                </div>
              </div>
            </div>
            
            <div class="card-body">
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Posizione</label>
                  <p>{{ sub.field_data.address }}, {{ sub.field_data.city }}</p>
                </div>
                <div class="detail-item">
                  <label>Coordinate</label>
                  <p>{{ sub.field_data.latitude.toFixed(4) }}, {{ sub.field_data.longitude.toFixed(4) }}</p>
                </div>
                <div class="detail-item full">
                  <label>Sport</label>
                  <div class="sports-preview">
                    <span v-for="sportId in sub.field_data.sport_ids" :key="sportId" class="sport-badge-mini">
                      ID: {{ sportId.substring(0, 4) }}...
                    </span>
                  </div>
                </div>
                <div class="detail-item full" v-if="sub.field_data.description">
                  <label>Messaggio User</label>
                  <p class="desc-text">{{ sub.field_data.description }}</p>
                </div>
              </div>
            </div>
            
            <div class="card-actions">
              <button class="btn-reject-sub" @click="reviewSubmission(sub.id, 'rejected')">
                Scarta
              </button>
              <button class="btn-approve-sub" @click="reviewSubmission(sub.id, 'approved')">
                Approva & Pubblica
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
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

.admin-page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 3rem;
}

.view-badge {
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.15em;
  color: var(--accent-color);
  background: rgba(245, 158, 11, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
  margin-bottom: 1rem;
  display: inline-block;
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.description {
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.btn-refresh {
  padding: 12px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  font-size: 1.25rem;
}

/* Submission Cards */
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
  gap: 2rem;
}

.card-status-indicator {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--primary-color);
}

.sub-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-top: 0.8rem;
}

.type-badge {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
}

.type-badge.new {
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-color);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.type-badge.update {
  background: rgba(245, 158, 11, 0.15);
  color: var(--accent-color);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.field-ref {
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--text-muted);
}

.dot { font-size: 1.5rem; line-height: 0; }

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.detail-item.full { grid-column: span 2; }

.detail-item label {
  display: block;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  letter-spacing: 0.05em;
}

.detail-item p {
  color: var(--text-primary);
  font-weight: 500;
}

.desc-text {
  background: rgba(255, 255, 255, 0.03);
  padding: 1rem;
  border-radius: 8px;
  font-style: italic;
}

.sport-badge-mini {
  background: var(--glass-bg);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 6px;
  border: 1px solid var(--glass-border);
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-approve-sub {
  background: var(--primary-color);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-approve-sub:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
}

.btn-reject-sub {
  background: transparent;
  color: var(--error);
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-reject-sub:hover {
  background: rgba(239, 68, 68, 0.1);
}

/* States */
.loading-container, .empty-container {
  padding: 5rem 2rem;
  text-align: center;
  margin-top: 2rem;
}

.empty-art { font-size: 4rem; margin-bottom: 1rem; }

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--glass-bg);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
