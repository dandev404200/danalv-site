<script setup>
import TerminalWindow from '../components/TerminalWindow.vue'
import TimelineItem from '../components/TimelineItem.vue'

const socialLinks = [
  { name: 'github/', url: 'https://github.com/dandev404200' },
  { name: 'linkedin/', url: 'https://www.linkedin.com/in/daniel-alvarez-458aa4234t4t455' },
  { name: 'substack/', url: 'https://substack.com/@dan1923487/reads' },
  { name: 'discord/', url: 'https://discord.com/users/1248082395601830030' },
]

const experiences = [
  {
    dateRange: '',
    title: 'Cybersecurity Analyst',
    company: 'TEKsystems',
    description:
      'Led AppSec assessments and built the organizations first security metrics program. Established a formal TPRM program, integrated NIST 800-53 controls into design phases, and engineered custom dashboards that cut resolution times in half.',
    isCurrent: true,
    position: 'left',
    accentColor: 'cyan',
  },
  {
    dateRange: '2021 — 2023',
    title: 'Cybersecurity Consultant',
    company: 'EY',
    description:
      'Enterprise security for Fortune 500 clients. Built TPRM programs, managed critical cyber risks in ServiceNow, led security tool evaluations, and conducted program assessments using NIST CSF and ISO 27001. Translated technical findings into strategic recommendations for CISOs and leadership.',
    isCurrent: false,
    position: 'right',
    accentColor: 'cyan',
  },
  {
    dateRange: '2020',
    title: 'Information Security Analyst',
    company: 'Artis Technologies',
    description:
      'Where it started. Container and server performance testing, AWS cost optimization, DDoS simulations, and network scanning. Learned the fundamentals by getting hands-on with real infrastructure.',
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
          <div class="w-56 h-71 rounded-xl shrink-0 border border-cyan-500/30 overflow-hidden">
            <img src="/danpicnew.png" alt="Daniel Alvarez" class="w-full h-full object-cover" />
          </div>

          <!-- Bio Content -->
          <div class="flex-1 text-center md:text-left">
            <p class="font-mono text-lg text-slate-500 mb-3">$ whoami</p>
            <h1 class="font-mono text-5xl md:text-6xl text-white mb-4">Daniel Alvarez</h1>
            <p class="text-cyan-400 font-mono text-2xl md:text-3xl mb-10 terminal-cursor">
              Security Consultant
            </p>

            <p class="font-mono text-lg text-slate-500 mb-3">$ cat about.txt</p>
            <p class="text-slate-400 leading-relaxed mb-10 text-lg md:text-xl">
              Four years of GRC program builds, AppSec assessments, TPRM strategy, and metrics at scale. Now I'm
              applying that knowledge hands-on: developing secure applications, automating controls, and using AI to
              enhance learning and bring clarity from ambiguity. Security should be a business enabler not a blocker.
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
          <div class="absolute top-0 right-0 w-8 h-8 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
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
