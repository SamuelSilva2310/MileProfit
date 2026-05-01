<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { CircleCheck, Info, Plus, Trash2, Car, Sun, Moon } from 'lucide-vue-next'
import { useI18n } from '../i18n'
import { useVehicles } from '../composables/useVehicles'
import { useToast } from '../composables/useToast'
import { useDarkMode } from '../composables/useDarkMode'

const { t, locale, setLocale, availableLocales } = useI18n()
const auth = useAuthStore()
const toast = useToast()
const { vehicles, fetchVehicles, createVehicle, updateVehicle, deleteVehicle } = useVehicles()
const { isDark, toggleDark } = useDarkMode()

const name = ref('')
const taxPercent = ref(0)
const saved = ref(false)
const saving = ref(false)

const newVehicleName = ref('')
const addingVehicle = ref(false)

onMounted(() => {
  if (auth.user) {
    name.value = auth.user.name
    taxPercent.value = auth.user.tax_percent
  }
  fetchVehicles()
})

async function saveProfile() {
  saving.value = true
  try {
    await auth.updateProfile({
      name: name.value,
      tax_percent: parseFloat(taxPercent.value) || 0,
    })
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } finally {
    saving.value = false
  }
}

async function addVehicle() {
  if (!newVehicleName.value.trim()) return
  addingVehicle.value = true
  try {
    await createVehicle(newVehicleName.value.trim())
    newVehicleName.value = ''
    toast.success(t('vehicles.added'))
  } catch {
    toast.error(t('vehicles.saveFailed'))
  } finally {
    addingVehicle.value = false
  }
}

async function setPrimary(id) {
  try {
    await updateVehicle(id, { is_primary: true })
  } catch {
    toast.error(t('vehicles.saveFailed'))
  }
}

async function removeVehicle(id) {
  if (!confirm(t('vehicles.deleted') + '?')) return
  try {
    await deleteVehicle(id)
    toast.success(t('vehicles.deleted'))
  } catch {
    toast.error(t('vehicles.deleteFailed'))
  }
}
</script>

<template>
  <div class="p-4 lg:p-8 max-w-lg mx-auto space-y-6">
    <h2 class="text-xl lg:text-2xl font-bold text-gray-800 dark:text-gray-100">{{ t('profile.title') }}</h2>

    <!-- Profile form -->
    <form @submit.prevent="saveProfile" class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-5">
      <!-- Avatar -->
      <div class="flex items-center gap-4 pb-4 border-b border-gray-100 dark:border-gray-700">
        <div class="w-14 h-14 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center text-xl font-bold">
          {{ auth.user?.name?.charAt(0) || '?' }}
        </div>
        <div>
          <p class="font-semibold text-gray-800 dark:text-gray-100">{{ auth.user?.name }}</p>
          <p class="text-sm text-gray-400 dark:text-gray-500">{{ auth.user?.email }}</p>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('profile.name') }}</label>
        <input v-model="name" type="text" required class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
      </div>

      <div>
        <div class="flex items-center gap-1 mb-1.5">
          <label class="text-xs font-medium text-gray-500 dark:text-gray-400">{{ t('profile.taxRate') }}</label>
          <span class="group relative cursor-help">
            <Info :size="13" class="text-gray-300 dark:text-gray-600" />
            <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-800 text-white text-[10px] rounded-lg px-2.5 py-1.5 whitespace-nowrap z-10">
              {{ t('profile.taxRateTooltip') }}
            </span>
          </span>
        </div>
        <input v-model="taxPercent" type="number" step="0.1" min="0" max="100" class="w-full rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-1.5">{{ t('profile.taxRateDescription') }}</p>
      </div>

      <!-- Language -->
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('profile.language') }}</label>
        <div class="flex gap-2">
          <button
            v-for="l in availableLocales"
            :key="l.code"
            type="button"
            @click="setLocale(l.code)"
            class="flex-1 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all"
            :class="locale === l.code
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 ring-2 ring-blue-200 dark:ring-blue-800'
              : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-500'"
          >
            {{ l.label }}
          </button>
        </div>
      </div>

      <!-- Appearance -->
      <div>
        <label class="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">{{ t('profile.appearance') }}</label>
        <button
          type="button"
          @click="toggleDark"
          class="flex items-center justify-between w-full px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 transition-colors"
        >
          <div class="flex items-center gap-2">
            <component :is="isDark ? Moon : Sun" :size="16" class="text-gray-500 dark:text-gray-400" />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200">{{ t('profile.darkMode') }}</span>
          </div>
          <div class="relative">
            <div class="w-12 h-7 rounded-full transition-colors" :class="isDark ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'"></div>
            <div class="absolute top-1 left-1 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="isDark ? 'translate-x-5' : ''"></div>
          </div>
        </button>
      </div>

      <button type="submit" :disabled="saving" class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm">
        {{ saving ? t('profile.saving') : t('profile.save') }}
      </button>

      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="saved" class="flex items-center justify-center gap-1.5 text-sm text-emerald-600 bg-emerald-50 rounded-xl py-2.5">
          <CircleCheck :size="16" />
          {{ t('profile.updated') }}
        </div>
      </Transition>
    </form>

    <!-- Vehicles section -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div class="flex items-center gap-2 mb-4">
        <Car :size="18" class="text-gray-500 dark:text-gray-400" />
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{{ t('vehicles.title') }}</h3>
      </div>

      <div v-if="vehicles.length === 0" class="text-sm text-gray-400 dark:text-gray-500 mb-4">{{ t('vehicles.empty') }}</div>

      <div v-else class="space-y-2 mb-4">
        <div v-for="v in vehicles" :key="v.id" class="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded-xl px-4 py-3">
          <div class="flex items-center gap-2 min-w-0">
            <Car :size="16" :class="v.is_primary ? 'text-blue-500' : 'text-gray-400 dark:text-gray-500'" />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-200 truncate">{{ v.name }}</span>
            <span v-if="v.is_primary" class="text-xs text-blue-600 bg-blue-50 dark:bg-blue-900/40 border border-blue-100 dark:border-blue-800 rounded px-1.5 py-0.5 shrink-0">{{ t('vehicles.primary') }}</span>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <button
              v-if="!v.is_primary"
              @click="setPrimary(v.id)"
              class="text-xs text-gray-400 hover:text-blue-600 px-2 py-1 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/40 transition-colors"
            >{{ t('vehicles.setPrimary') }}</button>
            <button @click="removeVehicle(v.id)" class="p-1.5 rounded-lg text-gray-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 transition-colors">
              <Trash2 :size="14" />
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <input
          v-model="newVehicleName"
          type="text"
          :placeholder="t('vehicles.namePlaceholder')"
          @keydown.enter.prevent="addVehicle"
          class="flex-1 rounded-xl border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow"
        />
        <button
          @click="addVehicle"
          :disabled="addingVehicle || !newVehicleName.trim()"
          class="inline-flex items-center gap-1 bg-blue-600 text-white text-sm font-medium px-4 py-2.5 rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          <Plus :size="16" />
          {{ t('vehicles.add') }}
        </button>
      </div>
    </div>
  </div>
</template>
