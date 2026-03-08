<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Coins, Pencil, Trash2 } from 'lucide-vue-next'
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

const platforms = ['Uber', 'Bolt', 'FreeNow', 'Private', 'Other']

const form = ref(defaultForm())

function defaultForm() {
  return {
    date: new Date().toISOString().slice(0, 10),
    platform: 'Uber',
    total_earnings: '',
    commission: '',
    tips: '',
    bonuses: '',
  }
}

const totalEarnings = computed(() => items.value.reduce((sum, i) => sum + i.total_earnings + i.tips + i.bonuses, 0))
const totalTips = computed(() => items.value.reduce((sum, i) => sum + i.tips, 0))

const platformTotals = computed(() => {
  const map = {}
  for (const item of items.value) {
    if (!map[item.platform]) map[item.platform] = 0
    map[item.platform] += item.total_earnings + item.tips + item.bonuses
  }
  return Object.entries(map).sort(([, a], [, b]) => b - a)
})

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
    const { data } = await api.get('/earnings/', {
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
  form.value = { date: item.date, platform: item.platform, total_earnings: item.total_earnings, commission: item.commission, tips: item.tips, bonuses: item.bonuses }
  editingId.value = item.id
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function saveItem() {
  const payload = { ...form.value, total_earnings: parseFloat(form.value.total_earnings) || 0, commission: parseFloat(form.value.commission) || 0, tips: parseFloat(form.value.tips) || 0, bonuses: parseFloat(form.value.bonuses) || 0 }
  try {
    if (editingId.value) {
      await api.put(`/earnings/${editingId.value}`, payload)
      toast.success('Earning updated')
    } else {
      await api.post('/earnings/', payload)
      toast.success('Earning added')
    }
    resetForm()
    await fetchItems()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save earning')
  }
}

async function deleteItem(id) {
  if (!confirm('Delete this earning?')) return
  try {
    await api.delete(`/earnings/${id}`)
    toast.success('Earning deleted')
    await fetchItems()
  } catch (e) {
    toast.error('Failed to delete earning')
  }
}

function fmt(v) { return `\u20AC${Number(v).toFixed(2)}` }

function formatDate(d) {
  const date = new Date(d + 'T00:00:00')
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  return `${days[date.getDay()]}, ${date.getDate()}`
}

const platformStyle = {
  Uber: { bg: 'bg-gray-900', text: 'text-white' },
  Bolt: { bg: 'bg-green-600', text: 'text-white' },
  FreeNow: { bg: 'bg-sky-600', text: 'text-white' },
  Private: { bg: 'bg-violet-600', text: 'text-white' },
  Other: { bg: 'bg-gray-200', text: 'text-gray-700' },
}

function getPlatformStyle(p) { return platformStyle[p] || platformStyle.Other }

onMounted(fetchItems)
watch([startDateISO, endDateISO], fetchItems)
</script>

<template>
  <div class="p-4 lg:p-8 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800">Earnings</h2>
      <button @click="showForm = !showForm; if (!showForm) resetForm()" class="inline-flex items-center gap-1.5 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">
        <Plus v-if="!showForm" :size="16" />
        {{ showForm ? 'Cancel' : 'Add Earning' }}
      </button>
    </div>

    <DateBrowser :range-label="rangeLabel" :view-mode="viewMode" @prev="prev" @next="next" @today="goToday" @update:view-mode="viewMode = $event" />

    <div v-if="items.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Total</p>
        <p class="text-lg font-bold text-green-600 mt-0.5">{{ fmt(totalEarnings) }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Tips</p>
        <p class="text-lg font-bold text-amber-600 mt-0.5">{{ fmt(totalTips) }}</p>
      </div>
      <div v-for="[platform, total] in platformTotals.slice(0, 2)" :key="platform" class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">{{ platform }}</p>
        <p class="text-lg font-bold text-gray-800 mt-0.5">{{ fmt(total) }}</p>
      </div>
    </div>

    <!-- Form -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <form v-if="showForm" @submit.prevent="saveItem" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-6 space-y-4">
        <h3 class="text-sm font-semibold text-gray-700">{{ editingId ? 'Edit Earning' : 'New Earning' }}</h3>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Date</label>
          <input v-model="form.date" type="date" required class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Platform</label>
          <select v-model="form.platform" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
            <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Earnings (&#8364;)</label>
          <input v-model="form.total_earnings" type="number" step="0.01" required placeholder="0.00" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Commission (&#8364;)</label>
          <input v-model="form.commission" type="number" step="0.01" placeholder="0.00" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1.5">Tips (&#8364;)</label>
            <input v-model="form.tips" type="number" step="0.01" placeholder="0.00" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-500 mb-1.5">Bonuses (&#8364;)</label>
            <input v-model="form.bonuses" type="number" step="0.01" placeholder="0.00" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
          </div>
        </div>

        <button type="submit" class="w-full bg-blue-600 text-white rounded-xl py-3.5 text-sm font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">{{ editingId ? 'Update Earning' : 'Save Earning' }}</button>
      </form>
    </Transition>

    <div v-if="loading" class="flex items-center justify-center py-16"><div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div></div>

    <div v-else-if="items.length === 0" class="text-center py-16">
      <Coins :size="48" class="text-gray-300 mx-auto mb-3" :stroke-width="1" />
      <p class="text-gray-400 text-sm">No earnings for this period</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="[month, group] in grouped" :key="month">
        <div class="flex items-center gap-2 mb-2 px-1">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ monthLabel(month) }}</h3>
          <div class="flex-1 h-px bg-gray-200"></div>
          <span class="text-xs font-medium text-green-600">{{ fmt(group.reduce((s, i) => s + i.total_earnings + i.tips + i.bonuses, 0)) }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in group" :key="item.id" class="bg-white rounded-xl border border-gray-200 p-4 transition-colors">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-start gap-3 min-w-0">
                <span class="text-xs font-semibold px-2.5 py-1 rounded-lg shrink-0 mt-0.5" :class="[getPlatformStyle(item.platform).bg, getPlatformStyle(item.platform).text]">{{ item.platform }}</span>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800">{{ formatDate(item.date) }} {{ monthLabel(item.date.slice(0, 7)).split(' ')[0] }}</p>
                  <div class="flex flex-wrap gap-x-3 text-xs text-gray-400 mt-0.5">
                    <span v-if="item.tips > 0">Tips: {{ fmt(item.tips) }}</span>
                    <span v-if="item.bonuses > 0">Bonus: {{ fmt(item.bonuses) }}</span>
                    <span v-if="item.commission > 0">Comm: {{ fmt(item.commission) }}</span>
                  </div>
                </div>
              </div>
              <div class="text-right shrink-0">
                <p class="text-sm font-bold text-green-600">{{ fmt(item.total_earnings) }}</p>
                <div class="flex gap-1 mt-1.5 justify-end">
                  <button @click="editItem(item)" class="p-1.5 rounded-lg text-gray-400 hover:text-blue-600 hover:bg-blue-50 active:bg-blue-100 transition-colors">
                    <Pencil :size="14" />
                  </button>
                  <button @click="deleteItem(item.id)" class="p-1.5 rounded-lg text-gray-400 hover:text-rose-500 hover:bg-rose-50 active:bg-rose-100 transition-colors">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
