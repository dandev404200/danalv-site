<script setup>
import TerminalWindow from '../components/TerminalWindow.vue'
import TimelineItem from '../components/TimelineItem.vue'

const socialLinks = [
  { name: 'github/', url: 'https://github.com' },
  { name: 'linkedin/', url: 'https://linkedin.com' },
  { name: 'substack/', url: 'https://substack.com' },
  { name: 'discord/', url: 'https://discord.com' },
]

const experiences = [
  {
    dateRange: '',
    title: 'Security Consultant',
    company: 'independent',
    description:
      'Freelance security consulting. Red team engagements, architecture reviews, and helping startups not get pwned. Building tools and writing about the stuff I find interesting.',
    isCurrent: true,
    position: 'left',
    accentColor: 'cyan',
  },
  {
    dateRange: '2021 — 2023',
    title: 'Cybersecurity Consultant',
    company: 'EY',
    description:
      'Enterprise security for big 4 clients. Learned how to translate "we found 47 critical vulns" into "here\'s why leadership should care." Pentests, risk assessments, the whole consulting playbook.',
    isCurrent: false,
    position: 'right',
    accentColor: 'cyan',
  },
  {
    dateRange: '2019 — 2021',
    title: 'Security Analyst',
    company: 'StartupCo',
    description:
      'Where it all started. Alert triage, incident response, and learning that most "attacks" are just misconfigured Jenkins servers. Built my first automated detection pipeline here.',
    isCurrent: false,
    position: 'left',
    accentColor: 'cyan',
  },
]

const projects = [
  {
    name: 'recon-automator',
    description:
      'Automated reconnaissance pipeline for bug bounty hunting. Chains subfinder, httpx, and nuclei with custom templates. Saves me hours of manual enumeration.',
    url: 'https://github.com',
  },
  {
    name: 'cve-tracker',
    description:
      'Personal CVE tracking dashboard with EPSS scoring and exploit availability checks. Filters the noise so I only see what matters for my tech stack.',
    url: 'https://github.com',
  },
]
</script>

<template>
  <main class="relative z-10 pt-20">
    <!-- About Section -->
    <section id="about" class="min-h-screen flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20">
      <div class="max-w-6xl w-full">
        <TerminalWindow title="terminal — bash" :glow="true">
          <div class="flex flex-col md:flex-row gap-12 items-center md:items-start">
            <!-- Avatar -->
            <div
              class="w-56 h-56 bg-slate-800 rounded-xl flex items-center justify-center shrink-0 border border-cyan-500/30">
              <span class="text-cyan-400 font-mono text-base">[avatar.png]</span>
            </div>

            <!-- Bio Content -->
            <div class="flex-1 text-center md:text-left">
              <p class="font-mono text-lg text-slate-500 mb-3">$ whoami</p>
              <h1 class="font-mono text-5xl md:text-6xl text-white mb-4">Daniel Alvarez</h1>
              <p class="text-cyan-400 font-mono text-2xl md:text-3xl mb-10 terminal-cursor">
                Security Engineer
              </p>

              <p class="font-mono text-lg text-slate-500 mb-3">$ cat about.txt</p>
              <p class="text-slate-400 leading-relaxed mb-10 text-lg md:text-xl">
                I break things so you don't have to. Five years in the trenches of enterprise
                security, from SOC analyst to leading pentest engagements. Now building the bridge
                between deep technical work and business strategy. I believe the best security is
                invisible—until you need it.
              </p>

              <p class="font-mono text-lg text-slate-500 mb-3">$ ls ~/links</p>
              <div class="flex gap-8 justify-center md:justify-start flex-wrap">
                <a v-for="link in socialLinks" :key="link.name" :href="link.url" target="_blank"
                  class="text-cyan-400 hover:text-white transition-colors font-mono text-lg">
                  {{ link.name }}
                </a>
              </div>
            </div>
          </div>
        </TerminalWindow>

        <!-- Tagline -->
        <div class="text-center mt-16">
          <p class="text-cyan-400 font-mono text-base">
            /* Be curious. Stay curious. Don't accept "That's just the way it is." */
          </p>
        </div>
      </div>
    </section>

    <!-- Experience Section -->
    <section id="experience" class="min-h-screen px-4 sm:px-6 lg:px-8 py-20">
      <div class="max-w-6xl mx-auto">
        <h2 class="font-mono text-3xl md:text-4xl text-white mb-16 text-center">
          <span class="text-slate-500">$ </span>
          <span class="text-cyan-400">history</span>
          <span class="text-slate-500"> --career</span>
        </h2>

        <!-- Timeline -->
        <div class="relative">
          <!-- Timeline Line -->
          <div class="absolute left-0 md:left-1/2 transform md:-translate-x-px top-0 bottom-0 w-0.5 bg-cyan-500/30">
          </div>

          <!-- Timeline Items -->
          <TimelineItem v-for="(exp, index) in experiences" :key="index" :date-range="exp.dateRange" :title="exp.title"
            :company="exp.company" :description="exp.description" :is-current="exp.isCurrent" :position="exp.position"
            :accent-color="exp.accentColor" />
        </div>
      </div>
    </section>

    <!-- Projects Section -->
    <section id="projects" class="min-h-screen px-4 sm:px-6 lg:px-8 pt-50 pb-20">
      <div class="max-w-6xl mx-auto">
        <h2 class="font-mono text-3xl md:text-4xl text-white mb-16 text-center">
          <span class="text-slate-500">$ </span>
          <span class="text-cyan-400">ls </span>
          <span class="text-slate-500">~/projects</span>
        </h2>

        <!-- Project Grid -->
        <div class="grid md:grid-cols-2 gap-8">
          <div v-for="project in projects" :key="project.name"
            class="group relative bg-slate-900/40 backdrop-blur-sm rounded-xl border border-slate-800 overflow-hidden hover:border-cyan-500/30 hover:bg-slate-800/50 transition-all duration-300 hover:shadow-[0_0_30px_-10px_rgba(6,182,212,0.15)]">
            <!-- Screenshot Placeholder -->
            <div class="h-56 bg-slate-800/50 flex items-center justify-center border-b border-slate-800">
              <span class="text-cyan-400 font-mono text-base">[screenshot.png]</span>
            </div>

            <!-- Project Info -->
            <div class="p-8">
              <h3 class="text-white font-mono text-2xl mb-4 group-hover:text-cyan-400 transition-colors">
                {{ project.name }}
              </h3>
              <p class="text-slate-400 leading-relaxed mb-6 font-mono text-base">
                {{ project.description }}
              </p>
              <a :href="project.url" target="_blank"
                class="inline-flex items-center gap-2 text-cyan-400 font-mono text-base hover:text-white transition-colors">
                git clone →
              </a>
            </div>

            <!-- Decorative Corner lines -->
            <div
              class="absolute top-0 right-0 w-8 h-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
              <div class="absolute top-0 right-0 w-[1px] h-full bg-gradient-to-b from-cyan-500/50 to-transparent"></div>
              <div class="absolute top-0 right-0 w-full h-[1px] bg-gradient-to-l from-cyan-500/50 to-transparent"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.terminal-cursor::after {
  content: '█';
  animation: blink 1s infinite;
  color: #22d3ee;
}

@keyframes blink {

  0%,
  50% {
    opacity: 1;
  }

  51%,
  100% {
    opacity: 0;
  }
}
</style>
