<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Line, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { TrendingUp, TrendingDown, Wallet, Info } from 'lucide-vue-next'
import api from '../services/api'
import { useDateBrowser } from '../composables/useDateBrowser'
import DateBrowser from '../components/DateBrowser.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Filler, Tooltip, Legend)

const { viewMode, rangeLabel, startDateISO, endDateISO, prev, next, goToday } = useDateBrowser()

const summary = ref(null)
const timeseries = ref([])
const platformData = ref([])
const categoryData = ref([])
const loading = ref(false)

async function fetchAll() {
  loading.value = true
  try {
    const params = { period: 'custom', start: startDateISO.value, end: endDateISO.value }
    const [s, ts, pb, cb] = await Promise.all([
      api.get('/dashboard/summary', { params }),
      api.get('/dashboard/timeseries', { params }),
      api.get('/dashboard/earnings-by-platform', { params }),
      api.get('/dashboard/expenses-by-category', { params }),
    ])
    summary.value = s.data
    timeseries.value = ts.data
    platformData.value = pb.data
    categoryData.value = cb.data
  } catch (e) {
    console.error('Dashboard load failed:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
watch([startDateISO, endDateISO], fetchAll)

function fmt(val) {
  if (val == null) return '-'
  return `\u20AC${val.toFixed(2)}`
}

const takeHome = computed(() => {
  if (!summary.value) return 0
  return summary.value.net_profit - summary.value.estimated_tax
})

const CATEGORY_LABELS = {
  fuel_charging: 'Fuel / Charging',
  maintenance: 'Maintenance',
  improvements: 'Improvements',
  operational: 'Operational',
}

const lineChartData = ref(null)
const doughnutPlatformData = ref(null)
const doughnutCategoryData = ref(null)

const earningsColor = '#3b82f6'
const expensesColor = '#f43f5e'
const profitColor = '#10b981'

const PLATFORM_COLORS = {
  Uber: '#111827',
  Bolt: '#16a34a',
  FreeNow: '#0284c7',
  Private: '#7c3aed',
  Other: '#6b7280',
}
const CATEGORY_COLORS = {
  fuel_charging: '#d97706',
  maintenance: '#4f46e5',
  improvements: '#db2777',
  operational: '#0d9488',
}
const fallbackColor = '#9ca3af'

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: { mode: 'index', intersect: false },
  plugins: {
    legend: { display: true, position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 16, font: { size: 11 } } },
    tooltip: {
      backgroundColor: '#1f2937',
      titleFont: { size: 12 },
      bodyFont: { size: 11 },
      padding: 10,
      cornerRadius: 8,
      callbacks: { label: (ctx) => `${ctx.dataset.label}: \u20AC${ctx.raw.toFixed(2)}` },
    },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { size: 10 }, maxRotation: 0 } },
    y: { grid: { color: '#f3f4f6' }, ticks: { font: { size: 10 }, callback: (v) => `\u20AC${v}` }, beginAtZero: true },
  },
  elements: { point: { radius: 3, hoverRadius: 5 }, line: { tension: 0.3 } },
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: { display: true, position: 'bottom', labels: { usePointStyle: true, pointStyle: 'circle', padding: 12, font: { size: 11 } } },
    tooltip: {
      backgroundColor: '#1f2937',
      padding: 10,
      cornerRadius: 8,
      callbacks: { label: (ctx) => `${ctx.label}: \u20AC${ctx.raw.toFixed(2)}` },
    },
  },
}

watch([timeseries, platformData, categoryData], () => {
  if (timeseries.value.length) {
    const labels = timeseries.value.map((p) => {
      const d = new Date(p.date)
      return `${d.getDate()}/${d.getMonth() + 1}`
    })
    lineChartData.value = {
      labels,
      datasets: [
        { label: 'Earnings', data: timeseries.value.map((p) => p.earnings), borderColor: earningsColor, backgroundColor: earningsColor + '18', fill: true },
        { label: 'Expenses', data: timeseries.value.map((p) => p.expenses), borderColor: expensesColor, backgroundColor: expensesColor + '18', fill: true },
        { label: 'Profit', data: timeseries.value.map((p) => p.profit), borderColor: profitColor, backgroundColor: profitColor + '18', fill: true },
      ],
    }
  } else {
    lineChartData.value = null
  }

  if (platformData.value.length) {
    doughnutPlatformData.value = {
      labels: platformData.value.map((p) => p.platform),
      datasets: [{
        data: platformData.value.map((p) => p.total),
        backgroundColor: platformData.value.map((p) => PLATFORM_COLORS[p.platform] || fallbackColor),
        borderWidth: 0,
      }],
    }
  } else {
    doughnutPlatformData.value = null
  }

  if (categoryData.value.length) {
    doughnutCategoryData.value = {
      labels: categoryData.value.map((c) => CATEGORY_LABELS[c.category] || c.category),
      datasets: [{
        data: categoryData.value.map((c) => c.total),
        backgroundColor: categoryData.value.map((c) => CATEGORY_COLORS[c.category] || fallbackColor),
        borderWidth: 0,
      }],
    }
  } else {
    doughnutCategoryData.value = null
  }
}, { immediate: true })

const statCards = ref([])
watch(summary, (s) => {
  if (!s) return
  statCards.value = [
    { label: 'Earnings', value: fmt(s.total_earnings), color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Expenses', value: fmt(s.total_expenses), color: 'text-rose-500', bg: 'bg-rose-50' },
    { label: 'Distance', value: `${s.total_km.toFixed(1)} km`, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'Hours', value: `${s.total_hours.toFixed(1)}h`, color: 'text-purple-600', bg: 'bg-purple-50' },
  ]
}, { immediate: true })
</script>

<template>
  <div class="p-4 lg:p-8 max-w-6xl mx-auto">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl lg:text-2xl font-bold text-gray-800">Dashboard</h2>
    </div>

    <DateBrowser
      :range-label="rangeLabel"
      :view-mode="viewMode"
      @prev="prev"
      @next="next"
      @today="goToday"
      @update:view-mode="viewMode = $event"
    />

    <div v-if="loading" class="flex items-center justify-center py-20">
      <div class="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
    </div>

    <template v-else-if="summary">
      <!-- Take-Home Hero Card -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 sm:p-6 mb-6">
        <div class="flex items-center justify-between gap-4">
          <div class="min-w-0">
            <div class="flex items-center gap-2 mb-1">
              <p class="text-sm font-medium text-gray-500">Take-Home Money</p>
              <span class="group relative cursor-help">
                <Info :size="14" class="text-gray-300" />
                <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-800 text-white text-[10px] rounded-lg px-2.5 py-1.5 whitespace-nowrap z-10">
                  Net Profit minus estimated IRS tax
                </span>
              </span>
            </div>
            <p class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight" :class="takeHome >= 0 ? 'text-emerald-600' : 'text-rose-600'">
              {{ fmt(takeHome) }}
            </p>
          </div>
          <div
            class="hidden sm:flex w-14 h-14 rounded-2xl items-center justify-center shrink-0"
            :class="takeHome >= 0 ? 'bg-emerald-50' : 'bg-rose-50'"
          >
            <Wallet v-if="takeHome >= 0" :size="28" class="text-emerald-500" />
            <TrendingDown v-else :size="28" class="text-rose-500" />
          </div>
        </div>

        <!-- Breakdown row: Net Profit | Expenses | Tax -->
        <div class="mt-4 pt-4 border-t border-gray-100 grid grid-cols-2 gap-2">
          <div>
            <p class="text-[10px] sm:text-xs font-medium text-gray-400 uppercase tracking-wide mb-0.5">Net Profit</p>
            <p class="text-base sm:text-lg font-bold" :class="summary.net_profit >= 0 ? 'text-emerald-600' : 'text-rose-600'">
              {{ fmt(summary.net_profit) }}
            </p>
            <p class="text-[10px] text-gray-400 mt-0.5 hidden sm:block">Earnings - Expenses</p>
          </div>
          <!--
          <div>
            <p class="text-[10px] sm:text-xs font-medium text-gray-400 uppercase tracking-wide mb-0.5">Expenses</p>
            <p class="text-base sm:text-lg font-bold text-rose-500">-{{ fmt(summary.total_expenses) }}</p>
            <p class="text-[10px] text-gray-400 mt-0.5 hidden sm:block">All costs</p>
          </div>
          -->
          <div>
            <div class="flex items-center gap-1 mb-0.5">
              <p class="text-[10px] sm:text-xs font-medium text-gray-400 uppercase tracking-wide">Est. Tax</p>
              <span class="group relative cursor-help">
                <Info :size="12" class="text-gray-300" />
                <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-800 text-white text-[10px] rounded-lg px-2.5 py-1.5 whitespace-nowrap z-10">
                  {{ summary.total_earnings > 0 ? ((summary.estimated_tax / summary.total_earnings) * 100).toFixed(0) : 0 }}% of earnings (set in Profile)
                </span>
              </span>
            </div>
            <p class="text-base sm:text-lg font-bold text-orange-500">-{{ fmt(summary.estimated_tax) }}</p>
            <p class="text-[10px] text-gray-400 mt-0.5 hidden sm:block">IRS estimate</p>
          </div>
        </div>
      </div>

      <!-- Stat Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4 mb-6">
        <div v-for="card in statCards" :key="card.label" class="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-2 h-2 rounded-full" :class="card.bg.replace('50', '400')"></div>
            <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">{{ card.label }}</p>
          </div>
          <p class="text-xl lg:text-2xl font-bold" :class="card.color">{{ card.value }}</p>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
          <h3 class="text-sm font-semibold text-gray-700 mb-4">Earnings vs Expenses</h3>
          <div v-if="lineChartData" class="h-56 lg:h-72">
            <Line :data="lineChartData" :options="lineChartOptions" />
          </div>
          <div v-else class="h-56 flex items-center justify-center text-sm text-gray-400">
            No data for this period
          </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
          <h3 class="text-sm font-semibold text-gray-700 mb-4">Earnings by Platform</h3>
          <div v-if="doughnutPlatformData" class="h-56 lg:h-72">
            <Doughnut :data="doughnutPlatformData" :options="doughnutOptions" />
          </div>
          <div v-else class="h-56 flex items-center justify-center text-sm text-gray-400">
            No earnings data
          </div>
        </div>
      </div>

      <!-- Bottom Row -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
          <h3 class="text-sm font-semibold text-gray-700 mb-4">Expenses by Category</h3>
          <div v-if="doughnutCategoryData" class="h-56 lg:h-64">
            <Doughnut :data="doughnutCategoryData" :options="doughnutOptions" />
          </div>
          <div v-else class="h-56 flex items-center justify-center text-sm text-gray-400">
            No expense data
          </div>
        </div>

        <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
          <h3 class="text-sm font-semibold text-gray-700 mb-4">Performance Metrics</h3>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Earn / km</p>
              <p class="text-lg font-bold text-gray-800">{{ fmt(summary.earnings_per_km) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Earn / hour</p>
              <p class="text-lg font-bold text-gray-800">{{ fmt(summary.earnings_per_hour) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Cost / km</p>
              <p class="text-lg font-bold text-gray-800">{{ fmt(summary.cost_per_km) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Profit / km</p>
              <p class="text-lg font-bold text-emerald-600">{{ fmt(summary.profit_per_km) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Profit / hour</p>
              <p class="text-lg font-bold text-emerald-600">{{ fmt(summary.profit_per_hour) }}</p>
            </div>
            <div class="space-y-1">
              <p class="text-xs text-gray-400 uppercase tracking-wide">Est. Tax</p>
              <p class="text-lg font-bold text-orange-500">{{ fmt(summary.estimated_tax) }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
