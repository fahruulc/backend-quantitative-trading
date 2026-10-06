<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading market data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-finred/10 border border-finred/30 rounded-xl p-6 text-center">
      <p class="text-finred font-semibold mb-2">Failed to load data</p>
      <p class="text-gray-400 text-sm mb-4">{{ error }}</p>
      <button @click="loadData" class="px-4 py-2 bg-finblue text-white rounded-lg hover:bg-finblue/80 transition">
        Retry
      </button>
    </div>

    <!-- Data Loaded -->
    <template v-else>

      <!-- ── ROW 1: Macro Metric Cards ── -->
      <section>
        <h2 class="text-xs text-gray-500 uppercase tracking-widest mb-3 font-medium">Macro Sensors — Phase 1</h2>
        <div class="grid grid-cols-3 lg:grid-cols-6 gap-3">
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Yield Rate</p>
            <p class="font-mono font-bold text-xl text-white">{{ macroData?.yield_rate || 0 }}%</p>
            <p class="text-[10px] text-finred mt-1">↑ Hawkish</p>
          </div>
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Oil (USD)</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ macroData?.oil || 0 }}</p>
            <p class="text-[10px] text-fingreen mt-1">↑ Bullish</p>
          </div>
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Gold (USD)</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ macroData?.gold || 0 }}</p>
            <p class="text-[10px] text-fingreen mt-1">↑ ATH</p>
          </div>
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">USD/IDR</p>
            <p class="font-mono font-bold text-xl text-white">{{ (macroData?.usd || 0).toLocaleString() }}</p>
            <p class="text-[10px] text-fingreen mt-1">↓ Weakening</p>
          </div>
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">BTC</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ ((macroData?.btc || 0) / 1000).toFixed(1) }}K</p>
            <p class="text-[10px] text-fingreen mt-1">↑ Risk On</p>
          </div>
          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Copper</p>
            <p class="font-mono font-bold text-xl text-white">${{ macroData?.copper || 0 }}</p>
            <p class="text-[10px] text-gray-500 mt-1">→ Neutral</p>
          </div>
        </div>
      </section>

      <!-- ── ROW 2: AI Insight + Signals Table ── -->
      <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- AI Insight Panel -->
        <div class="lg:col-span-1 bg-fincard border border-finborder rounded-xl flex flex-col overflow-hidden">
          <div class="px-5 py-4 border-b border-finborder flex items-center justify-between gap-2">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
              <h3 class="text-white font-semibold text-sm">AI Analyst</h3>
            </div>
            <span
              v-if="aiModelUsed"
              class="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-finblue/10 text-finblue border border-finblue/30"
            >
              {{ aiModelUsed }}
            </span>
          </div>
          <div class="p-5 flex-1 space-y-4">
            <!-- Macro Reasoning -->
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Macro Reasoning</p>
              <p class="text-sm text-gray-300 leading-relaxed italic">"{{ macroData?.reasoning || 'Loading...' }}"</p>
            </div>
            <!-- Divider -->
            <div class="border-t border-finborder"></div>
            <!-- AI Insight -->
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Sector Narrative</p>
              <p class="text-sm text-gray-300 leading-relaxed">{{ sectorData?.ai_insight || 'Loading...' }}</p>
            </div>
          </div>
          <!-- Top Sector Badge -->
          <div class="px-5 py-4 border-t border-finborder bg-finbase/50 flex items-center justify-between">
            <div>
              <p class="text-[10px] text-gray-500 uppercase tracking-wider">Top Sector — Phase 2</p>
              <p class="text-white font-bold font-mono text-lg tracking-widest mt-0.5">{{ sectorData?.top_sector || 'N/A' }}</p>
            </div>
            <div class="w-10 h-10 rounded-xl bg-finyellow/10 border border-finyellow/30 flex items-center justify-center">
              <svg class="w-5 h-5 text-finyellow" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
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
            <span class="text-xs text-gray-500 font-mono">{{ stockSignals.length }} assets</span>
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
                <tr v-for="s in stockSignals" :key="s.ticker"
                  class="border-b border-finborder/40 hover:bg-finbase/60 transition-colors cursor-pointer">
                  <td class="px-5 py-3.5 font-mono font-bold text-white">{{ s.ticker }}</td>
                  <td class="px-4 py-3.5 font-mono text-gray-200">{{ s.price?.toLocaleString() || 0 }}</td>
                  <td class="px-4 py-3.5 font-mono text-gray-400">{{ s.ma200?.toLocaleString() || 0 }}</td>
                  <!-- RSI with color coding -->
                  <td class="px-4 py-3.5 font-mono font-semibold"
                    :class="{
                      'text-finred': s.rsi > 70,
                      'text-fingreen': s.rsi < 40,
                      'text-gray-300': s.rsi >= 40 && s.rsi <= 70
                    }">
                    {{ s.rsi || 0 }}
                  </td>
                  <!-- Score bar -->
                  <td class="px-4 py-3.5">
                    <div class="flex items-center gap-2">
                      <div class="w-16 bg-finborder rounded-full h-1.5">
                        <div class="h-1.5 rounded-full transition-all"
                          :style="{ width: (s.score || 0) + '%' }"
                          :class="(s.score || 0) >= 70 ? 'bg-fingreen' : (s.score || 0) >= 50 ? 'bg-finyellow' : 'bg-finred'">
                        </div>
                      </div>
                      <span class="text-xs font-mono text-gray-400">{{ s.score || 0 }}</span>
                    </div>
                  </td>
                  <!-- Trend -->
                  <td class="px-4 py-3.5">
                    <span v-if="s.trend === 'UP'" class="flex items-center gap-1 text-fingreen text-xs font-medium">
                      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
                      </svg>
                      Bullish
                    </span>
                    <span v-else-if="s.trend === 'DOWN'" class="flex items-center gap-1 text-finred text-xs font-medium">
                      <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
                      </svg>
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

    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMarketStore } from '../stores/marketStore'

const marketStore = useMarketStore()

// Local state
const loading = ref(false)

// Computed from store
const error = computed(() => marketStore.error)
const macroData = computed(() => marketStore.macroData)
const sectorData = computed(() => marketStore.sectorData)
const stockSignals = computed(() => marketStore.stockSignals || [])
const aiModelUsed = computed(() =>
  marketStore.fullReport?.ai_model_used ||
  marketStore.stockSignals?.find(s => s.ai_model_used)?.ai_model_used ||
  null
)

// Load data
const loadData = async () => {
  loading.value = true
  try {
    await marketStore.fetchFullReport()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Load data if not already loaded or if stale
  if (!marketStore.isDataFresh) {
    loadData()
  }
})
</script>
