<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading sector data...</p>
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
          <h2 class="text-white font-bold text-xl">Sector Rotation</h2>
          <p class="text-xs text-gray-500 mt-1">Sector performance comparison &amp; momentum — Phase 2</p>
        </div>
        <button @click="loadData" class="px-4 py-2 bg-finblue text-white text-sm rounded-lg hover:bg-finblue/80 transition">
          Refresh
        </button>
      </div>

      <!-- Sector Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div
          v-for="(sector, index) in sectorData"
          :key="sector.sector"
          class="bg-fincard border rounded-xl overflow-hidden"
          :class="index === 0 ? 'border-finyellow/50' : 'border-finborder'"
        >
          <!-- Card Header -->
          <div class="px-5 py-4 border-b border-finborder flex items-center justify-between">
            <div class="flex items-center gap-2">
              <div
                class="w-2 h-2 rounded-full"
                :class="index === 0 ? 'bg-finyellow' : 'bg-finblue shadow-glow-blue'"
              ></div>
              <h3 class="text-white font-semibold text-sm font-mono tracking-widest">{{ sector.sector }}</h3>
            </div>
            <div class="flex items-center gap-2">
              <span
                v-if="index === 0"
                class="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-finyellow/20 text-finyellow border border-finyellow/40"
              >
                Leader
              </span>
              <span class="text-xs text-gray-500 font-mono">{{ sector.stock_count }} stocks</span>
            </div>
          </div>

          <!-- Metrics -->
          <div class="p-5 space-y-4">
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <p class="text-[10px] text-gray-500 uppercase tracking-widest">Avg Score</p>
                <p class="font-mono font-bold text-white">{{ sector.avg_score?.toFixed(1) ?? '—' }}</p>
              </div>
              <div class="w-full bg-finborder rounded-full h-1.5">
                <div
                  class="h-1.5 rounded-full transition-all"
                  :class="(sector.avg_score || 0) >= 70 ? 'bg-fingreen' : (sector.avg_score || 0) >= 55 ? 'bg-finyellow' : 'bg-finred'"
                  :style="{ width: Math.min(sector.avg_score || 0, 100) + '%' }"
                ></div>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Avg ROE</p>
                <p class="font-mono font-bold text-lg text-white">{{ sector.avg_roe?.toFixed(1) ?? '—' }}%</p>
              </div>
              <div>
                <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Avg Growth</p>
                <p class="font-mono font-bold text-lg text-fingreen">{{ sector.avg_growth?.toFixed(1) ?? '—' }}%</p>
              </div>
            </div>
          </div>

          <!-- Top Stocks -->
          <div class="border-t border-finborder">
            <p class="px-5 pt-3 pb-2 text-[10px] text-gray-500 uppercase tracking-widest">Top Performers</p>
            <div
              v-for="stock in sector.top_stocks"
              :key="stock.ticker"
              class="px-5 py-2.5 flex items-center justify-between border-t border-finborder/40 hover:bg-finbase/60 transition-colors cursor-pointer"
              @click="goToChart(stock.ticker)"
            >
              <span class="font-mono font-bold text-white text-sm">{{ stock.ticker.replace('.JK', '') }}</span>
              <div class="flex items-center gap-3">
                <span class="font-mono text-xs text-gray-400">{{ formatPrice(stock.price) }}</span>
                <span
                  class="font-mono text-xs font-bold px-2 py-0.5 rounded"
                  :class="scoreClass(stock.score)"
                >
                  {{ stock.score?.toFixed(0) ?? '—' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Comparison Bars -->
      <div class="bg-fincard border border-finborder rounded-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-finborder flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-fingreen shadow-glow-green"></div>
          <h3 class="text-white font-semibold text-sm">Sector Metrics Comparison</h3>
        </div>

        <div class="p-5 space-y-5">
          <!-- Legend -->
          <div class="flex items-center gap-5 text-[10px] text-gray-400">
            <span class="flex items-center gap-1.5">
              <span class="w-3 h-3 rounded-sm bg-finblue inline-block"></span> Avg Score
            </span>
            <span class="flex items-center gap-1.5">
              <span class="w-3 h-3 rounded-sm bg-fingreen inline-block"></span> Avg ROE
            </span>
            <span class="flex items-center gap-1.5">
              <span class="w-3 h-3 rounded-sm bg-finyellow inline-block"></span> Avg Growth
            </span>
          </div>

          <div v-for="sector in sectorData" :key="sector.sector" class="space-y-2">
            <p class="text-xs font-mono font-bold text-gray-300 tracking-widest">{{ sector.sector }}</p>

            <div class="flex items-center gap-3">
              <span class="text-[10px] text-gray-500 w-14 shrink-0">Score</span>
              <div class="flex-1 bg-finborder/50 rounded-full h-4 relative">
                <div
                  class="h-4 rounded-full bg-finblue transition-all flex items-center justify-end pr-2"
                  :style="{ width: Math.min(sector.avg_score || 0, 100) + '%' }"
                >
                  <span class="text-[10px] font-mono font-bold text-white">{{ sector.avg_score?.toFixed(0) ?? '—' }}</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <span class="text-[10px] text-gray-500 w-14 shrink-0">ROE</span>
              <div class="flex-1 bg-finborder/50 rounded-full h-4 relative">
                <div
                  class="h-4 rounded-full bg-fingreen transition-all flex items-center justify-end pr-2"
                  :style="{ width: Math.min((sector.avg_roe || 0) * 3, 100) + '%' }"
                >
                  <span class="text-[10px] font-mono font-bold text-white">{{ sector.avg_roe?.toFixed(0) ?? '—' }}%</span>
                </div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <span class="text-[10px] text-gray-500 w-14 shrink-0">Growth</span>
              <div class="flex-1 bg-finborder/50 rounded-full h-4 relative">
                <div
                  class="h-4 rounded-full bg-finyellow transition-all flex items-center justify-end pr-2"
                  :style="{ width: Math.min((sector.avg_growth || 0) * 3, 100) + '%' }"
                >
                  <span class="text-[10px] font-mono font-bold text-white">{{ sector.avg_growth?.toFixed(0) ?? '—' }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketStore } from '@/stores/marketStore'

export default {
  name: 'SectorRotationPage',
  setup() {
    const store = useMarketStore()
    const router = useRouter()
    const loading = ref(true)
    const error = ref(null)
    const sectorData = ref([])

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await store.api.get('/frontend/sector-rotation')
        sectorData.value = response.data.sectors || []
      } catch (err) {
        error.value = err.response?.data?.detail || err.message
      } finally {
        loading.value = false
      }
    }

    const formatPrice = (price) => {
      if (!price) return '—'
      return new Intl.NumberFormat('id-ID').format(price)
    }

    const scoreClass = (score) => {
      if (!score) return 'bg-finborder text-gray-400'
      if (score >= 80) return 'bg-fingreen/20 text-fingreen'
      if (score >= 70) return 'bg-fingreen/10 text-fingreen'
      if (score >= 60) return 'bg-finyellow/20 text-finyellow'
      return 'bg-finred/20 text-finred'
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
      sectorData,
      loadData,
      formatPrice,
      scoreClass,
      goToChart
    }
  }
}
</script>
