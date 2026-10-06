<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading macro data...</p>
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

    <template v-else>
      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-white font-bold text-xl">Macro Sensors</h2>
          <p class="text-xs text-gray-500 mt-1">Global market indicators — Phase 1</p>
        </div>
        <div class="flex items-center gap-3">
          <span
            class="text-xs font-bold uppercase tracking-widest px-3 py-1.5 rounded-lg border"
            :class="statusClass"
          >
            {{ macroData.macro_status || 'N/A' }}
          </span>
          <button @click="loadData" class="px-4 py-2 bg-finblue text-white text-sm rounded-lg hover:bg-finblue/80 transition">
            Refresh
          </button>
        </div>
      </div>

      <!-- Macro Reasoning -->
      <div
        v-if="macroData.macro_reasoning"
        class="bg-finblue/10 border border-finblue/30 rounded-xl px-5 py-4 flex items-start gap-3"
      >
        <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue mt-1.5 shrink-0"></div>
        <div>
          <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Market Insight</p>
          <p class="text-sm text-gray-300 leading-relaxed italic">"{{ macroData.macro_reasoning }}"</p>
        </div>
      </div>

      <!-- Metrics Grid -->
      <section>
        <h2 class="text-xs text-gray-500 uppercase tracking-widest mb-3 font-medium">Global Indicators</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">USD/IDR</p>
            <p class="font-mono font-bold text-xl text-white">{{ formatNumber(macroData.usd) }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.usd, 16000)">
              {{ changePct(macroData.usd, 16000) }} vs 16.000
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Crude Oil</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ formatNumber(macroData.oil) }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.oil, 80)">
              {{ changePct(macroData.oil, 80) }} vs $80
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Gold</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ formatNumber(macroData.gold) }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.gold, 2300)">
              {{ changePct(macroData.gold, 2300) }} vs $2.300
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Copper</p>
            <p class="font-mono font-bold text-xl text-white">${{ macroData.copper?.toFixed(2) ?? '—' }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.copper, 4.2)">
              {{ changePct(macroData.copper, 4.2) }} vs $4.20
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Bitcoin</p>
            <p class="font-mono font-bold text-xl text-finyellow">${{ formatNumber(macroData.btc) }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.btc, 100000)">
              {{ changePct(macroData.btc, 100000) }} vs $100K
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">US 10Y Yield</p>
            <p class="font-mono font-bold text-xl text-white">{{ macroData.yield_rate?.toFixed(2) ?? '—' }}%</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.yield_rate, 4.3)">
              {{ changePct(macroData.yield_rate, 4.3) }} vs 4.30%
            </p>
          </div>

          <div class="metric-card text-center">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">EIDO ETF</p>
            <p class="font-mono font-bold text-xl text-white">${{ macroData.eido?.toFixed(2) ?? '—' }}</p>
            <p class="text-[10px] mt-1" :class="changeClass(macroData.eido, 23)">
              {{ changePct(macroData.eido, 23) }} vs $23
            </p>
          </div>

          <div class="metric-card text-center border-finyellow/40">
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Leading Sector</p>
            <p class="font-mono font-bold text-xl text-finyellow">{{ macroData.top_sector || 'N/A' }}</p>
            <p class="text-[10px] text-gray-500 mt-1">Momentum Leader</p>
          </div>

        </div>
      </section>

      <!-- AI Insight Panel -->
      <div class="bg-fincard border border-finborder rounded-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-finborder flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
          <h3 class="text-white font-semibold text-sm">AI Market Analysis</h3>
        </div>
        <div class="p-5">
          <p class="text-sm text-gray-300 leading-relaxed">{{ macroData.ai_insight || 'No AI insight available yet.' }}</p>
        </div>
        <div class="px-5 py-3 border-t border-finborder bg-finbase/50">
          <p class="text-[10px] text-gray-500 font-mono">Last updated: {{ formatTimestamp(macroData.timestamp) }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useMarketStore } from '@/stores/marketStore'

export default {
  name: 'MacroSensorsPage',
  setup() {
    const store = useMarketStore()
    const loading = ref(true)
    const error = ref(null)
    const macroData = ref({})

    const statusClass = computed(() => {
      const status = macroData.value.macro_status
      if (status?.includes('RISK ON')) return 'bg-fingreen/20 text-fingreen border-fingreen/40'
      if (status?.includes('RISK OFF')) return 'bg-finred/20 text-finred border-finred/40'
      return 'bg-finyellow/20 text-finyellow border-finyellow/40'
    })

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await store.api.get('/frontend/macro-sensors')
        macroData.value = response.data
      } catch (err) {
        error.value = err.response?.data?.detail || err.message
      } finally {
        loading.value = false
      }
    }

    const formatNumber = (num) => {
      if (num == null) return '—'
      return new Intl.NumberFormat('id-ID').format(Math.round(num))
    }

    const changeClass = (current, baseline) => {
      if (current == null) return 'text-gray-500'
      return current > baseline ? 'text-fingreen' : 'text-finred'
    }

    const changePct = (current, baseline) => {
      if (current == null) return '—'
      const change = ((current - baseline) / baseline) * 100
      const sign = change >= 0 ? '+' : ''
      return `${sign}${change.toFixed(2)}%`
    }

    const formatTimestamp = (ts) => {
      if (!ts) return '—'
      try {
        return new Date(ts).toLocaleString('id-ID')
      } catch {
        return ts
      }
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      error,
      macroData,
      statusClass,
      loadData,
      formatNumber,
      changeClass,
      changePct,
      formatTimestamp
    }
  }
}
</script>
