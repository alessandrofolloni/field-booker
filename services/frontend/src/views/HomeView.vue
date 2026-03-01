<script setup>
import { onMounted, watch } from 'vue'
import { useFieldsStore } from '@/stores/fields'

import MapComponent from '@/components/MapComponent.vue'
import FieldSidebar from '@/components/FieldSidebar.vue'

const fieldsStore = useFieldsStore()

onMounted(() => {
  fieldsStore.fetchSports()
  fieldsStore.getUserLocation()
})

</script>

<template>
  <div class="home-layout">
    
    <!-- Sidebar for filters and field details -->
    <aside class="sidebar">
      <FieldSidebar />
    </aside>
    
    <!-- Leaflet Map -->
    <main class="map-container">
      <MapComponent />
      
      <!-- Current location button -->
      <button class="location-btn" @click="fieldsStore.getUserLocation" title="Trova la mia posizione">
        📍
      </button>
    </main>
    
  </div>
</template>

<style scoped>
.home-layout {
  display: flex;
  height: 100%;
  min-height: 0;
  width: 100%;
  overflow: hidden;
  background-color: var(--background-color);
}

.sidebar {
  width: 420px;
  max-width: 45vw;
  background-color: transparent;
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-container {
  flex: 1;
  position: relative;
  z-index: 1;
}

.location-btn {
  position: absolute;
  top: 2rem;
  right: 2rem;
  z-index: 1000;
  background: var(--surface-color);
  backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  box-shadow: var(--shadow-xl);
  color: var(--text-primary);
}

.location-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

@media (max-width: 1024px) {
  .sidebar {
    width: 350px;
  }
}

@media (max-width: 768px) {
  .home-layout {
    flex-direction: column-reverse;
  }
  
  .sidebar {
    width: 100%;
    max-width: 100%;
    height: 50vh;
  }
}
</style>
