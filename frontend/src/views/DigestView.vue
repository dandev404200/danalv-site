<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Clock, ExternalLink, Database, Loader2 } from 'lucide-vue-next'

// API base URL - empty string for same-origin (production)
// Override with VITE_API_BASE for local development with separate backend
const API_BASE = import.meta.env.VITE_API_BASE ?? ''
const LIMIT = 6
const MAX_CARDS = 42

// State
const entries = ref([])
const offset = ref(0)
const loading = ref(false)
const hasMore = ref(true)
const error = ref(null)

// Fetch digest entries from API
async function fetchEntries() {
  if (loading.value || !hasMore.value) return
  if (entries.value.length >= MAX_CARDS) {
    hasMore.value = false
    return
  }

  loading.value = true
  error.value = null

  try {
    const response = await fetch(`${API_BASE}/api/digest?offset=${offset.value}&limit=${LIMIT}`)
    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`)
    }
    const data = await response.json()

    if (data.length === 0) {
      hasMore.value = false
    } else {
      entries.value = [...entries.value, ...data]
      offset.value += data.length

      // Check if we've reached max cards
      if (entries.value.length >= MAX_CARDS) {
        hasMore.value = false
      }
    }
  } catch (e) {
    error.value = e.message
    console.error('Failed to fetch digest entries:', e)
  } finally {
    loading.value = false
  }
}

// Format date for display
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Infinite scroll handler
function handleScroll() {
  const scrollHeight = document.documentElement.scrollHeight
  const scrollTop = document.documentElement.scrollTop
  const clientHeight = document.documentElement.clientHeight

  // Load more when user is within 200px of bottom
  if (scrollTop + clientHeight >= scrollHeight - 200) {
    fetchEntries()
  }
}

// Lifecycle
onMounted(() => {
  fetchEntries()
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<template>
<main class="relative z-10 pt-20 min-h-screen">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header Section -->
    <div class="mb-8">
      <h1 class="text-4xl md:text-5xl font-bold text-white mb-3 tracking-tight">Daily Intelligence Digest</h1>
      <p class="text-slate-400 text-lg flex items-center gap-2">
        <span class="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
        System Status: Monitoring global feeds
      </p>
    </div>

    <!-- Grid Content -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <a v-for="item in entries" :key="item.link" :href="item.link" target="_blank"
        class="group relative bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800 p-6 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300 hover:shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)] flex flex-col">
        <!-- Header of Card -->
        <div class="flex items-center justify-end mb-5">
          <span class="text-sm font-mono text-slate-500 flex items-center gap-1.5 leading-none">
            <Clock class="w-4 h-4 shrink-0" /> <span class="leading-none pt-1">{{ formatDate(item.published_at)
            }}</span>
          </span>
        </div>

        <!-- Title -->
        <h3
          class="text-xl font-semibold text-slate-100 mb-4 leading-snug group-hover:text-cyan-400 transition-colors flex-grow">
          {{ item.title }}
        </h3>

        <!-- Footer -->
        <div class="pt-5 border-t border-slate-800/50 flex items-center justify-between">
          <span class="text-sm font-mono text-white uppercase font-bold">{{ item.source }}</span>
          <div class="text-slate-400 group-hover:text-cyan-400 transition-colors p-1.5 rounded hover:bg-cyan-500/10">
            <ExternalLink class="w-5 h-5" />
          </div>
        </div>

        <!-- Decorative Corner lines -->
        <div class="absolute top-0 right-0 w-8 h-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-cyan-500/50 to-transparent"></div>
          <div class="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-cyan-500/50 to-transparent"></div>
        </div>
      </a>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <Loader2 class="w-8 h-8 text-cyan-500 animate-spin" />
    </div>

    <!-- Error State -->
    <div v-if="error" class="text-center py-12">
      <p class="text-red-400">Error: {{ error }}</p>
      <button @click="fetchEntries"
        class="mt-4 px-4 py-2 bg-cyan-500/20 text-cyan-300 rounded-lg hover:bg-cyan-500/30 transition-colors">
        Retry
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && entries.length === 0"
      class="text-center py-20 border border-dashed border-slate-800 rounded-xl bg-slate-900/20">
      <Database class="w-12 h-12 text-slate-700 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-slate-300">No signals detected</h3>
      <p class="text-slate-500">No items available at this time.</p>
    </div>


  </div>
</main>
</template>
