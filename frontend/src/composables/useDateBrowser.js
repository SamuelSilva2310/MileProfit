import { ref, computed } from 'vue'
import { useI18n } from '../i18n'

export function useDateBrowser() {
  const { t } = useI18n()
  const viewMode = ref('month')
  const currentDate = ref(new Date())

  function startOfWeek(d) {
    const date = new Date(d)
    const day = date.getDay()
    const diff = day === 0 ? -6 : 1 - day
    date.setDate(date.getDate() + diff)
    return date
  }

  const rangeStart = computed(() => {
    if (viewMode.value === 'week') {
      return startOfWeek(currentDate.value)
    }
    const d = new Date(currentDate.value)
    return new Date(d.getFullYear(), d.getMonth(), 1)
  })

  const rangeEnd = computed(() => {
    if (viewMode.value === 'week') {
      const s = startOfWeek(currentDate.value)
      s.setDate(s.getDate() + 6)
      return s
    }
    const d = new Date(currentDate.value)
    return new Date(d.getFullYear(), d.getMonth() + 1, 0)
  })

  const rangeLabel = computed(() => {
    const months = t('months.short')
    if (viewMode.value === 'week') {
      const s = rangeStart.value
      const e = rangeEnd.value
      return `${s.getDate()} ${months[s.getMonth()]} - ${e.getDate()} ${months[e.getMonth()]} ${e.getFullYear()}`
    }
    const d = currentDate.value
    return `${months[d.getMonth()]} ${d.getFullYear()}`
  })

  function prev() {
    const d = new Date(currentDate.value)
    if (viewMode.value === 'week') {
      d.setDate(d.getDate() - 7)
    } else {
      d.setMonth(d.getMonth() - 1)
    }
    currentDate.value = d
  }

  function next() {
    const d = new Date(currentDate.value)
    if (viewMode.value === 'week') {
      d.setDate(d.getDate() + 7)
    } else {
      d.setMonth(d.getMonth() + 1)
    }
    currentDate.value = d
  }

  function goToday() {
    currentDate.value = new Date()
  }

  function toISODate(d) {
    return d.toISOString().slice(0, 10)
  }

  const startDateISO = computed(() => toISODate(rangeStart.value))
  const endDateISO = computed(() => toISODate(rangeEnd.value))

  return {
    viewMode,
    currentDate,
    rangeStart,
    rangeEnd,
    rangeLabel,
    startDateISO,
    endDateISO,
    prev,
    next,
    goToday,
  }
}
