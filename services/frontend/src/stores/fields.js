import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useFieldsStore = defineStore('fields', () => {
    const fields = ref([])
    const sports = ref([])
    const isLoading = ref(false)

    const userLocation = ref({ lat: 45.4642, lng: 9.1900 }) // Reference location for search
    const realUserLocation = ref(null) // Actual GPS location
    const searchAddress = ref('')
    const addressSuggestions = ref([])
    const isGeocoding = ref(false)
    const radiusKm = ref(20)
    const selectedSportIds = ref([])
    const minRating = ref(null)

    const selectedField = ref(null)

    const fetchSports = async () => {
        try {
            const { data } = await api.get('/fields/sports/')
            sports.value = data
        } catch (error) {
            console.error('Failed to fetch sports', error)
        }
    }

    const fetchNearbyFields = async () => {
        isLoading.value = true
        try {
            const params = {
                latitude: userLocation.value.lat,
                longitude: userLocation.value.lng,
                radius_km: radiusKm.value,
                page: 1,
                page_size: 50
            }

            if (selectedSportIds.value.length > 0) {
                params.sport_ids = selectedSportIds.value.join(',')
            }

            const { data } = await api.get('/fields/nearby', { params })
            fields.value = data.items
        } catch (error) {
            console.error('Failed to fetch fields', error)
            fields.value = []
        } finally {
            isLoading.value = false
        }
    }

    const fetchAddressSuggestions = async (query) => {
        if (!query || query.length < 3) {
            addressSuggestions.value = []
            return
        }

        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1&countrycodes=it`)
            const data = await response.json()
            addressSuggestions.value = data.map(item => ({
                display_name: item.display_name,
                lat: parseFloat(item.lat),
                lng: parseFloat(item.lon)
            }))
        } catch (error) {
            console.error("Suggestions error:", error)
        }
    }

    const selectSuggestion = (suggestion) => {
        userLocation.value = {
            lat: suggestion.lat,
            lng: suggestion.lng
        }
        searchAddress.value = suggestion.display_name
        addressSuggestions.value = []
        fetchNearbyFields()
    }

    const searchLocationByAddress = async () => {
        if (!searchAddress.value) return

        isGeocoding.value = true
        try {
            // Use Nominatim (OpenStreetMap free geocoder)
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(searchAddress.value)}&limit=1`)
            const data = await response.json()

            if (data && data.length > 0) {
                userLocation.value = {
                    lat: parseFloat(data[0].lat),
                    lng: parseFloat(data[0].lon)
                }
                fetchNearbyFields()
            } else {
                alert("Indirizzo non trovato. Riprova con più dettagli (es. città).")
            }
        } catch (error) {
            console.error("Geocoding error:", error)
        } finally {
            isGeocoding.value = false
        }
    }

    const getUserLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const loc = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    }
                    userLocation.value = loc
                    realUserLocation.value = loc
                    fetchNearbyFields()
                },
                (error) => {
                    console.error("Error getting location: ", error)
                    fetchNearbyFields()
                }
            )
        } else {
            fetchNearbyFields()
        }
    }

    const selectField = (field) => {
        selectedField.value = field
    }

    return {
        fields,
        sports,
        isLoading,
        isGeocoding,
        userLocation,
        realUserLocation,
        searchAddress,
        addressSuggestions,
        radiusKm,
        selectedSportIds,
        minRating,
        selectedField,
        fetchSports,
        fetchNearbyFields,
        fetchAddressSuggestions,
        selectSuggestion,
        searchLocationByAddress,
        getUserLocation,
        selectField
    }
})
