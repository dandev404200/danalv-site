<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { 
  Shield, 
  Terminal, 
  AlertTriangle, 
  Activity, 
  Search, 
  Filter, 
  Clock, 
  ExternalLink,
  Cpu, 
  Lock, 
  Wifi, 
  ChevronRight, 
  Database 
} from 'lucide-vue-next';

// Mock Data
const MOCK_NEWS = [
  {
    id: 1,
    title: "Critical RCE Vulnerability Discovered in Popular Framework",
    source: "Krebs on Security",
    date: "Jan 14",
    type: "VULN",
    severity: "critical",
    excerpt: "Researchers have identified a remote code execution flaw affecting millions of devices. Immediate patching is recommended."
  },
  {
    id: 2,
    title: "CISA Adds Three New Exploited Vulnerabilities to Catalog",
    source: "CISA",
    date: "Jan 14",
    type: "ADVISORY",
    severity: "high",
    excerpt: "The Cybersecurity and Infrastructure Security Agency has updated its Known Exploited Vulnerabilities Catalog."
  },
  {
    id: 3,
    title: "New Ransomware Gang Targets Healthcare Sector",
    source: "BleepingComputer",
    date: "Jan 13",
    type: "THREAT",
    severity: "critical",
    excerpt: "A sophisticated new group is leveraging double-extortion tactics against hospitals and clinics across the Midwest."
  },
  {
    id: 4,
    title: "Google Patches Zero-Day Actively Exploited in Chrome",
    source: "The Hacker News",
    date: "Jan 13",
    type: "PATCH",
    severity: "medium",
    excerpt: "Chrome users urged to update immediately to address a type confusion vulnerability in the V8 JavaScript engine."
  },
  {
    id: 5,
    title: "Understanding the Latest MITRE ATT&CK Framework Updates",
    source: "MITRE",
    date: "Jan 12",
    type: "RESEARCH",
    severity: "low",
    excerpt: "An in-depth look at the new techniques and sub-techniques added in version 14 of the framework."
  },
  {
    id: 6,
    title: "Supply Chain Attack Compromises Python Package Index",
    source: "Ars Technica",
    date: "Jan 12",
    type: "THREAT",
    severity: "high",
    excerpt: "Malicious code found in several popular PyPI libraries steals developer credentials and environment variables."
  }
];

const CATEGORIES = ["ALL", "VULN", "THREAT", "ADVISORY", "PATCH", "RESEARCH"];

// State
const activeCategory = ref("ALL");
const searchQuery = ref("");
const currentTime = ref(new Date());
let timer = null;

// Lifecycle
onMounted(() => {
  timer = setInterval(() => {
    currentTime.value = new Date();
  }, 1000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});

// Computed
const filteredNews = computed(() => {
  return MOCK_NEWS.filter(item => {
    const matchesCategory = activeCategory.value === "ALL" || item.type === activeCategory.value;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          item.source.toLowerCase().includes(searchQuery.value.toLowerCase());
    return matchesCategory && matchesSearch;
  });
});

// Format Time Helper
const formattedTime = computed(() => {
  return currentTime.value.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
});

// Styles Helper
const getBadgeStyle = (type) => {
  switch (type) {
    case 'VULN': return 'bg-red-900/40 text-red-300 border-red-700/50';
    case 'THREAT': return 'bg-orange-900/40 text-orange-300 border-orange-700/50';
    case 'PATCH': return 'bg-green-900/40 text-green-300 border-green-700/50';
    case 'ADVISORY': return 'bg-yellow-900/40 text-yellow-300 border-yellow-700/50';
    case 'RESEARCH': return 'bg-blue-900/40 text-blue-300 border-blue-700/50';
    default: return 'bg-slate-800 text-slate-300 border-slate-700';
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500/30 selection:text-cyan-200 overflow-x-hidden relative">
    
    <!-- Background Grid & ambient light -->
    <div class="fixed inset-0 pointer-events-none">
      <div class="absolute inset-0 bg-[linear-gradient(rgba(15,23,42,0.95),rgba(15,23,42,0.98)),url('https://www.transparenttextures.com/patterns/dark-matter.png')]"></div>
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>
      <div class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-500/50 to-transparent"></div>
      
      <!-- Animated Orbs -->
      <div class="absolute top-20 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
    </div>

    <!-- Top Navigation Bar -->
    <nav class="relative z-10 border-b border-slate-800/60 bg-slate-900/50 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center space-x-3 group cursor-pointer">
            <div class="p-2 bg-cyan-500/10 rounded-lg border border-cyan-500/20 group-hover:border-cyan-500/50 transition-colors">
              <Terminal class="w-6 h-6 text-cyan-400" />
            </div>
            <div>
              <span class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">
                ~ /danalv
              </span>
              <span class="text-xs block text-slate-500 font-mono tracking-wider">SECURE_SHELL_ACTIVE</span>
            </div>
          </div>
          
          <div class="hidden md:flex items-center space-x-8 text-sm font-medium font-mono text-slate-400">
            <a href="#" class="hover:text-cyan-400 transition-colors">whoami</a>
            <a href="#" class="hover:text-cyan-400 transition-colors">history</a>
            <a href="#" class="hover:text-cyan-400 transition-colors">ls projects/</a>
            <div class="px-3 py-1 bg-cyan-500/10 text-cyan-400 rounded border border-cyan-500/30 shadow-[0_0_10px_rgba(34,211,238,0.1)]">
              cat /daily
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <!-- Header Section -->
      <div class="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-2">
          <h1 class="text-4xl font-bold text-white mb-2 tracking-tight">
            Daily Intelligence Digest
          </h1>
          <p class="text-slate-400 flex items-center gap-2">
            <span class="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            System Status: Monitoring global feeds
          </p>
        </div>
        
        <!-- Status Card -->
        <div class="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-lg">
            <div class="flex flex-col">
              <span class="text-xs text-slate-500 font-mono uppercase">Last Sync</span>
              <span class="text-lg font-mono text-cyan-300">
                {{ formattedTime }}
              </span>
            </div>
            <div class="flex gap-4">
              <div class="flex flex-col items-end">
                <span class="text-xs text-slate-500 font-mono uppercase">Threat Level</span>
                <div class="flex gap-1 mt-1">
                  <div class="w-2 h-4 bg-red-500 rounded-sm"></div>
                  <div class="w-2 h-4 bg-red-500/30 rounded-sm"></div>
                  <div class="w-2 h-4 bg-red-500/30 rounded-sm"></div>
                </div>
              </div>
            </div>
        </div>
      </div>

      <!-- Controls Bar -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-slate-900/30 p-2 rounded-xl border border-slate-800/50">
        
        <!-- Category Filter -->
        <div class="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
          <button
            v-for="cat in CATEGORIES"
            :key="cat"
            @click="activeCategory = cat"
            :class="[
              'px-4 py-1.5 rounded-lg text-xs font-bold tracking-wide transition-all border',
              activeCategory === cat 
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-[0_0_15px_-3px_rgba(34,211,238,0.2)]' 
                : 'bg-transparent text-slate-500 border-transparent hover:bg-slate-800 hover:text-slate-300'
            ]"
          >
            {{ cat }}
          </button>
        </div>

        <!-- Search -->
        <div class="relative group w-full md:w-64">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search class="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
          </div>
          <input
            type="text"
            placeholder="grep search..."
            v-model="searchQuery"
            class="block w-full pl-10 pr-3 py-1.5 border border-slate-700 rounded-lg leading-5 bg-slate-900/50 text-slate-300 placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 sm:text-sm transition-all font-mono"
          />
        </div>
      </div>

      <!-- Grid Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="item in filteredNews"
          :key="item.id"
          class="group relative bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800 p-5 hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300 hover:shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)] flex flex-col"
        >
          <!-- Header of Card -->
          <div class="flex items-start justify-between mb-4">
            <span :class="['px-2 py-0.5 rounded text-[10px] font-bold tracking-wider border', getBadgeStyle(item.type)]">
              {{ item.type }}
            </span>
            <span class="text-xs font-mono text-slate-500 flex items-center gap-1">
              <Clock class="w-3 h-3" /> {{ item.date }}
            </span>
          </div>

          <!-- Title -->
          <h3 class="text-lg font-semibold text-slate-100 mb-3 leading-snug group-hover:text-cyan-400 transition-colors">
            {{ item.title }}
          </h3>

          <!-- Excerpt -->
          <p class="text-slate-400 text-sm mb-6 flex-grow line-clamp-3">
            {{ item.excerpt }}
          </p>

          <!-- Footer -->
          <div class="pt-4 border-t border-slate-800/50 flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div :class="['w-2 h-2 rounded-full', item.severity === 'critical' ? 'bg-red-500 animate-pulse' : 'bg-slate-600']"></div>
              <span class="text-xs font-mono text-slate-500 uppercase">{{ item.source }}</span>
            </div>
            <button class="text-slate-400 hover:text-cyan-400 transition-colors p-1 rounded hover:bg-cyan-500/10">
              <ExternalLink class="w-4 h-4" />
            </button>
          </div>

          <!-- Decorative Corner lines -->
          <div class="absolute top-0 right-0 w-8 h-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
            <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-cyan-500/50 to-transparent"></div>
            <div class="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-cyan-500/50 to-transparent"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredNews.length === 0" class="text-center py-20 border border-dashed border-slate-800 rounded-xl bg-slate-900/20">
        <Database class="w-12 h-12 text-slate-700 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-slate-300">No signals detected</h3>
        <p class="text-slate-500">Try adjusting your filters or search query.</p>
      </div>

      <!-- Footer Info -->
      <div class="mt-12 border-t border-slate-800/50 pt-6 flex flex-col md:flex-row justify-between items-center text-xs text-slate-500 font-mono">
          <div class="flex gap-4 mb-4 md:mb-0">
            <span>Items Loaded: <span class="text-cyan-500">{{ MOCK_NEWS.length }}</span></span>
            <span>|</span>
            <span>Latency: <span class="text-green-500">24ms</span></span>
          </div>
          <div>
            /* Feeds: Krebs, CISA, BleepingComputer, The Hacker News, Ars Technica */
          </div>
      </div>

    </main>
  </div>
</template>
