import { ref, computed } from 'vue'
import en from './en.js'
import pt from './pt.js'

const messages = { en, pt }
const locale = ref(localStorage.getItem('locale') || 'pt')

export function useI18n() {
  function t(key) {
    const keys = key.split('.')
    let result = messages[locale.value]
    for (const k of keys) {
      result = result?.[k]
      if (result === undefined) break
    }
    if (result !== undefined) return result

    let fallback = messages.en
    for (const k of keys) {
      fallback = fallback?.[k]
      if (fallback === undefined) return key
    }
    return fallback
  }

  function setLocale(l) {
    locale.value = l
    localStorage.setItem('locale', l)
  }

  return {
    t,
    locale: computed(() => locale.value),
    setLocale,
    availableLocales: [
      { code: 'pt', label: 'Português' },
      { code: 'en', label: 'English' },
    ],
  }
}
