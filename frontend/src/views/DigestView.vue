<script setup>
import { ref, computed } from 'vue'
import { Clock, ExternalLink, Search, Database } from 'lucide-vue-next'

// Mock Data - replace with real RSS feed later
const MOCK_NEWS = [
  {
    id: 1,
    title: 'Critical RCE Vulnerability Discovered in Popular Framework',
    source: 'Krebs on Security',
    url: 'https://example.com/article-1',
    date: 'Jan 14',
    type: 'VULN',
    severity: 'critical',
    excerpt:
      'Researchers have identified a remote code execution flaw affecting millions of devices. Immediate patching is recommended.',
  },
  {
    id: 2,
    title: 'CISA Adds Three New Exploited Vulnerabilities to Catalog',
    source: 'CISA',
    url: 'https://example.com/article-2',
    date: 'Jan 14',
    type: 'ADVISORY',
    severity: 'high',
    excerpt:
      'The Cybersecurity and Infrastructure Security Agency has updated its Known Exploited Vulnerabilities Catalog.',
  },
  {
    id: 3,
    title: 'New Ransomware Gang Targets Healthcare Sector',
    source: 'BleepingComputer',
    url: 'https://example.com/article-3',
    date: 'Jan 13',
    type: 'THREAT',
    severity: 'critical',
    excerpt:
      'A sophisticated new group is leveraging double-extortion tactics against hospitals and clinics across the Midwest.',
  },
  {
    id: 4,
    title: 'Google Patches Zero-Day Actively Exploited in Chrome',
    source: 'The Hacker News',
    url: 'https://example.com/article-4',
    date: 'Jan 13',
    type: 'PATCH',
    severity: 'medium',
    excerpt:
      'Chrome users urged to update immediately to address a type confusion vulnerability in the V8 JavaScript engine.',
  },
  {
    id: 5,
    title: 'Understanding the Latest MITRE ATT&CK Framework Updates',
    source: 'MITRE',
    url: 'https://example.com/article-5',
    date: 'Jan 12',
    type: 'RESEARCH',
    severity: 'low',
    excerpt:
      'An in-depth look at the new techniques and sub-techniques added in version 14 of the framework.',
  },
  {
    id: 6,
    title: 'Supply Chain Attack Compromises Python Package Index',
    source: 'Ars Technica',
    url: 'https://example.com/article-6',
    date: 'Jan 12',
    type: 'THREAT',
    severity: 'high',
    excerpt:
      'Malicious code found in several popular PyPI libraries steals developer credentials and environment variables.',
  },
]

const CATEGORIES = ['ALL', 'VULN', 'THREAT', 'ADVISORY', 'PATCH', 'RESEARCH']

// State
const activeCategory = ref('ALL')
const searchQuery = ref('')

// Computed
const filteredNews = computed(() => {
  return MOCK_NEWS.filter((item) => {
    const matchesCategory = activeCategory.value === 'ALL' || item.type === activeCategory.value
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.source.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCategory && matchesSearch
  })
})

// Styles Helper
const getBadgeStyle = (type) => {
  switch (type) {
    case 'VULN':
      return 'bg-red-900/40 text-red-300 border-red-700/50'
    case 'THREAT':
      return 'bg-orange-900/40 text-orange-300 border-orange-700/50'
    case 'PATCH':
      return 'bg-green-900/40 text-green-300 border-green-700/50'
    case 'ADVISORY':
      return 'bg-yellow-900/40 text-yellow-300 border-yellow-700/50'
    case 'RESEARCH':
      return 'bg-blue-900/40 text-blue-300 border-blue-700/50'
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700'
  }
}
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

      <!-- Controls Bar -->
      <div
        class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10 bg-slate-900/30 p-3 rounded-xl border border-slate-800/50">
        <!-- Category Filter -->
        <div class="flex items-center gap-3 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
          <button v-for="cat in CATEGORIES" :key="cat" @click="activeCategory = cat" :class="[
            'px-5 py-2 rounded-lg text-sm font-bold tracking-wide transition-all border',
            activeCategory === cat
              ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_15px_-3px_rgba(34,211,238,0.2)]'
              : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-800 hover:text-slate-300',
          ]">
            {{ cat }}
          </button>
        </div>

        <!-- Search -->
        <div class="relative group w-full md:w-80">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search class="h-5 w-5 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
          </div>
          <input type="text" placeholder="grep search..." v-model="searchQuery"
            class="block w-full pl-12 pr-4 py-2.5 border border-slate-700 rounded-lg leading-5 bg-slate-900/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 text-base transition-all font-mono" />
        </div>
      </div>

      <!-- Grid Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <a v-for="item in filteredNews" :key="item.id" :href="item.url" target="_blank"
          class="group relative bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800 p-6 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300 hover:shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)] flex flex-col">
          <!-- Header of Card -->
          <div class="flex items-start justify-between mb-5">
            <span :class="[
              'px-3 py-1 rounded text-xs font-bold tracking-wider border',
              getBadgeStyle(item.type),
            ]">
              {{ item.type }}
            </span>
            <span class="text-sm font-mono text-slate-500 flex items-center gap-1.5">
              <Clock class="w-4 h-4" /> {{ item.date }}
            </span>
          </div>

          <!-- Title -->
          <h3
            class="text-xl font-semibold text-slate-100 mb-4 leading-snug group-hover:text-cyan-400 transition-colors">
            {{ item.title }}
          </h3>

          <!-- Excerpt -->
          <p class="text-slate-400 text-base mb-8 flex-grow line-clamp-3">
            {{ item.excerpt }}
          </p>

          <!-- Footer -->
          <div class="pt-5 border-t border-slate-800/50 flex items-center justify-between">
            <span class="text-sm font-mono text-slate-500 uppercase">{{ item.source }}</span>
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

      <!-- Empty State -->
      <div v-if="filteredNews.length === 0"
        class="text-center py-20 border border-dashed border-slate-800 rounded-xl bg-slate-900/20">
        <Database class="w-12 h-12 text-slate-700 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-slate-300">No signals detected</h3>
        <p class="text-slate-500">Try adjusting your filters or search query.</p>
      </div>


    </div>
  </main>
</template>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style>
