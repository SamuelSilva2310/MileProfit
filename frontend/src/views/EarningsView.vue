<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, Coins, Pencil, Trash2, ShieldCheck, CheckCircle, Clock, Car } from 'lucide-vue-next'
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

const platforms = ['Uber', 'Bolt', 'FreeNow', 'Private', 'Other']
const NON_TAXABLE_PLATFORMS = ['Private']

const form = ref(defaultForm())

function defaultForm() {
  return {
    date: todayISO(),
    platform: 'Uber',
    total_earnings: '',
    tips: '',
    is_taxable: true,
    notes: '',
    is_paid: true,
    vehicle_id: primaryVehicleId.value,
  }
}

const isPrivate = computed(() => form.value.platform === 'Private')

const totalEarnings = computed(() => items.value.reduce((sum, i) => sum + i.total_earnings + i.tips, 0))
const totalTips = computed(() => items.value.reduce((sum, i) => sum + i.tips, 0))
const unpaidTotal = computed(() => items.value.filter(i => i.platform === 'Private' && !i.is_paid).reduce((sum, i) => sum + i.total_earnings, 0))

const platformTotals = computed(() => {
  const map = {}
  for (const item of items.value) {
    if (!map[item.platform]) map[item.platform] = 0
    map[item.platform] += item.total_earnings + item.tips
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
  form.value = {
    date: item.date,
    platform: item.platform,
    total_earnings: item.total_earnings,
    tips: item.tips,
    is_taxable: item.is_taxable ?? true,
    notes: item.notes || '',
    is_paid: item.is_paid ?? true,
    vehicle_id: item.vehicle_id ?? null,
  }
  editingId.value = item.id
  showForm.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(() => form.value.platform, (newPlatform) => {
  form.value.is_taxable = !NON_TAXABLE_PLATFORMS.includes(newPlatform)
})

async function saveItem() {
  const payload = {
    ...form.value,
    total_earnings: parseFloat(form.value.total_earnings) || 0,
    tips: parseFloat(form.value.tips) || 0,
    notes: form.value.notes || null,
    vehicle_id: form.value.vehicle_id || null,
  }
  try {
    if (editingId.value) {
      await api.put(`/earnings/${editingId.value}`, payload)
      toast.success(t('earnings.updated'))
    } else {
      await api.post('/earnings/', payload)
      toast.success(t('earnings.added'))
    }
    resetForm()
    await fetchItems()
  } catch (e) {
    toast.error(e.response?.data?.detail || t('earnings.saveFailed'))
  }
}

async function deleteItem(id) {
  if (!confirm(t('earnings.deleteConfirm'))) return
  try {
    await api.delete(`/earnings/${id}`)
    toast.success(t('earnings.deleted'))
    await fetchItems()
  } catch (e) {
    toast.error(t('earnings.deleteFailed'))
  }
}

async function togglePaid(item) {
  try {
    await api.put(`/earnings/${item.id}`, { is_paid: !item.is_paid })
    item.is_paid = !item.is_paid
  } catch (e) {
    toast.error(t('earnings.saveFailed'))
  }
}

function fmt(v) { return `€${Number(v).toFixed(2)}` }

function formatDate(d) {
  const date = new Date(d + 'T00:00:00')
  const days = t('days.short')
  return `${days[date.getDay()]}, ${date.getDate()}`
}

const platformStyle = {
  Uber: { bg: 'bg-gray-900', text: 'text-white' },
  Bolt: { bg: 'bg-green-500', text: 'text-white' },
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
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800 dark:text-gray-100">{{ t('earnings.title') }}</h2>
      <button @click="showForm = !showForm; if (!showForm) resetForm()" class="inline-flex items-center gap-1.5 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">
        <Plus v-if="!showForm" :size="16" />
        {{ showForm ? t('common.cancel') : t('earnings.add') }}
      </button>
    </div>

    <DateBrowser :range-label="rangeLabel" :view-mode="viewMode" @prev="prev" @next="next" @today="goToday" @update:view-mode="viewMode = $event" />

    <!-- Summary cards -->
    <div v-if="items.length" class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{{ t('earnings.total') }}</p>
        <p class="text-lg font-bold text-green-600 mt-0.5">{{ fmt(totalEarnings) }}</p>
      </div>
      <div v-if="totalTips > 0" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{{ t('earnings.tips').replace(' (€)', '') }}</p>
        <p class="text-lg font-bold text-amber-600 mt-0.5">{{ fmt(totalTips) }}</p>
      </div>
      <div v-if="unpaidTotal > 0" class="bg-rose-50 rounded-xl border border-rose-100 p-3">
        <p class="text-[10px] sm:text-xs text-rose-400 uppercase tracking-wide">{{ t('earnings.unpaid') }}</p>
        <p class="text-lg font-bold text-rose-600 mt-0.5">{{ fmt(unpaidTotal) }}</p>
      </div>
      <div v-for="[platform, total] in platformTotals" :key="platform" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-3">
        <div class="flex items-center gap-1.5 mb-0.5">
          <span class="w-2 h-2 rounded-full shrink-0" :class="getPlatformStyle(platform).bg"></span>
          <p class="text-[10px] sm:text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide">{{ platform }}</p>
        </div>
        <p class="text-lg font-bold text-gray-800 dark:text-gray-100">{{ fmt(total) }}</p>
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
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ editingId ? t('earnings.edit') : t('earnings.new') }}</h3>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.date') }}</label>
          <input v-model="form.date" type="date" required class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.platform') }}</label>
          <select v-model="form.platform" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
            <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.amount') }}</label>
          <input v-model="form.total_earnings" type="number" step="0.01" required placeholder="0.00" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <div v-if="!isPrivate">
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.tips') }}</label>
          <input v-model="form.tips" type="number" step="0.01" placeholder="0.00" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        </div>

        <!-- Private-specific fields -->
        <template v-if="isPrivate">
          <div>
            <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.notes') }}</label>
            <input v-model="form.notes" type="text" :placeholder="t('earnings.notesPlaceholder')" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
          </div>
          <label class="flex items-center gap-3 cursor-pointer select-none">
            <div class="relative">
              <input type="checkbox" v-model="form.is_paid" class="sr-only peer" />
              <div class="w-10 h-6 bg-gray-200 rounded-full peer-checked:bg-emerald-500 transition-colors"></div>
              <div class="absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform peer-checked:translate-x-4"></div>
            </div>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('earnings.isPaid') }}</span>
          </label>
        </template>

        <!-- Vehicle selector (only if user has vehicles configured) -->
        <div v-if="vehicles.length > 0">
          <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('earnings.vehicle') }}</label>
          <select v-model="form.vehicle_id" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow bg-white">
            <option :value="null">{{ t('earnings.noVehicle') }}</option>
            <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.name }}</option>
          </select>
        </div>

        <button type="submit" class="w-full bg-blue-600 text-white rounded-xl py-3.5 text-sm font-semibold hover:bg-blue-700 active:bg-blue-800 transition-colors shadow-sm">{{ editingId ? t('earnings.update') : t('earnings.save') }}</button>
      </form>
    </Transition>

    <div v-if="loading" class="flex items-center justify-center py-16"><div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div></div>

    <div v-else-if="items.length === 0" class="text-center py-16">
      <Coins :size="48" class="text-gray-300 mx-auto mb-3" :stroke-width="1" />
      <p class="text-gray-400 text-sm">{{ t('earnings.empty') }}</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="[month, group] in grouped" :key="month">
        <div class="flex items-center gap-2 mb-2 px-1">
          <h3 class="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">{{ monthLabel(month) }}</h3>
          <div class="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
          <span class="text-xs font-medium text-green-600">{{ fmt(group.reduce((s, i) => s + i.total_earnings + i.tips, 0)) }}</span>
        </div>
        <div class="space-y-2">
          <div v-for="item in group" :key="item.id" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 transition-colors" :class="item.platform === 'Private' && !item.is_paid ? 'border-rose-200 bg-rose-50/30 dark:bg-rose-900/20' : ''">
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-start gap-3 min-w-0">
                <span class="text-xs font-semibold px-2.5 py-1 rounded-lg shrink-0 mt-0.5" :class="[getPlatformStyle(item.platform).bg, getPlatformStyle(item.platform).text]">{{ item.platform }}</span>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 dark:text-gray-100">{{ formatDate(item.date) }} {{ monthLabel(item.date.slice(0, 7)).split(' ')[0] }}</p>
                  <div class="flex flex-wrap gap-x-3 text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                    <span v-if="item.tips > 0">{{ t('earnings.tips').replace(' (€)', '') }}: {{ fmt(item.tips) }}</span>
                    <span v-if="item.is_taxable === false" class="text-emerald-500 font-medium flex items-center gap-0.5">
                      <ShieldCheck :size="12" />{{ t('earnings.notTaxable') }}
                    </span>
                    <span v-if="item.notes" class="text-gray-500 dark:text-gray-400 truncate max-w-[140px]">{{ item.notes }}</span>
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-end gap-1.5 shrink-0">
                <p class="text-sm font-bold text-green-600">{{ fmt(item.total_earnings) }}</p>
                <div class="flex gap-1 items-center">
                  <!-- Paid toggle for Private -->
                  <button
                    v-if="item.platform === 'Private'"
                    @click="togglePaid(item)"
                    :title="item.is_paid ? t('earnings.paid') : t('earnings.unpaid')"
                    class="p-1.5 rounded-lg transition-colors"
                    :class="item.is_paid ? 'text-emerald-500 hover:bg-emerald-50' : 'text-rose-400 hover:bg-rose-50'"
                  >
                    <CheckCircle v-if="item.is_paid" :size="14" />
                    <Clock v-else :size="14" />
                  </button>
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
