<template>
  <div
    class="flex items-center gap-2 px-3 py-2 rounded-lg
           bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-700"
  >
    <span class="text-sm">✅</span>
    <div class="flex-1 min-w-0">
      <div class="text-xs font-medium text-green-700 dark:text-green-300">
        {{ result.label }}
      </div>
      <div class="text-xs text-green-600 dark:text-green-400 truncate">
        {{ result.path }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  result: {
    type: Object,
    required: true
  }
})
</script>