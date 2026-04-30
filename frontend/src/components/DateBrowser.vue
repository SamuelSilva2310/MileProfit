<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { useI18n } from '../i18n'

const { t } = useI18n()

const props = defineProps({
  rangeLabel: String,
  viewMode: String,
})

const emit = defineEmits(['prev', 'next', 'today', 'update:viewMode'])
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 px-3 py-2.5 mb-5 shadow-sm">
    <div class="flex items-center justify-between">
      <button @click="emit('prev')" class="p-2 -ml-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 active:bg-gray-200 transition-colors">
        <ChevronLeft :size="20" class="text-gray-500 dark:text-gray-400" />
      </button>

      <div class="flex flex-col items-center gap-1.5 min-w-0">
        <span class="text-sm font-semibold text-gray-700 dark:text-gray-200 truncate">{{ rangeLabel }}</span>
        <div class="flex items-center gap-2">
          <button @click="emit('today')" class="text-xs text-blue-600 font-medium hover:underline px-1">{{ t('dateBrowser.today') }}</button>
          <div class="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-0.5">
            <button
              @click="emit('update:viewMode', 'day')"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              :class="viewMode === 'day' ? 'bg-white dark:bg-gray-600 shadow-sm text-gray-700 dark:text-gray-100' : 'text-gray-400 dark:text-gray-500'"
            >
              {{ t('dateBrowser.day') }}
            </button>
            <button
              @click="emit('update:viewMode', 'week')"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              :class="viewMode === 'week' ? 'bg-white dark:bg-gray-600 shadow-sm text-gray-700 dark:text-gray-100' : 'text-gray-400 dark:text-gray-500'"
            >
              {{ t('dateBrowser.week') }}
            </button>
            <button
              @click="emit('update:viewMode', 'month')"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              :class="viewMode === 'month' ? 'bg-white dark:bg-gray-600 shadow-sm text-gray-700 dark:text-gray-100' : 'text-gray-400 dark:text-gray-500'"
            >
              {{ t('dateBrowser.month') }}
            </button>
          </div>
        </div>
      </div>

      <button @click="emit('next')" class="p-2 -mr-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 active:bg-gray-200 transition-colors">
        <ChevronRight :size="20" class="text-gray-500 dark:text-gray-400" />
      </button>
    </div>
  </div>
</template>
