<script setup>
import { CircleCheck, CircleX, Info } from 'lucide-vue-next'
import { useToast } from '../composables/useToast'

const { toasts } = useToast()

const iconMap = { success: CircleCheck, error: CircleX, info: Info }
const colorMap = {
  success: 'bg-emerald-600',
  error: 'bg-rose-600',
  info: 'bg-blue-600',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] flex flex-col items-center gap-2 pointer-events-none w-full max-w-sm px-4">
      <TransitionGroup
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 -translate-y-3 scale-95"
        enter-to-class="opacity-100 translate-y-0 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0 scale-100"
        leave-to-class="opacity-0 -translate-y-2 scale-95"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="pointer-events-auto w-full flex items-center gap-2.5 px-4 py-3 rounded-xl text-white text-sm font-medium shadow-lg"
          :class="colorMap[toast.type]"
        >
          <component :is="iconMap[toast.type]" :size="18" class="shrink-0" />
          <span>{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
