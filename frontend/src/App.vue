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
          <p class="text-white font-bold text-sm tracking-widest">QUANT.AI</p>
          <p class="text-gray-500 text-[10px] uppercase tracking-wider">Trading Intelligence</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-6 px-3 space-y-1">
        <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-finblue/10 text-finblue border border-finblue/20 font-medium text-sm">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
          Overview
        </a>
        <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-finborder/50 hover:text-white transition-colors text-sm">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
          Macro Sensors
        </a>
        <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-finborder/50 hover:text-white transition-colors text-sm">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
          Sector Rotation
        </a>
        <a href="#" class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-400 hover:bg-finborder/50 hover:text-white transition-colors text-sm">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          Stock Signals
        </a>
      </nav>

      <!-- API Limit Indicator -->
      <div class="p-4 mx-3 mb-4 rounded-xl bg-finbase border border-finborder">
        <div class="flex justify-between text-xs mb-2">
          <span class="text-gray-400">API Quota Used</span>
          <span class="text-finyellow font-mono font-bold">80 / 1000</span>
        </div>
        <div class="w-full bg-finborder rounded-full h-1.5">
          <div class="bg-finyellow h-1.5 rounded-full" style="width: 8%"></div>
        </div>
        <p class="text-[10px] text-gray-600 mt-2">920 requests remaining</p>
      </div>
    </aside>

    <!-- ═══════════════ MAIN CONTENT ═══════════════ -->
    <div class="flex-1 flex flex-col overflow-hidden">

      <!-- Topbar -->
      <header class="h-16 shrink-0 border-b border-finborder bg-fincard flex items-center justify-between px-8">
        <div class="flex items-center gap-3">
          <h1 class="text-white font-semibold text-lg">Dashboard Overview</h1>
          <span
            class="text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider border"
            :class="data.macro_status === 'RISK ON'
              ? 'bg-fingreen/15 text-fingreen border-fingreen/30 shadow-glow-green'
              : 'bg-finred/15 text-finred border-finred/30 shadow-glow-red'"
          >
            {{ data.macro_status }}
          </span>
        </div>

        <div class="flex items-center gap-4 text-sm text-gray-500">
          <span class="font-mono text-xs">{{ data.timestamp }}</span>
          <!-- Live dot -->
          <div class="flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-fingreen opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-fingreen"></span>
            </span>
            <span class="text-xs text-fingreen">Mock Mode</span>
          </div>
        </div>
      </header>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">

        <!-- ── ROW 1: Macro Metric Cards ── -->
        <section>
          <h2 class="text-xs text-gray-500 uppercase tracking-widest mb-3 font-medium">Macro Sensors — Phase 1</h2>
          <div class="grid grid-cols-3 lg:grid-cols-6 gap-3">
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Yield Rate</p>
              <p class="font-mono font-bold text-xl text-white">{{ data.macro_details.yield_rate }}%</p>
              <p class="text-[10px] text-finred mt-1">↑ Hawkish</p>
            </div>
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Oil (USD)</p>
              <p class="font-mono font-bold text-xl text-finyellow">${{ data.macro_details.oil }}</p>
              <p class="text-[10px] text-fingreen mt-1">↑ Bullish</p>
            </div>
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Gold (USD)</p>
              <p class="font-mono font-bold text-xl text-finyellow">${{ data.macro_details.gold }}</p>
              <p class="text-[10px] text-fingreen mt-1">↑ ATH</p>
            </div>
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">USD/IDR</p>
              <p class="font-mono font-bold text-xl text-white">{{ data.macro_details.usd.toLocaleString() }}</p>
              <p class="text-[10px] text-fingreen mt-1">↓ Weakening</p>
            </div>
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">BTC</p>
              <p class="font-mono font-bold text-xl text-finyellow">${{ (data.macro_details.btc / 1000).toFixed(1) }}K</p>
              <p class="text-[10px] text-fingreen mt-1">↑ Risk On</p>
            </div>
            <div class="metric-card text-center">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Copper</p>
              <p class="font-mono font-bold text-xl text-white">${{ data.macro_details.copper }}</p>
              <p class="text-[10px] text-gray-500 mt-1">→ Neutral</p>
            </div>
          </div>
        </section>

        <!-- ── ROW 2: AI Insight + Top Sector + Signals Table ── -->
        <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <!-- AI Insight Panel -->
          <div class="lg:col-span-1 bg-fincard border border-finborder rounded-xl flex flex-col overflow-hidden">
            <div class="px-5 py-4 border-b border-finborder flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
              <h3 class="text-white font-semibold text-sm">Gemini AI Analyst</h3>
            </div>
            <div class="p-5 flex-1 space-y-4">
              <!-- Macro Reasoning -->
              <div>
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Macro Reasoning</p>
                <p class="text-sm text-gray-300 leading-relaxed italic">"{{ data.macro_reasoning }}"</p>
              </div>
              <!-- Divider -->
              <div class="border-t border-finborder"></div>
              <!-- AI Insight -->
              <div>
                <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Sector Narrative</p>
                <p class="text-sm text-gray-300 leading-relaxed">{{ data.ai_insight }}</p>
              </div>
            </div>
            <!-- Top Sector Badge -->
            <div class="px-5 py-4 border-t border-finborder bg-finbase/50 flex items-center justify-between">
              <div>
                <p class="text-[10px] text-gray-500 uppercase tracking-wider">Top Sector — Phase 2</p>
                <p class="text-white font-bold font-mono text-lg tracking-widest mt-0.5">{{ data.top_sector }}</p>
              </div>
              <div class="w-10 h-10 rounded-xl bg-finyellow/10 border border-finyellow/30 flex items-center justify-center">
                <svg class="w-5 h-5 text-finyellow" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
              </div>
            </div>
          </div>

          <!-- Signals Table -->
          <div class="lg:col-span-2 bg-fincard border border-finborder rounded-xl flex flex-col overflow-hidden">
            <div class="px-5 py-4 border-b border-finborder flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-fingreen shadow-glow-green"></div>
                <h3 class="text-white font-semibold text-sm">Execution Signals — Phase 4</h3>
              </div>
              <span class="text-xs text-gray-500 font-mono">{{ data.signals.length }} assets</span>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead>
                  <tr class="border-b border-finborder text-left">
                    <th class="px-5 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Ticker</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Price</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">MA200</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">RSI</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Score</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Trend</th>
                    <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium text-right pr-5">Signal</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in data.signals" :key="s.ticker"
                    class="border-b border-finborder/40 hover:bg-finbase/60 transition-colors">
                    <td class="px-5 py-3.5 font-mono font-bold text-white">{{ s.ticker }}</td>
                    <td class="px-4 py-3.5 font-mono text-gray-200">{{ s.price.toLocaleString() }}</td>
                    <td class="px-4 py-3.5 font-mono text-gray-400">{{ s.ma200.toLocaleString() }}</td>
                    <!-- RSI with color coding -->
                    <td class="px-4 py-3.5 font-mono font-semibold"
                      :class="{
                        'text-finred': s.rsi > 70,
                        'text-fingreen': s.rsi < 40,
                        'text-gray-300': s.rsi >= 40 && s.rsi <= 70
                      }">
                      {{ s.rsi }}
                    </td>
                    <!-- Score bar -->
                    <td class="px-4 py-3.5">
                      <div class="flex items-center gap-2">
                        <div class="w-16 bg-finborder rounded-full h-1.5">
                          <div class="h-1.5 rounded-full transition-all"
                            :style="{ width: s.score + '%' }"
                            :class="s.score >= 70 ? 'bg-fingreen' : s.score >= 50 ? 'bg-finyellow' : 'bg-finred'">
                          </div>
                        </div>
                        <span class="text-xs font-mono text-gray-400">{{ s.score }}</span>
                      </div>
                    </td>
                    <!-- Trend -->
                    <td class="px-4 py-3.5">
                      <span v-if="s.trend === 'UP'" class="flex items-center gap-1 text-fingreen text-xs font-medium">
                        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18"/></svg>
                        Bullish
                      </span>
                      <span v-else-if="s.trend === 'DOWN'" class="flex items-center gap-1 text-finred text-xs font-medium">
                        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3"/></svg>
                        Bearish
                      </span>
                      <span v-else class="text-gray-500 text-xs">→ Flat</span>
                    </td>
                    <!-- Action Badge -->
                    <td class="px-4 py-3.5 pr-5 text-right">
                      <div class="flex flex-col items-end gap-1">
                        <span :class="s.action === 'BUY' ? 'badge-buy' : 'badge-wait'">
                          {{ s.action }}
                        </span>
                        <span class="tag-chip">{{ s.tag }}</span>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

      </div>
      <!-- end scrollable -->
    </div>
    <!-- end main -->
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { mockData } from './mockData.js'
const data = ref(mockData)
</script>
