<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { CircleCheck, Info } from 'lucide-vue-next'

const auth = useAuthStore()
const name = ref('')
const vehicleName = ref('')
const taxPercent = ref(0)
const saved = ref(false)
const saving = ref(false)

onMounted(() => {
  if (auth.user) {
    name.value = auth.user.name
    vehicleName.value = auth.user.vehicle_name || ''
    taxPercent.value = auth.user.tax_percent
  }
})

async function saveProfile() {
  saving.value = true
  try {
    await auth.updateProfile({
      name: name.value,
      vehicle_name: vehicleName.value || null,
      tax_percent: parseFloat(taxPercent.value) || 0,
    })
    saved.value = true
    setTimeout(() => (saved.value = false), 2500)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="p-4 lg:p-8 max-w-lg mx-auto">
    <h2 class="text-xl lg:text-2xl font-bold text-gray-800 mb-6">Profile</h2>

    <form @submit.prevent="saveProfile" class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-5">
      <!-- Avatar -->
      <div class="flex items-center gap-4 pb-4 border-b border-gray-100">
        <div class="w-14 h-14 rounded-2xl bg-blue-100 text-blue-700 flex items-center justify-center text-xl font-bold">
          {{ auth.user?.name?.charAt(0) || '?' }}
        </div>
        <div>
          <p class="font-semibold text-gray-800">{{ auth.user?.name }}</p>
          <p class="text-sm text-gray-400">{{ auth.user?.email }}</p>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1.5">Name</label>
        <input v-model="name" type="text" required class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
      </div>

      <div>
        <label class="block text-xs font-medium text-gray-500 mb-1.5">Vehicle</label>
        <input v-model="vehicleName" type="text" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" placeholder="e.g. Tesla Model 3" />
      </div>

      <div>
        <div class="flex items-center gap-1 mb-1.5">
          <label class="text-xs font-medium text-gray-500">Tax Rate (%)</label>
          <span class="group relative cursor-help">
            <Info :size="13" class="text-gray-300" />
            <span class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block bg-gray-800 text-white text-[10px] rounded-lg px-2.5 py-1.5 whitespace-nowrap z-10">
              Applied to total earnings to estimate IRS tax liability
            </span>
          </span>
        </div>
        <input v-model="taxPercent" type="number" step="0.1" min="0" max="100" class="w-full rounded-xl border border-gray-300 px-4 py-3 text-base outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow" />
        <p class="text-xs text-gray-400 mt-1.5">Used to estimate IRS tax on the dashboard. Your net profit already shows earnings minus expenses; this adds a separate "Profit After Tax" estimate.</p>
      </div>

      <button
        type="submit"
        :disabled="saving"
        class="w-full bg-blue-600 text-white rounded-xl py-3 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
      >
        {{ saving ? 'Saving...' : 'Save Changes' }}
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
          Profile updated successfully
        </div>
      </Transition>
    </form>
  </div>
</template>
