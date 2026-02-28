<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { LMap, LTileLayer, LMarker, LPopup, LCircle } from '@vue-leaflet/vue-leaflet'
import { useFieldsStore } from '@/stores/fields'
import L from 'leaflet'

const fieldsStore = useFieldsStore()
const zoom = ref(13)
const mapRef = ref(null)

const center = computed(() => {
  return [fieldsStore.userLocation.lat, fieldsStore.userLocation.lng]
})

// Watch for both the map being ready and the location. 
// This ensures that as soon as we have a location AND the map is ready, we center it.
watch([() => fieldsStore.userLocation, () => mapRef.value?.leafletObject], ([newLoc, mapObj], [oldLoc, oldMapObj]) => {
  if (newLoc && mapObj) {
    // If it's the first time we get a valid map object, or the location changed
    const isNewMap = !oldMapObj && mapObj;
    const isNewLoc = oldLoc && (newLoc.lat !== oldLoc.lat || newLoc.lng !== oldLoc.lng);
    
    if (isNewMap || isNewLoc) {
      if (isNewMap) {
        // First mount, use setView for "immediate" feel
        mapObj.setView([newLoc.lat, newLoc.lng], zoom.value)
      } else {
        // Subsequent moves, use flyTo for smoothness
        mapObj.flyTo([newLoc.lat, newLoc.lng], zoom.value, {
          duration: 1.5,
          easeLinearity: 0.25
        })
      }
    }
  }
}, { deep: true, immediate: true })

// Watch for selected field to pan map
watch(() => fieldsStore.selectedField, (newField) => {
  if (newField && mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.flyTo(
      [newField.latitude, newField.longitude], 
      15, // Closer zoom when selecting a field
      { duration: 1.2 }
    )
  }
})

const onMarkerClick = (field) => {
  fieldsStore.selectField(field)
}

const getMarkerIconHTML = (field, selected = false) => {
  const primarySport = field.sports && field.sports.length > 0 ? field.sports[0] : null
  const color = primarySport ? primarySport.color : '#6366f1'
  const icon = primarySport ? primarySport.icon : '📍'

  return `
    <div class="field-marker-container${selected ? ' selected' : ''}">
      ${selected ? `<div class="field-marker-glow" style="background:${color}"></div>` : ''}
      <div class="field-marker-pulse" style="background:${color}"></div>
      <div class="field-marker-main" style="background:${color};${selected ? `box-shadow:0 0 0 3px white,0 0 18px ${color};` : ''}">
        <span class="field-marker-icon">${icon}</span>
      </div>
    </div>
  `
}

// Reactive icon creation — reads selectedField to trigger re-render on selection change
const getFieldIcon = (field) => {
  const selected = fieldsStore.selectedField?.id === field.id
  return L.divIcon({
    html: getMarkerIconHTML(field, selected),
    className: 'custom-field-icon',
    iconSize: [40, 48],
    iconAnchor: [20, 44],
    popupAnchor: [0, -44]
  })
}

// User location marker
const userIcon = L.divIcon({
  html: `
    <div class="user-position-marker">
      <div class="user-position-ring"></div>
      <div class="user-position-dot"></div>
    </div>
  `,
  className: 'user-location-custom',
  iconSize: [24, 24],
  iconAnchor: [12, 12]
})
</script>

<template>
  <div class="map-wrapper glass-panel">
    <l-map 
      ref="mapRef" 
      v-model:zoom="zoom" 
      :center="center" 
      :use-global-leaflet="false"
      class="full-height-map"
    >
      <l-tile-layer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        layer-type="base"
        name="CartoDB Dark"
        attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
      ></l-tile-layer>

      <!-- Glowy Search Radius (Layered for premium effect) -->
      <l-circle
        :lat-lng="center"
        :radius="fieldsStore.radiusKm * 1000"
        :weight="1"
        color="rgba(99, 102, 241, 0.4)"
        fillColor="rgba(99, 102, 241, 0.05)"
        :dashArray="'10, 15'"
      />
      <l-circle
        :lat-lng="center"
        :radius="fieldsStore.radiusKm * 1000 + 400"
        :weight="3"
        color="rgba(99, 102, 241, 0.1)"
        :fill="false"
      />

      <!-- User Location -->
      <l-marker :lat-lng="center" :icon="userIcon" :z-index-offset="1000">
        <l-popup>Sei qui</l-popup>
      </l-marker>

      <!-- Fields Markers -->
      <l-marker
        v-for="field in fieldsStore.fields"
        :key="field.id"
        :lat-lng="[field.latitude, field.longitude]"
        :icon="getFieldIcon(field)"
        @click="onMarkerClick(field)"
      >
        <l-popup>
          <div class="modern-popup">
            <header class="popup-header">
              <h3>{{ field.name }}</h3>
              <div class="popup-rating" v-if="field.avg_rating">
                ⭐ {{ field.avg_rating.toFixed(1) }}
              </div>
            </header>
            <p class="popup-address">📍 {{ field.address }}</p>
            <div class="popup-tags">
              <span v-for="sport in field.sports" :key="sport.id" class="tag" :style="{ background: sport.color + '22', color: sport.color }">
                {{ sport.icon }} {{ sport.name }}
              </span>
            </div>
            <button class="btn-popup-action" @click="onMarkerClick(field)">
              Vedi Disponibilità
            </button>
          </div>
        </l-popup>
      </l-marker>
    </l-map>
  </div>
</template>

<style>
.map-wrapper {
  height: 100%;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.full-height-map {
  height: 100%;
  width: 100%;
}

/* User Marker */
.user-position-marker {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-position-dot {
  width: 12px;
  height: 12px;
  background: #3b82f6;
  border: 2px solid white;
  border-radius: 50%;
  z-index: 2;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.8);
}

.user-position-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  background: rgba(59, 130, 246, 0.3);
  border-radius: 50%;
  animation: ripple 2s infinite;
}

@keyframes ripple {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(3); opacity: 0; }
}

/* Field Marker */
.field-marker-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 48px;
}

.field-marker-main {
  width: 34px;
  height: 34px;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(255,255,255,0.9);
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  z-index: 2;
  position: relative;
  transition: box-shadow 0.2s;
}

.field-marker-icon {
  transform: rotate(45deg);
  font-size: 15px;
  display: block;
  line-height: 1;
}

.field-marker-pulse {
  position: absolute;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  z-index: 1;
  opacity: 0.45;
  animation: marker-pulse 2.2s infinite;
}

@keyframes marker-pulse {
  0%   { transform: scale(1);   opacity: 0.45; }
  100% { transform: scale(2.8); opacity: 0; }
}

/* Selected marker glow */
.field-marker-container.selected .field-marker-glow {
  position: absolute;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  top: -8px;
  left: -5px;
  filter: blur(8px);
  animation: marker-glow 1.6s ease-in-out infinite;
  z-index: 0;
}

@keyframes marker-glow {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50%       { opacity: 0.5; transform: scale(1.3); }
}

/* Modern Popup Styles */
.modern-popup {
  padding: 12px;
  min-width: 200px;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.popup-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: white;
}

.popup-address {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.popup-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 12px;
}

.tag {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.btn-popup-action {
  width: 100%;
  background: var(--primary-color);
  color: white;
  padding: 8px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
