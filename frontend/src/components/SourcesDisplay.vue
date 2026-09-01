<template>
  <div class="border-t border-gray-100 dark:border-gray-700 pt-2">
    <div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
      📚 来源
    </div>
    <div class="flex flex-wrap gap-2">
      <span
        v-for="(source, idx) in sources"
        :key="idx"
        class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs
               bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300
               border border-gray-200 dark:border-gray-600"
      >
        <span class="truncate max-w-[150px]">{{ source.source }}</span>
        <span v-if="source.page" class="text-gray-400">第{{ source.page }}页</span>
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sources: {
    type: Array,
    default: () => []
  }
})
</script>