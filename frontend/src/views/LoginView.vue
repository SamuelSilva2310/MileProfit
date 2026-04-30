<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Coins, AlertTriangle } from 'lucide-vue-next'
import { useI18n } from '../i18n'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const mode = ref('login') // 'login' | 'register'

const email = ref('')
const password = ref('')
const name = ref('')
const error = ref('')
const loading = ref(false)

function switchMode(m) {
  mode.value = m
  error.value = ''
}

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

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await auth.register(name.value, email.value, password.value)
    router.push('/')
  } catch (e) {
    const detail = e.response?.data?.detail
    if (e.response?.status === 409) {
      error.value = t('register.emailTaken')
    } else if (Array.isArray(detail)) {
      error.value = detail[0]?.msg || 'Registration failed'
    } else {
      error.value = detail || 'Registration failed'
    }
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
        <h1 class="text-2xl font-bold text-gray-800">
          {{ mode === 'login' ? t('login.title') : t('register.title') }}
        </h1>
        <p class="text-gray-400 text-sm mt-1">
          {{ mode === 'login' ? t('login.subtitle') : t('register.subtitle') }}
        </p>
      </div>

      <!-- Login form -->
      <form v-if="mode === 'login'" @submit.prevent="handleLogin" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
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

        <p class="text-center text-sm text-gray-400">
          {{ t('login.noAccount') }}
          <button type="button" @click="switchMode('register')" class="text-blue-600 font-medium hover:underline">
            {{ t('login.signUpLink') }}
          </button>
        </p>
      </form>

      <!-- Register form -->
      <form v-else @submit.prevent="handleRegister" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
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
          <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ t('register.name') }}</label>
          <input
            v-model="name"
            type="text"
            required
            :placeholder="t('register.namePlaceholder')"
            class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ t('register.email') }}</label>
          <input
            v-model="email"
            type="email"
            required
            placeholder="your@email.com"
            class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
          />
        </div>

        <div>
          <label class="block text-xs font-medium text-gray-500 mb-1.5">{{ t('register.password') }}</label>
          <input
            v-model="password"
            type="password"
            required
            minlength="8"
            class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
          />
          <p class="text-xs text-gray-400 mt-1">{{ t('register.passwordHint') }}</p>
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
        >
          {{ loading ? t('register.signingUp') : t('register.signUp') }}
        </button>

        <p class="text-center text-sm text-gray-400">
          {{ t('register.haveAccount') }}
          <button type="button" @click="switchMode('login')" class="text-blue-600 font-medium hover:underline">
            {{ t('register.signInLink') }}
          </button>
        </p>
      </form>
    </div>
  </div>
</template>
