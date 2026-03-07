<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Receipt, Fuel, Wrench, Sparkles, Briefcase } from 'lucide-vue-next'
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

const categories = [
  { value: 'fuel_charging', label: 'Fuel / Charging', color: 'bg-amber-100 text-amber-700', icon: Fuel },
  { value: 'maintenance', label: 'Maintenance', color: 'bg-indigo-100 text-indigo-700', icon: Wrench },
  { value: 'improvements', label: 'Improvements', color: 'bg-pink-100 text-pink-700', icon: Sparkles },
  { value: 'operational', label: 'Operational', color: 'bg-teal-100 text-teal-700', icon: Briefcase },
]

const form = ref(defaultForm())

function defaultForm() {
  return {
    date: new Date().toISOString().slice(0, 10),
    category: 'fuel_charging',
    subcategory: '',
    description: '',
    amount: '',
    station_name: '',
    fuel_type: '',
    price_per_unit: '',
    quantity: '',
  }
}

const isFuel = computed(() => form.value.category === 'fuel_charging')

const totalExpenses = computed(() => items.value.reduce((sum, i) => sum + i.amount, 0))
const totalEntries = computed(() => items.value.length)

const categoryTotals = computed(() => {
  const map = {}
  for (const item of items.value) {
    if (!map[item.category]) map[item.category] = 0
    map[item.category] += item.amount
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

function getCategoryMeta(val) {
  return categories.find((c) => c.value === val) || { label: val, color: 'bg-gray-100 text-gray-600', icon: Receipt }
}

async function fetchItems() {
  loading.value = true
  try {
    const { data } = await api.get('/expenses/', {
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
  form.value = { date: item.date, category: item.category, subcategory: item.subcategory || '', description: item.description || '', amount: item.amount, station_name: item.station_name || '', fuel_type: item.fuel_type || '', price_per_unit: item.price_per_unit || '', quantity: item.quantity || '' }
  editingId.value = item.id
  showForm.value = true
}

async function saveItem() {
  const payload = { ...form.value, amount: parseFloat(form.value.amount) || 0, subcategory: form.value.subcategory || null, description: form.value.description || null, station_name: form.value.station_name || null, fuel_type: form.value.fuel_type || null, price_per_unit: form.value.price_per_unit ? parseFloat(form.value.price_per_unit) : null, quantity: form.value.quantity ? parseFloat(form.value.quantity) : null }
  try {
    if (editingId.value) {
      await api.put(`/expenses/${editingId.value}`, payload)
      toast.success('Expense updated')
    } else {
      await api.post('/expenses/', payload)
      toast.success('Expense added')
    }
    resetForm()
    await fetchItems()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to save expense')
  }
}

async function deleteItem(id) {
  if (!confirm('Delete this expense?')) return
  try {
    await api.delete(`/expenses/${id}`)
    toast.success('Expense deleted')
    await fetchItems()
  } catch (e) {
    toast.error('Failed to delete expense')
  }
}

function fmt(v) { return `\u20AC${Number(v).toFixed(2)}` }

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
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800">Expenses</h2>
      <button @click="showForm = !showForm; if (!showForm) resetForm()" class="inline-flex items-center gap-1.5 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 transition-colors shadow-sm">
        <Plus v-if="!showForm" :size="16" />
        {{ showForm ? 'Cancel' : 'Add Expense' }}
      </button>
    </div>

    <DateBrowser :range-label="rangeLabel" :view-mode="viewMode" @prev="prev" @next="next" @today="goToday" @update:view-mode="viewMode = $event" />

    <div v-if="items.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Total</p>
        <p class="text-lg font-bold text-rose-500 mt-0.5">{{ fmt(totalExpenses) }}</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide">Entries</p>
        <p class="text-lg font-bold text-gray-800 mt-0.5">{{ totalEntries }}</p>
      </div>
      <div v-for="[cat, total] in categoryTotals.slice(0, 2)" :key="cat" class="bg-white rounded-xl border border-gray-200 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 uppercase tracking-wide truncate">{{ getCategoryMeta(cat).label }}</p>
        <p class="text-lg font-bold text-gray-800 mt-0.5">{{ fmt(total) }}</p>
      </div>
    </div>

    <form v-if="showForm" @submit.prevent="saveItem" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-6 space-y-4">
      <h3 class="text-sm font-semibold text-gray-700">{{ editingId ? 'Edit Expense' : 'New Expense' }}</h3>

      <div>
        <label class="block text-xs font-medium text-gray-500 mb-2">Category</label>
        <div class="grid grid-cols-2 gap-2">
          <button v-for="c in categories" :key="c.value" type="button" @click="form.category = c.value"
            class="flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm font-medium transition-all"
            :class="form.category === c.value ? 'border-blue-500 bg-blue-50 text-blue-700 ring-2 ring-blue-200' : 'border-gray-200 text-gray-600 hover:border-gray-300'">
            <component :is="c.icon" :size="16" class="shrink-0" />
            <span class="truncate">{{ c.label }}</span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Date</label>
          <input v-model="form.date" type="date" required class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">Amount (&#8364;)</label>
          <input v-model="form.amount" type="number" step="0.01" required placeholder="0.00" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1.5">Description</label>
        <input v-model="form.description" type="text" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" placeholder="Optional description" />
      </div>

      <template v-if="isFuel">
        <div class="bg-amber-50 rounded-xl p-4 space-y-3 border border-amber-100">
          <p class="text-xs font-semibold text-amber-700 uppercase tracking-wide">Fuel Details</p>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1.5">Station</label>
              <input v-model="form.station_name" type="text" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="e.g. Galp" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1.5">Fuel Type</label>
              <select v-model="form.fuel_type" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
                <option value="">Select...</option>
                <option value="diesel">Diesel</option>
                <option value="gasoline">Gasoline</option>
                <option value="lpg">LPG</option>
                <option value="electric">Electric</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1.5">Price / Unit (&#8364;)</label>
              <input v-model="form.price_per_unit" type="number" step="0.001" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="1.650" />
            </div>
            <div>
              <label class="block text-xs font-medium text-gray-500 mb-1.5">Qty (L / kWh)</label>
              <input v-model="form.quantity" type="number" step="0.01" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="27.27" />
            </div>
          </div>
        </div>
      </template>

      <button type="submit" class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 transition-colors shadow-sm">{{ editingId ? 'Update Expense' : 'Save Expense' }}</button>
    </form>

    <div v-if="loading" class="flex items-center justify-center py-16"><div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div></div>

    <div v-else-if="items.length === 0" class="text-center py-16">
      <Receipt :size="48" class="text-gray-300 mx-auto mb-3" :stroke-width="1" />
      <p class="text-gray-400 text-sm">No expenses for this period</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="[month, group] in grouped" :key="month">
        <div class="flex items-center gap-2 mb-2 px-1">
          <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider">{{ monthLabel(month) }}</h3>
          <div class="flex-1 h-px bg-gray-200"></div>
          <span class="text-xs font-medium text-rose-500">-{{ fmt(group.reduce((s, i) => s + i.amount, 0)) }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in group" :key="item.id" class="bg-white rounded-xl border border-gray-200 p-4 hover:border-gray-300 transition-colors group">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="getCategoryMeta(item.category).color">
                  <component :is="getCategoryMeta(item.category).icon" :size="20" :stroke-width="1.5" />
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800">{{ getCategoryMeta(item.category).label }}</p>
                  <p class="text-xs text-gray-400 mt-0.5 truncate">
                    {{ formatDate(item.date) }} {{ monthLabel(item.date.slice(0, 7)).split(' ')[0] }}
                    <span v-if="item.description" class="ml-1">&middot; {{ item.description }}</span>
                  </p>
                  <p v-if="item.station_name" class="text-xs text-gray-400 truncate">
                    {{ item.station_name }}
                    <span v-if="item.fuel_type">&middot; {{ item.fuel_type }}</span>
                    <span v-if="item.quantity"> &middot; {{ item.quantity }} {{ item.fuel_type === 'electric' ? 'kWh' : 'L' }}</span>
                  </p>
                </div>
              </div>
              <div class="text-right shrink-0 ml-2">
                <p class="text-sm font-bold text-rose-500">-{{ fmt(item.amount) }}</p>
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
