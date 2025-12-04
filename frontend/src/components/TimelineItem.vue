<script setup>
defineProps({
  dateRange: {
    type: String,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  company: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  isCurrent: {
    type: Boolean,
    default: false,
  },
  position: {
    type: String,
    default: 'left',
    validator: (value) => ['left', 'right'].includes(value),
  },
  accentColor: {
    type: String,
    default: 'cyan',
    validator: (value) => ['cyan', 'slate'].includes(value),
  },
})
</script>

<template>
  <div class="relative mb-12 last:mb-0">
    <div :class="[
      'md:w-1/2',
      position === 'left' ? 'md:pr-12' : 'md:ml-auto md:pl-12',
    ]">
      <!-- Timeline Dot -->
      <div
        class="absolute w-4 h-4 rounded-full border-4 border-slate-950 left-0 md:left-1/2 transform -translate-x-1/2 top-6"
        :class="{
          'bg-cyan-400': accentColor === 'cyan',
          'bg-slate-600': accentColor === 'slate',
        }"></div>

      <!-- Content Card -->
      <div
        class="group relative bg-slate-900/40 backdrop-blur-sm border border-slate-800 rounded-xl p-8 ml-8 md:ml-0 transition-all duration-300 hover:bg-slate-800/50"
        :class="{
          'hover:border-cyan-500/30 hover:shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)]': accentColor === 'cyan',
          'hover:border-slate-700': accentColor === 'slate',
        }">
        <!-- Date Range -->
        <span class="font-mono text-base" :class="{
          'text-cyan-400': accentColor === 'cyan',
          'text-slate-500': accentColor === 'slate',
        }">
          {{ isCurrent ? '[current]' : dateRange }}
        </span>

        <!-- Title -->
        <h3 class="text-white font-mono text-2xl mt-3 group-hover:text-cyan-400 group-hover:transition-colors">
          {{ title }}
        </h3>

        <!-- Company -->
        <p class="font-mono text-base mt-2" :class="{
          'text-cyan-400': accentColor === 'cyan',
          'text-slate-500': accentColor === 'slate',
        }">
          @{{ company }}
        </p>

        <!-- Description -->
        <p class="text-slate-400 mt-6 leading-relaxed font-mono text-base">
          {{ description }}
        </p>

        <!-- Decorative Corner lines -->
        <div class="absolute top-0 right-0 w-8 h-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-cyan-500/50 to-transparent"></div>
          <div class="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-cyan-500/50 to-transparent"></div>
        </div>
      </div>
    </div>
  </div>
</template>
