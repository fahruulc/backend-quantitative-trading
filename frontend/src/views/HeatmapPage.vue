<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading heatmap...</p>
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
          <h2 class="text-white font-bold text-xl">Stock Heatmap</h2>
          <p class="text-xs text-gray-500 mt-1">Visual performance overview by sector — click a cell for technical chart</p>
        </div>
        <button @click="loadData" class="px-4 py-2 bg-finblue text-white text-sm rounded-lg hover:bg-finblue/80 transition">
          Refresh
        </button>
      </div>

      <!-- Legend -->
      <div class="bg-fincard border border-finborder rounded-xl px-5 py-3 flex items-center gap-5 flex-wrap">
        <span class="text-[10px] text-gray-500 uppercase tracking-widest">Score Range</span>
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm bg-fingreen"></span>
          <span class="text-xs text-gray-400">Excellent (80+)</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm bg-fingreen/50"></span>
          <span class="text-xs text-gray-400">Good (70–79)</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm bg-finyellow"></span>
          <span class="text-xs text-gray-400">Fair (60–69)</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm bg-orange-500"></span>
          <span class="text-xs text-gray-400">Moderate (50–59)</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-sm bg-finred"></span>
          <span class="text-xs text-gray-400">Poor (&lt;50)</span>
        </div>
      </div>

      <!-- Heatmap Grid by Sector -->
      <div
        v-for="(stocks, sector) in heatmapData.heatmap"
        :key="sector"
        class="bg-fincard border border-finborder rounded-xl overflow-hidden"
      >
        <div class="px-5 py-4 border-b border-finborder flex items-center gap-2">
          <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
          <h3 class="text-white font-semibold text-sm font-mono tracking-widest">{{ sector }}</h3>
          <span class="text-xs text-gray-500 font-mono ml-auto">{{ stocks.length }} stocks</span>
        </div>

        <div class="p-4 grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-5 gap-3">
          <div
            v-for="stock in stocks"
            :key="stock.ticker"
            class="rounded-lg p-3 cursor-pointer border transition-all hover:scale-[1.03] hover:shadow-lg"
            :class="getHeatClass(stock.score)"
            @click="selectStock(stock)"
            :title="`${stock.ticker}: Score ${stock.score?.toFixed(0)}, ROE ${stock.roe?.toFixed(1) ?? '—'}%`"
          >
            <p class="font-mono font-bold text-white text-sm">{{ stock.ticker.replace('.JK', '') }}</p>
            <p class="font-mono font-bold text-2xl text-white mt-1">{{ stock.score?.toFixed(0) ?? '—' }}</p>
            <p class="text-[10px] text-gray-300 font-mono mt-0.5">{{ formatPrice(stock.price) }}</p>
          </div>
        </div>
      </div>

      <!-- Selected Stock Detail Panel -->
      <div v-if="selectedStock" class="bg-fincard border border-finborder rounded-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-finborder flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-fingreen shadow-glow-green"></div>
            <h3 class="text-white font-semibold text-sm font-mono tracking-wider">{{ selectedStock.ticker }}</h3>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="goToChart(selectedStock.ticker)"
              class="px-3 py-1.5 bg-finblue text-white text-xs rounded-lg hover:bg-finblue/80 transition font-semibold"
            >
              Open Chart →
            </button>
            <button @click="selectedStock = null" class="text-gray-500 hover:text-white transition px-2">✕</button>
          </div>
        </div>

        <div class="p-5 grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Price</p>
            <p class="font-mono font-bold text-lg text-white">{{ formatPrice(selectedStock.price) }}</p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Score</p>
            <p class="font-mono font-bold text-lg text-finblue">{{ selectedStock.score?.toFixed(0) ?? '—' }}</p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">ROE</p>
            <p class="font-mono font-bold text-lg text-white">{{ selectedStock.roe?.toFixed(1) ?? '—' }}%</p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">EPS Growth</p>
            <p class="font-mono font-bold text-lg text-fingreen">{{ selectedStock.eps_growth?.toFixed(1) ?? '—' }}%</p>
          </div>
          <div>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mb-1">Rev Growth</p>
            <p class="font-mono font-bold text-lg text-fingreen">{{ selectedStock.revenue_growth?.toFixed(1) ?? '—' }}%</p>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <section>
        <h2 class="text-xs text-gray-500 uppercase tracking-widest mb-3 font-medium">Market Summary</h2>
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div class="metric-card text-center">
            <p class="font-mono font-bold text-2xl text-fingreen">{{ excellentCount }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Excellent</p>
          </div>
          <div class="metric-card text-center">
            <p class="font-mono font-bold text-2xl text-finyellow">{{ goodCount + fairCount }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Good + Fair</p>
          </div>
          <div class="metric-card text-center">
            <p class="font-mono font-bold text-2xl text-finred">{{ poorCount }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Watch List</p>
          </div>
          <div class="metric-card text-center">
            <p class="font-mono font-bold text-2xl text-white">{{ heatmapData.all.length }}</p>
            <p class="text-[10px] text-gray-500 uppercase tracking-widest mt-1">Total Stocks</p>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMarketStore } from '@/stores/marketStore'

export default {
  name: 'HeatmapPage',
  setup() {
    const store = useMarketStore()
    const router = useRouter()
    const loading = ref(true)
    const error = ref(null)
    const heatmapData = ref({ heatmap: {}, all: [] })
    const selectedStock = ref(null)

    const excellentCount = computed(() =>
      heatmapData.value.all.filter(s => (s.score || 0) >= 80).length
    )
    const goodCount = computed(() =>
      heatmapData.value.all.filter(s => (s.score || 0) >= 70 && (s.score || 0) < 80).length
    )
    const fairCount = computed(() =>
      heatmapData.value.all.filter(s => (s.score || 0) >= 60 && (s.score || 0) < 70).length
    )
    const poorCount = computed(() =>
      heatmapData.value.all.filter(s => (s.score || 0) < 60).length
    )

    const loadData = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await store.api.get('/frontend/heatmap')
        heatmapData.value = response.data
      } catch (err) {
        error.value = err.response?.data?.detail || err.message
      } finally {
        loading.value = false
      }
    }

    const getHeatClass = (score) => {
      if (!score) return 'bg-finred/20 border-finred/40'
      if (score >= 80) return 'bg-fingreen/30 border-fingreen/50'
      if (score >= 70) return 'bg-fingreen/15 border-fingreen/30'
      if (score >= 60) return 'bg-finyellow/20 border-finyellow/40'
      if (score >= 50) return 'bg-orange-500/20 border-orange-500/40'
      return 'bg-finred/20 border-finred/40'
    }

    const formatPrice = (price) => {
      if (!price) return '—'
      return new Intl.NumberFormat('id-ID').format(price)
    }

    const selectStock = (stock) => {
      selectedStock.value = stock
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
      heatmapData,
      selectedStock,
      excellentCount,
      goodCount,
      fairCount,
      poorCount,
      loadData,
      getHeatClass,
      formatPrice,
      selectStock,
      goToChart
    }
  }
}
</script>
