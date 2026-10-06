<template>
  <div class="flex h-screen overflow-hidden font-sans bg-finbase text-gray-300">

    <!-- ═══════════════ SIDEBAR ═══════════════ -->
    <aside class="w-64 shrink-0 border-r border-finborder bg-fincard flex flex-col">
      <!-- Logo -->
      <div class="h-16 flex items-center gap-3 px-6 border-b border-finborder">
        <div class="w-8 h-8 rounded-lg bg-finblue flex items-center justify-center font-bold text-white text-sm shadow-glow-blue">
          Q
        </div>
        <div>
          <p class="text-white font-bold text-sm tracking-widest">PRABONOMICS</p>
          <p class="text-gray-500 text-[10px] uppercase tracking-wider">Trading Intelligence</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-6 px-3 space-y-1">
        <router-link
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm"
          :class="$route.path === '/'
            ? 'bg-finblue/10 text-finblue border border-finblue/20 font-medium'
            : 'text-gray-400 hover:bg-finborder/50 hover:text-white'"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          Overview
        </router-link>

        <router-link
          to="/macro-sensors"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm"
          :class="$route.path === '/macro-sensors'
            ? 'bg-finblue/10 text-finblue border border-finblue/20 font-medium'
            : 'text-gray-400 hover:bg-finborder/50 hover:text-white'"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/>
          </svg>
          Macro Sensors
        </router-link>

        <router-link
          to="/sector-rotation"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm"
          :class="$route.path === '/sector-rotation'
            ? 'bg-finblue/10 text-finblue border border-finblue/20 font-medium'
            : 'text-gray-400 hover:bg-finborder/50 hover:text-white'"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
          </svg>
          Sector Rotation
        </router-link>

        <router-link
          to="/stock-signals"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm"
          :class="$route.path === '/stock-signals'
            ? 'bg-finblue/10 text-finblue border border-finblue/20 font-medium'
            : 'text-gray-400 hover:bg-finborder/50 hover:text-white'"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
          Stock Signals
        </router-link>

        <router-link
          to="/heatmap"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm"
          :class="$route.path === '/heatmap'
            ? 'bg-finblue/10 text-finblue border border-finblue/20 font-medium'
            : 'text-gray-400 hover:bg-finborder/50 hover:text-white'"
        >
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z"/>
          </svg>
          Heatmap
        </router-link>
      </nav>

      <!-- API Limit Indicator -->
      <div class="p-4 mx-3 mb-4 rounded-xl bg-finbase border border-finborder">
        <div class="flex justify-between text-xs mb-2">
          <span class="text-gray-400">Token Budget</span>
          <span
            class="font-mono font-bold"
            :class="{
              'text-fingreen': tokenAlertLevel === 'ok',
              'text-finyellow': tokenAlertLevel === 'warning',
              'text-finred': tokenAlertLevel === 'critical'
            }"
          >
            {{ tokenUsed }} / {{ tokenBudget }}
          </span>
        </div>
        <div class="w-full bg-finborder rounded-full h-1.5">
          <div
            class="h-1.5 rounded-full transition-all duration-500"
            :class="{
              'bg-fingreen': tokenPercentage < 80,
              'bg-finyellow': tokenPercentage >= 80 && tokenPercentage < 90,
              'bg-finred': tokenPercentage >= 90
            }"
            :style="{ width: tokenPercentage + '%' }"
          ></div>
        </div>
        <p class="text-[10px] text-gray-600 mt-2">
          {{ tokenRemaining }} tokens remaining
        </p>
      </div>
    </aside>

    <!-- ═══════════════ MAIN CONTENT ═══════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Topbar -->
      <header class="h-16 shrink-0 border-b border-finborder bg-fincard flex items-center justify-between px-8">
        <div class="flex items-center gap-3">
          <h1 class="text-white font-semibold text-lg">{{ pageTitle }}</h1>
          <span
            v-if="macroStatus"
            class="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider border"
            :class="macroStatus === 'RISK ON'
              ? 'bg-fingreen/15 text-fingreen border-fingreen/30 shadow-glow-green'
              : 'bg-finred/15 text-finred border-finred/30 shadow-glow-red'"
          >
            {{ macroStatus }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span v-if="lastUpdated" class="font-mono text-xs">
            {{ formatTimestamp(lastUpdated) }}
          </span>
          <!-- Live dot / Demo mode indicator -->
          <div class="flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-finblue opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-finblue"></span>
            </span>
            <span class="text-xs" :class="demoMode ? 'text-finyellow' : 'text-finblue'">
              {{ demoMode ? 'Demo Mode' : 'Live' }}
            </span>
          </div>
        </div>
      </header>

      <!-- Scrollable Content Area (router-view) -->
      <div class="flex-1 overflow-y-auto">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useMarketStore } from '../stores/marketStore'

const route = useRoute()
const marketStore = useMarketStore()

// Computed properties
const pageTitle = computed(() => route.meta.title || 'Dashboard')
const macroStatus = computed(() => marketStore.macroData?.status || null)
const lastUpdated = computed(() => marketStore.lastUpdated)
const demoMode = computed(() => marketStore.demoMode)

// Token usage
const tokenUsed = computed(() => marketStore.tokenUsage?.total_used || 0)
const tokenBudget = computed(() => marketStore.tokenUsage?.budget || 500)
const tokenRemaining = computed(() => marketStore.tokenUsage?.remaining || 500)
const tokenPercentage = computed(() => marketStore.tokenPercentage)
const tokenAlertLevel = computed(() => marketStore.tokenAlertLevel)

// Format timestamp
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Load initial data
onMounted(() => {
  // Fetch token usage on mount
  marketStore.fetchTokenUsage()
})
</script>
