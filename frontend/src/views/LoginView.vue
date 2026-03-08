<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Coins, AlertTriangle } from 'lucide-vue-next'
import { useI18n } from '../i18n'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 px-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
          <Coins :size="32" class="text-white" :stroke-width="1.5" />
        </div>
        <h1 class="text-2xl font-bold text-gray-800">{{ t('login.title') }}</h1>
        <p class="text-gray-400 text-sm mt-1">{{ t('login.subtitle') }}</p>
      </div>

      <form @submit.prevent="handleLogin" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
        <Transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
        >
          <div v-if="error" class="bg-rose-50 text-rose-600 text-sm rounded-xl px-4 py-3 flex items-center gap-2">
            <AlertTriangle :size="16" class="shrink-0" />
            {{ error }}
          </div>
        </Transition>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ t('login.email') }}</label>
          <input
            v-model="email"
            type="email"
            required
            class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ t('login.password') }}</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
        >
          {{ loading ? t('login.signingIn') : t('login.signIn') }}
        </button>
      </form>
    </div>
  </div>
</template>
