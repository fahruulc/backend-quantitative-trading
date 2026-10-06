<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading stock signals...</p>
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
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-white font-bold text-xl">Stock Signals</h2>
          <p class="text-xs text-gray-500 mt-1">Fundamental recommendations — Phase 3 · click a row for technical chart</p>
        </div>
        <button @click="loadData" class="px-4 py-2 bg-finblue text-white text-sm rounded-lg hover:bg-finblue/80 transition">
          Refresh
        </button>
      </div>

      <!-- Filter Bar -->
      <div class="bg-fincard border border-finborder rounded-xl px-5 py-3 flex items-center justify-between flex-wrap gap-3">
        <div class="flex items-center gap-3">
          <span class="text-[10px] text-gray-500 uppercase tracking-widest">Min Score</span>
          <div class="flex gap-1.5">
            <button
              v-for="opt in scoreFilters"
              :key="opt.label"
              @click="setFilter(opt.value)"
              class="px-3 py-1 rounded-lg text-xs font-bold transition"
              :class="minScore === opt.value
                ? 'bg-finblue text-white'
                : 'bg-finbase border border-finborder text-gray-400 hover:text-white'"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
        <span class="text-xs text-gray-500 font-mono">{{ signals.length }} assets</span>
      </div>

      <!-- Signals Table -->
      <div class="bg-fincard border border-finborder rounded-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-finborder flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-fingreen shadow-glow-green"></div>
          <h3 class="text-white font-semibold text-sm">Fundamental Signals</h3>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-finborder text-left">
                <th class="px-5 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Ticker</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Price</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Score</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">ROE</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">DER</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">PBV</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Fwd PE</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">EPS Grw</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Div Yld</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium">Flow</th>
                <th class="px-4 py-3 text-[10px] text-gray-500 uppercase tracking-widest font-medium text-right pr-5">Signal</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="s in signals"
                :key="s.ticker"
                class="border-b border-finborder/40 hover:bg-finbase/60 transition-colors cursor-pointer"
                @click="goToChart(s.ticker)"
              >
                <td class="px-5 py-3.5 font-mono font-bold text-white">{{ s.ticker.replace('.JK', '') }}</td>
                <td class="px-4 py-3.5 font-mono text-gray-200">{{ formatPrice(s.price) }}</td>
                <td class="px-4 py-3.5">
                  <div class="flex items-center gap-2">
                    <div class="w-14 bg-finborder rounded-full h-1.5">
                      <div
                        class="h-1.5 rounded-full transition-all"
                        :style="{ width: Math.min(s.sectors_score || 0, 100) + '%' }"
                        :class="(s.sectors_score || 0) >= 70 ? 'bg-fingreen' : (s.sectors_score || 0) >= 50 ? 'bg-finyellow' : 'bg-finred'"
                      ></div>
                    </div>
                    <span class="text-xs font-mono text-gray-400">{{ s.sectors_score?.toFixed(0) ?? '—' }}</span>
                  </div>
                </td>
                <td class="px-4 py-3.5 font-mono" :class="(s.roe || 0) >= 15 ? 'text-fingreen' : 'text-gray-300'">
                  {{ s.roe?.toFixed(1) ?? '—' }}%
                </td>
                <td class="px-4 py-3.5 font-mono" :class="(s.der || 0) <= 0.5 ? 'text-fingreen' : (s.der || 0) > 1.5 ? 'text-finred' : 'text-gray-300'">
                  {{ s.der?.toFixed(2) ?? '—' }}
                </td>
                <td class="px-4 py-3.5 font-mono text-gray-300">{{ s.pbv?.toFixed(2) ?? '—' }}</td>
                <td class="px-4 py-3.5 font-mono text-gray-300">{{ s.forward_pe?.toFixed(1) ?? '—' }}</td>
                <td class="px-4 py-3.5 font-mono" :class="(s.eps_growth || 0) >= 10 ? 'text-fingreen' : 'text-gray-300'">
                  {{ s.eps_growth?.toFixed(1) ?? '—' }}%
                </td>
                <td class="px-4 py-3.5 font-mono text-gray-300">{{ s.dividend_yield?.toFixed(2) ?? '—' }}%</td>
                <td class="px-4 py-3.5">
                  <span
                    class="text-[10px] font-bold uppercase tracking-wider"
                    :class="s.institutional_flow === 'positive' ? 'text-fingreen' : 'text-gray-500'"
                  >
                    {{ s.institutional_flow || '—' }}
                  </span>
                </td>
                <td class="px-4 py-3.5 pr-5 text-right">
                  <span
                    class="text-xs font-bold px-2.5 py-1 rounded uppercase tracking-widest border"
                    :class="actionClass(s.action)"
                  >
                    {{ s.action }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- AI Insights -->
      <section>
        <h2 class="text-xs text-gray-500 uppercase tracking-widest mb-3 font-medium">AI Stock Insights — Top 3</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div
            v-for="s in signals.slice(0, 3)"
            :key="s.ticker"
            class="bg-fincard border border-finborder rounded-xl overflow-hidden"
          >
            <div class="px-5 py-4 border-b border-finborder flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
                <span class="font-mono font-bold text-white">{{ s.ticker.replace('.JK', '') }}</span>
              </div>
              <span
                class="text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-widest border"
                :class="actionClass(s.action)"
              >
                {{ s.action }}
              </span>
            </div>
            <div class="p-5">
              <p class="text-sm text-gray-300 leading-relaxed">{{ s.ai_insight || 'No AI insight available' }}</p>
              <div class="flex items-center gap-4 mt-4 text-[10px] text-gray-500 font-mono">
                <span>ROE {{ s.roe?.toFixed(1) ?? '—' }}%</span>
                <span>Score {{ s.sectors_score?.toFixed(0) ?? '—' }}</span>
                <span>Growth {{ s.eps_growth?.toFixed(1) ?? '—' }}%</span>
                <span v-if="s.ai_model_used" class="ml-auto text-finblue">{{ s.ai_model_used }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketStore } from '@/stores/marketStore'

export default {
  name: 'StockSignalsPage',
  setup() {
    const store = useMarketStore()
    const router = useRouter()
    const loading = ref(true)
    const error = ref(null)
    const signals = ref([])
    const minScore = ref(null)

    const scoreFilters = [
      { label: 'All', value: null },
      { label: '60+', value: 60 },
      { label: '70+', value: 70 },
      { label: '80+', value: 80 }
    ]

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const params = {}
        if (minScore.value) params.min_score = minScore.value
        const response = await store.api.get('/frontend/stock-signals', { params })
        signals.value = response.data.signals || []
      } catch (err) {
        error.value = err.response?.data?.detail || err.message
      } finally {
        loading.value = false
      }
    }

    const setFilter = (val) => {
      minScore.value = val
      loadData()
    }

    const formatPrice = (price) => {
      if (!price) return '—'
      return new Intl.NumberFormat('id-ID').format(price)
    }

    const actionClass = (action) => {
      if (action === 'STRONG BUY') return 'bg-fingreen/20 text-fingreen border-fingreen/40'
      if (action === 'BUY') return 'bg-fingreen/10 text-fingreen border-fingreen/30'
      return 'bg-gray-700/50 text-gray-400 border-gray-600/50'
    }

    const goToChart = (ticker) => {
      router.push(`/technical/${ticker}`)
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      error,
      signals,
      minScore,
      scoreFilters,
      loadData,
      setFilter,
      formatPrice,
      actionClass,
      goToChart
    }
  }
}
</script>
