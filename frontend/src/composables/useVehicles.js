import { ref, computed } from 'vue'
import api from '../services/api'

const vehicles = ref([])
let fetched = false

export function useVehicles() {
  const primaryVehicle = computed(() => vehicles.value.find(v => v.is_primary) ?? null)
  const primaryVehicleId = computed(() => primaryVehicle.value?.id ?? null)

  async function fetchVehicles() {
    try {
      const { data } = await api.get('/vehicles/')
      vehicles.value = data
      fetched = true
    } catch {}
  }

  if (!fetched) fetchVehicles()

  async function createVehicle(name) {
    const { data } = await api.post('/vehicles/', { name })
    vehicles.value.push(data)
    return data
  }

  async function updateVehicle(id, payload) {
    const { data } = await api.patch(`/vehicles/${id}`, payload)
    if (payload.is_primary) {
      vehicles.value.forEach(v => { v.is_primary = v.id === id })
    } else {
      const idx = vehicles.value.findIndex(v => v.id === id)
      if (idx !== -1) vehicles.value[idx] = data
    }
    return data
  }

  async function deleteVehicle(id) {
    await api.delete(`/vehicles/${id}`)
    vehicles.value = vehicles.value.filter(v => v.id !== id)
  }

  return { vehicles, primaryVehicle, primaryVehicleId, fetchVehicles, createVehicle, updateVehicle, deleteVehicle }
}
