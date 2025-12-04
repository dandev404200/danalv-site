<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { computed } from 'vue'

const mobileMenuOpen = ref(false)
const route = useRoute()

const isDigestPage = computed(() => route.path === '/digest')

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const navLinks = [
  { name: 'whoami', href: '/#about', hash: '#about' },
  { name: 'history', href: '/#experience', hash: '#experience' },
  { name: 'ls projects/', href: '/#projects', hash: '#projects' },
]
</script>

<template>
  <nav class="fixed top-0 left-0 right-0 z-50 border-b border-slate-800/60 bg-slate-900/50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
      <div class="flex items-center justify-between h-20">
        <!-- Logo -->
        <RouterLink to="/" class="flex items-center space-x-2 group cursor-pointer" @click="closeMobileMenu">
          <span class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-300 to-blue-400">
            ~/danalv
          </span>
        </RouterLink>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-10 text-base font-medium font-mono text-slate-400">
          <a v-for="link in navLinks" :key="link.name" :href="link.href" class="hover:text-cyan-400 transition-colors">
            {{ link.name }}
          </a>
          <RouterLink to="/digest"
            class="px-4 py-2 rounded border transition-all bg-cyan-500/10 text-cyan-400 border-cyan-500/30 shadow-[0_0_10px_rgba(34,211,238,0.1)] hover:border-cyan-500/50 hover:bg-cyan-500/20">
            cat /daily
          </RouterLink>
        </div>

        <!-- Mobile Hamburger Button -->
        <button class="md:hidden flex flex-col gap-1.5 p-2" @click="toggleMobileMenu" aria-label="Toggle menu">
          <span class="w-6 h-0.5 bg-cyan-400 transition-all duration-300"
            :class="{ 'rotate-45 translate-y-2': mobileMenuOpen }"></span>
          <span class="w-6 h-0.5 bg-cyan-400 transition-all duration-300"
            :class="{ 'opacity-0': mobileMenuOpen }"></span>
          <span class="w-6 h-0.5 bg-cyan-400 transition-all duration-300"
            :class="{ '-rotate-45 -translate-y-2': mobileMenuOpen }"></span>
        </button>
      </div>
    </div>

    <!-- Mobile Menu -->
    <Transition enter-active-class="transition-all duration-300 ease-out" enter-from-class="opacity-0 -translate-y-4"
      enter-to-class="opacity-100 translate-y-0" leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-4">
      <div v-if="mobileMenuOpen"
        class="md:hidden bg-slate-900/95 backdrop-blur-md border-b border-slate-800/60 px-4 py-4">
        <div class="flex flex-col gap-4">
          <a v-for="link in navLinks" :key="link.name" :href="link.href"
            class="text-slate-400 hover:text-cyan-400 transition-colors font-mono text-base py-2"
            @click="closeMobileMenu">
            {{ link.name }}
          </a>
          <RouterLink to="/digest" :class="[
            'font-mono text-base px-4 py-3 rounded border text-center transition-all',
            isDigestPage
              ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50'
              : 'text-cyan-400 border-cyan-500/30 hover:bg-cyan-500/10'
          ]" @click="closeMobileMenu">
            cat /daily
          </RouterLink>
        </div>
      </div>
    </Transition>
  </nav>
</template>
