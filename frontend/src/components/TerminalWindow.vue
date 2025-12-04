<script setup>
defineProps({
  title: {
    type: String,
    default: 'terminal — bash',
  },
  glow: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div class="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-2xl overflow-hidden"
    :class="{ 'shadow-[0_0_40px_-10px_rgba(6,182,212,0.25)]': glow }">
    <!-- Title Bar -->
    <div class="bg-slate-800/80 px-6 py-4 flex items-center gap-3 border-b border-slate-700/50">
      <div class="w-4 h-4 rounded-full bg-red-500/80"></div>
      <div class="w-4 h-4 rounded-full bg-yellow-500/80"></div>
      <div class="w-4 h-4 rounded-full bg-green-500/80"></div>
      <span class="text-slate-500 font-mono text-sm ml-3">{{ title }}</span>
    </div>

    <!-- Content -->
    <div class="p-8 md:p-12">
      <slot></slot>
    </div>
  </div>
</template>
