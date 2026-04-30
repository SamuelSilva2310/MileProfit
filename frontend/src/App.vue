<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter, useRoute } from 'vue-router'
import { LayoutDashboard, MapPinned, Coins, Receipt, UserRound, LogOut } from 'lucide-vue-next'
import ToastContainer from './components/ToastContainer.vue'
import { useI18n } from './i18n'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

function logout() {
  auth.logout()
  router.push('/login')
}

const navItems = [
  { path: '/', labelKey: 'nav.dashboard', icon: LayoutDashboard },
  { path: '/activities', labelKey: 'nav.activity', icon: MapPinned },
  { path: '/earnings', labelKey: 'nav.earnings', icon: Coins },
  { path: '/expenses', labelKey: 'nav.expenses', icon: Receipt },
  { path: '/profile', labelKey: 'nav.profile', icon: UserRound },
]
</script>

<template>
  <ToastContainer />
  <div v-if="!auth.isAuthenticated">
    <router-view />
  </div>

  <div v-else class="min-h-screen bg-gray-50 dark:bg-gray-900 lg:flex">
    <!-- Desktop Sidebar -->
    <aside class="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <div class="px-6 py-5 border-b border-gray-100 dark:border-gray-700">
        <h1 class="text-xl font-bold text-gray-800 dark:text-gray-100 tracking-tight">{{ t('app.title') }}</h1>
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ t('app.subtitle') }}</p>
      </div>

      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150"
          :class="route.path === item.path
            ? 'bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400'
            : 'text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-700 dark:hover:text-gray-200'"
        >
          <component :is="item.icon" :size="20" :stroke-width="1.5" class="shrink-0" />
          {{ t(item.labelKey) }}
        </router-link>
      </nav>

      <div class="p-4 border-t border-gray-100 dark:border-gray-700">
        <div class="flex items-center gap-3 mb-3 px-2">
          <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-sm font-bold">
            {{ auth.user?.name?.charAt(0) || '?' }}
          </div>
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-200 truncate">{{ auth.user?.name }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ auth.user?.email }}</p>
          </div>
        </div>
        <button
          @click="logout"
          class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-600 transition-colors"
        >
          <LogOut :size="16" />
          {{ t('nav.signOut') }}
        </button>
      </div>
    </aside>

    <!-- Mobile Header -->
    <header class="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3 flex items-center justify-between sticky top-0 z-40">
      <h1 class="text-lg font-bold text-gray-800 dark:text-gray-100">{{ t('app.title') }}</h1>
      <button @click="logout" class="text-sm text-gray-500 dark:text-gray-400 hover:text-red-500 transition-colors flex items-center gap-1">
        <LogOut :size="16" />
        {{ t('nav.logout') }}
      </button>
    </header>

    <!-- Main Content -->
    <main class="flex-1 lg:ml-64 pb-20 lg:pb-0">
      <router-view />
    </main>

    <!-- Mobile Bottom Nav -->
    <nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 flex justify-around py-1.5 z-50 safe-area-bottom">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex flex-col items-center px-2 py-1 text-[10px] transition-colors min-w-[56px]"
        :class="route.path === item.path ? 'text-blue-600' : 'text-gray-400 dark:text-gray-500'"
      >
        <component :is="item.icon" :size="22" :stroke-width="route.path === item.path ? 2 : 1.5" class="mb-0.5" />
        <span :class="route.path === item.path ? 'font-semibold' : ''">{{ t(item.labelKey) }}</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
.safe-area-bottom {
  padding-bottom: max(0.375rem, env(safe-area-inset-bottom));
}
</style>
