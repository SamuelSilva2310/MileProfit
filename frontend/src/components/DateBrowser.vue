<script setup>
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

const props = defineProps({
  rangeLabel: String,
  viewMode: String,
})

const emit = defineEmits(['prev', 'next', 'today', 'update:viewMode'])
</script>

<template>
  <div class="bg-white rounded-xl border border-gray-200 px-3 py-2.5 mb-5 shadow-sm">
    <div class="flex items-center justify-between">
      <button @click="emit('prev')" class="p-2 -ml-1 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors">
        <ChevronLeft :size="20" class="text-gray-500" />
      </button>

      <div class="flex flex-col items-center gap-1.5 min-w-0">
        <span class="text-sm font-semibold text-gray-700 truncate">{{ rangeLabel }}</span>
        <div class="flex items-center gap-2">
          <button @click="emit('today')" class="text-xs text-blue-600 font-medium hover:underline px-1">Today</button>
          <div class="flex bg-gray-100 rounded-lg p-0.5">
            <button
              @click="emit('update:viewMode', 'week')"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              :class="viewMode === 'week' ? 'bg-white shadow-sm text-gray-700' : 'text-gray-400'"
            >
              Week
            </button>
            <button
              @click="emit('update:viewMode', 'month')"
              class="px-2.5 py-1 rounded-md text-xs font-medium transition-colors"
              :class="viewMode === 'month' ? 'bg-white shadow-sm text-gray-700' : 'text-gray-400'"
            >
              Month
            </button>
          </div>
        </div>
      </div>

      <button @click="emit('next')" class="p-2 -mr-1 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors">
        <ChevronRight :size="20" class="text-gray-500" />
      </button>
    </div>
  </div>
</template>
