<script setup>
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div
    class="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500/30 selection:text-cyan-200 overflow-x-hidden relative">
    <!-- Background Grid & ambient light -->
    <div class="fixed inset-0 pointer-events-none">
      <div class="absolute inset-0 bg-[linear-gradient(rgba(15,23,42,0.95),rgba(15,23,42,0.98))]"></div>

      <!-- Top gradient line -->
      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent">
      </div>

      <!-- Bottom gradient line -->
      <div
        class="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent">
      </div>

      <!-- Animated Orbs -->
      <div class="absolute top-20 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-20 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"
        style="animation-delay: 1s;"></div>
    </div>

    <!-- Navigation -->
    <NavBar />

    <!-- Main Content -->
    <router-view />

    <!-- Footer -->
    <footer class="relative z-10 border-t border-slate-800/50 py-8 px-6 bg-transparent">
      <div class="max-w-7xl mx-auto text-center">
        <p class="text-slate-500 font-mono text-sm">EOF // 2025</p>
      </div>
    </footer>
  </div>
</template>

<style scoped></style>
