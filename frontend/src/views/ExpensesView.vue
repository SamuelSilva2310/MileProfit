<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Receipt, Fuel, Wrench, Sparkles, Briefcase, Pencil, Trash2 } from 'lucide-vue-next'
import api from '../services/api'
import { useDateBrowser } from '../composables/useDateBrowser'
import { useVehicles } from '../composables/useVehicles'
import { useToast } from '../composables/useToast'
import { todayISO } from '../utils/date'
import DateBrowser from '../components/DateBrowser.vue'
import { useI18n } from '../i18n'

const { t } = useI18n()
const { viewMode, rangeLabel, startDateISO, endDateISO, prev, next, goToday } = useDateBrowser()
const { vehicles, primaryVehicleId } = useVehicles()
const toast = useToast()

const items = ref([])
const showForm = ref(false)
const editingId = ref(null)
const loading = ref(false)

const categories = [
  { value: 'fuel_charging', icon: Fuel },
  { value: 'maintenance', icon: Wrench },
  { value: 'improvements', icon: Sparkles },
  { value: 'operational', icon: Briefcase },
]
const categoryColors = {
  fuel_charging: 'bg-amber-100 text-amber-700',
  maintenance: 'bg-indigo-100 text-indigo-700',
  improvements: 'bg-pink-100 text-pink-700',
  operational: 'bg-teal-100 text-teal-700',
}

const form = ref(defaultForm())

function defaultForm() {
  return {
    date: todayISO(),
    category: 'fuel_charging',
    subcategory: '',
    description: '',
    amount: '',
    station_name: '',
    fuel_type: '',
    price_per_unit: '',
    quantity: '',
    vehicle_id: primaryVehicleId.value,
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
  const months = t('months.short')
  return `${months[parseInt(m) - 1]} ${y}`
}

function getCategoryMeta(val) {
  const cat = categories.find((c) => c.value === val)
  return {
    label: t(`expenses.categories.${val}`) || val,
    color: categoryColors[val] || 'bg-gray-100 text-gray-600',
    icon: cat?.icon || Receipt,
  }
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
  form.value = { date: item.date, category: item.category, subcategory: item.subcategory || '', description: item.description || '', amount: item.amount, station_name: item.station_name || '', fuel_type: item.fuel_type || '', price_per_unit: item.price_per_unit || '', quantity: item.quantity || '', vehicle_id: item.vehicle_id ?? null }
  editingId.value = item.id
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function saveItem() {
  const payload = { ...form.value, amount: parseFloat(form.value.amount) || 0, subcategory: form.value.subcategory || null, description: form.value.description || null, station_name: form.value.station_name || null, fuel_type: form.value.fuel_type || null, price_per_unit: form.value.price_per_unit ? parseFloat(form.value.price_per_unit) : null, quantity: form.value.quantity ? parseFloat(form.value.quantity) : null, vehicle_id: form.value.vehicle_id || null }
  try {
    if (editingId.value) {
      await api.put(`/expenses/${editingId.value}`, payload)
      toast.success(t('expenses.updated'))
    } else {
      await api.post('/expenses/', payload)
      toast.success(t('expenses.added'))
    }
    resetForm()
    await fetchItems()
  } catch (e) {
    toast.error(e.response?.data?.detail || t('expenses.saveFailed'))
  }
}

async function deleteItem(id) {
  if (!confirm(t('expenses.deleteConfirm'))) return
  try {
    await api.delete(`/expenses/${id}`)
    toast.success(t('expenses.deleted'))
    await fetchItems()
  } catch (e) {
    toast.error(t('expenses.deleteFailed'))
  }
}

function fmt(v) { return `\u20AC${Number(v).toFixed(2)}` }

function formatDate(d) {
  const date = new Date(d + 'T00:00:00')
  const days = t('days.short')
  return `${days[date.getDay()]}, ${date.getDate()}`
}

onMounted(fetchItems)
watch([startDateISO, endDateISO], fetchItems)
</script>

<template>
  <div class="p-4 lg:p-8 max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800 dark:text-gray-100">{{ t('expenses.title') }}</h2>
      <button @click="showForm = !showForm; if (!showForm) resetForm()" class="inline-flex items-center gap-1.5 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">
        <Plus v-if="!showForm" :size="16" />
        {{ showForm ? t('common.cancel') : t('expenses.add') }}
      </button>
    </div>

    <DateBrowser :range-label="rangeLabel" :view-mode="viewMode" @prev="prev" @next="next" @today="goToday" @update:view-mode="viewMode = $event" />

    <div v-if="items.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{{ t('expenses.total') }}</p>
        <p class="text-lg font-bold text-rose-500 mt-0.5">{{ fmt(totalExpenses) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{{ t('expenses.entries') }}</p>
        <p class="text-lg font-bold text-gray-800 dark:text-gray-100 mt-0.5">{{ totalEntries }}</p>
      </div>
      <div v-for="[cat, total] in categoryTotals.slice(0, 2)" :key="cat" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide truncate">{{ getCategoryMeta(cat).label }}</p>
        <p class="text-lg font-bold text-gray-800 dark:text-gray-100 mt-0.5">{{ fmt(total) }}</p>
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
      <form v-if="showForm" @submit.prevent="saveItem" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 mb-6 space-y-4">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ editingId ? t('expenses.edit') : t('expenses.new') }}</h3>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">{{ t('expenses.category') }}</label>
          <div class="grid grid-cols-2 gap-2">
            <button v-for="c in categories" :key="c.value" type="button" @click="form.category = c.value"
              class="flex items-center gap-2 px-3 py-2.5 rounded-xl border text-sm font-medium transition-all"
              :class="form.category === c.value ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 ring-2 ring-blue-200 dark:ring-blue-800' : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-500'">
              <component :is="c.icon" :size="16" class="shrink-0" />
              <span class="truncate">{{ t(`expenses.categories.${c.value}`) }}</span>
            </button>
          </div>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.date') }}</label>
          <input v-model="form.date" type="date" required class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.amount') }}</label>
          <input v-model="form.amount" type="number" step="0.01" required placeholder="0.00" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.description') }}</label>
          <input v-model="form.description" type="text" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" :placeholder="t('expenses.descriptionPlaceholder')" />
        </div>

        <template v-if="isFuel">
          <div class="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4 space-y-4 border border-amber-100 dark:border-amber-800/40">
            <p class="text-xs font-semibold text-amber-700 dark:text-amber-400 uppercase tracking-wide">{{ t('expenses.fuelDetails') }}</p>

            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.station') }}</label>
              <input v-model="form.station_name" type="text" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="e.g. Galp" />
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.fuelType') }}</label>
              <select v-model="form.fuel_type" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
                <option value="">{{ t('expenses.fuelTypeSelect') }}</option>
                <option value="diesel">{{ t('expenses.fuelTypes.diesel') }}</option>
                <option value="gasoline">{{ t('expenses.fuelTypes.gasoline') }}</option>
                <option value="lpg">{{ t('expenses.fuelTypes.lpg') }}</option>
                <option value="electric">{{ t('expenses.fuelTypes.electric') }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.pricePerUnit') }}</label>
                <input v-model="form.price_per_unit" type="number" step="0.001" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="1.650" />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('expenses.quantity') }}</label>
                <input v-model="form.quantity" type="number" step="0.01" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white" placeholder="27.27" />
              </div>
            </div>
          </div>
        </template>

        <div v-if="vehicles.length > 0">
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.vehicle') }}</label>
          <select v-model="form.vehicle_id" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
            <option :value="null">{{ t('earnings.noVehicle') }}</option>
            <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
        </div>

        <button type="submit" class="w-full bg-blue-600 text-white rounded-xl py-3.5 text-sm font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">{{ editingId ? t('expenses.update') : t('expenses.save') }}</button>
      </form>
    </Transition>

    <div v-if="loading" class="flex items-center justify-center py-16"><div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div></div>

    <div v-else-if="items.length === 0" class="text-center py-16">
      <Receipt :size="48" class="text-gray-300 mx-auto mb-3" :stroke-width="1" />
      <p class="text-gray-400 text-sm">{{ t('expenses.empty') }}</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="[month, group] in grouped" :key="month">
        <div class="flex items-center gap-2 mb-2 px-1">
          <h3 class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{{ monthLabel(month) }}</h3>
          <div class="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
          <span class="text-xs font-medium text-rose-500">-{{ fmt(group.reduce((s, i) => s + i.amount, 0)) }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in group" :key="item.id" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 transition-colors">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-start gap-3 min-w-0">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" :class="getCategoryMeta(item.category).color">
                  <component :is="getCategoryMeta(item.category).icon" :size="20" :stroke-width="1.5" />
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ getCategoryMeta(item.category).label }}</p>
                  <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5 truncate">
                    {{ formatDate(item.date) }} {{ monthLabel(item.date.slice(0, 7)).split(' ')[0] }}
                    <span v-if="item.description" class="ml-1">&middot; {{ item.description }}</span>
                  </p>
                  <p v-if="item.station_name" class="text-xs text-gray-400 dark:text-gray-500 truncate">
                    {{ item.station_name }}
                    <span v-if="item.fuel_type">&middot; {{ t(`expenses.fuelTypes.${item.fuel_type}`) || item.fuel_type }}</span>
                    <span v-if="item.quantity"> &middot; {{ item.quantity }} {{ item.fuel_type === 'electric' ? 'kWh' : 'L' }}</span>
                  </p>
                </div>
              </div>
              <div class="text-right shrink-0">
                <p class="text-sm font-bold text-rose-500">-{{ fmt(item.amount) }}</p>
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
