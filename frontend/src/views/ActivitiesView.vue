<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, MapPinned } from 'lucide-vue-next'
import api from '../services/api'
import { useDateBrowser } from '../composables/useDateBrowser'
import { useToast } from '../composables/useToast'
import DateBrowser from '../components/DateBrowser.vue'

const { viewMode, rangeLabel, startDateISO, endDateISO, prev, next, goToday } = useDateBrowser()
const toast = useToast()

const items = ref([])
const showForm = ref(false)
const editingId = ref(null)
const loading = ref(false)

const form = ref(defaultForm())

function defaultForm() {
  return {
    date: new Date().toISOString().slice(0, 10),
    start_km: '',
    end_km: '',
    start_time: '',
    end_time: '',
  }
}

const totalKm = computed(() => items.value.reduce((sum, i) => sum + i.total_km, 0))
const avgKm = computed(() => items.value.length ? totalKm.value / items.value.length : 0)
const totalEntries = computed(() => items.value.length)

const grouped = computed(() => {
  const groups = {}
  for (const item of items.value) {
    const key = item.date.slice(0, 7)
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
  }
  return Object.entries(groups).sort(([a], [b]) => b.localeCompare(a))
})

function monthLabel(key) {
  const [y, m] = key.split('-')
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  return `${months[parseInt(m) - 1]} ${y}`
}

async function fetchItems() {
  loading.value = true
  try {
    const { data } = await api.get('/activities/', {
      params: { start_date: startDateISO.value, end_date: endDateISO.value },
    })
    items.value = data
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = defaultForm()
  editingId.value = null
  showForm.value = false
}

function editItem(item) {
  form.value = {
    date: item.date,
    start_km: item.start_km,
    end_km: item.end_km,
    start_time: item.start_time?.slice(0, 5) || '',
    end_time: item.end_time?.slice(0, 5) || '',
  }
  editingId.value = item.id
  showForm.value = true
}

async function saveItem() {
  const payload = {
    ...form.value,
    start_km: parseFloat(form.value.start_km),
    end_km: parseFloat(form.value.end_km),
    start_time: form.value.start_time || null,
    end_time: form.value.end_time || null,
  }
  try {
    if (editingId.value) {
      await api.put(`/activities/${editingId.value}`, payload)
      toast.success('Activity updated')
    } else {
      await api.post('/activities/', payload)
      toast.success('Activity logged')
    }
    resetForm()
    await fetchItems()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save activity')
  }
}

async function deleteItem(id) {
  if (!confirm('Delete this activity?')) return
  try {
    await api.delete(`/activities/${id}`)
    toast.success('Activity deleted')
    await fetchItems()
  } catch (e) {
    toast.error('Failed to delete activity')
  }
}

function formatDate(d) {
  const date = new Date(d + 'T00:00:00')
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  return `${days[date.getDay()]}, ${date.getDate()}`
}

onMounted(fetchItems)
watch([startDateISO, endDateISO], fetchItems)
</script>

<template>
  <div class="p-4 lg:p-8 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800">Daily Activity</h2>
      <button
        @click="showForm = !showForm; if (!showForm) resetForm()"
        class="inline-flex items-center gap-1.5 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 transition-colors shadow-sm"
      >
        <Plus v-if="!showForm" :size="16" />
        {{ showForm ? 'Cancel' : 'Log Activity' }}
      </button>
    </div>

    <DateBrowser
      :range-label="rangeLabel"
      :view-mode="viewMode"
      @prev="prev"
      @next="next"
      @today="goToday"
      @update:view-mode="viewMode = $event"
    />

    <div v-if="items.length" class="grid grid-cols-3 gap-3 mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-3 text-center">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Entries</p>
        <p class="text-lg font-bold text-gray-800 mt-0.5">{{ totalEntries }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3 text-center">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Total KM</p>
        <p class="text-lg font-bold text-blue-600 mt-0.5">{{ totalKm.toFixed(1) }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3 text-center">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Avg / Day</p>
        <p class="text-lg font-bold text-amber-600 mt-0.5">{{ avgKm.toFixed(1) }}</p>
      </div>
    </div>

    <form v-if="showForm" @submit.prevent="saveItem" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-6 space-y-4">
      <h3 class="text-sm font-semibold text-gray-700">{{ editingId ? 'Edit Activity' : 'New Activity' }}</h3>
      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1.5">Date</label>
        <input v-model="form.date" type="date" required class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Start KM</label>
          <input v-model="form.start_km" type="number" step="0.1" required placeholder="0.0" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">End KM</label>
          <input v-model="form.end_km" type="number" step="0.1" required placeholder="0.0" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Start Time</label>
          <input v-model="form.start_time" type="time" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">End Time</label>
          <input v-model="form.end_time" type="time" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
      </div>
      <button type="submit" class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 transition-colors shadow-sm">
        {{ editingId ? 'Update Activity' : 'Save Activity' }}
      </button>
    </form>

    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <div v-else-if="items.length === 0" class="text-center py-16">
      <MapPinned :size="48" class="text-gray-300 mx-auto mb-3" :stroke-width="1" />
      <p class="text-gray-400 text-sm">No activities for this period</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="[month, group] in grouped" :key="month">
        <div class="flex items-center gap-2 mb-2 px-1">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ monthLabel(month) }}</h3>
          <div class="flex-1 h-px bg-gray-200"></div>
          <span class="text-xs text-gray-400">{{ group.reduce((s, i) => s + i.total_km, 0).toFixed(1) }} km</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in group" :key="item.id" class="bg-white rounded-xl border border-gray-200 p-4 hover:border-gray-300 transition-colors group">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center text-xs font-bold shrink-0">
                  {{ formatDate(item.date).split(',')[0] }}
                </div>
                <div>
                  <p class="text-sm font-medium text-gray-800">{{ formatDate(item.date).split(', ')[1] }} {{ monthLabel(item.date.slice(0, 7)).split(' ')[0] }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">
                    {{ item.start_km.toLocaleString() }} &rarr; {{ item.end_km.toLocaleString() }} km
                    <span v-if="item.start_time && item.end_time" class="ml-2">&middot; {{ item.start_time.slice(0, 5) }} &ndash; {{ item.end_time.slice(0, 5) }}</span>
                  </p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm font-bold text-blue-600">{{ item.total_km.toFixed(1) }} km</p>
                <div class="flex gap-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="editItem(item)" class="text-xs text-gray-400 hover:text-blue-600">Edit</button>
                  <button @click="deleteItem(item.id)" class="text-xs text-gray-400 hover:text-rose-500">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
