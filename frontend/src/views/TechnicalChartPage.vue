<template>
  <div class="p-6 space-y-6">

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center h-96">
      <div class="text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-finblue mx-auto mb-4"></div>
        <p class="text-gray-400">Loading chart for {{ ticker }}...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-finred/10 border border-finred/30 rounded-xl p-6 text-center">
      <p class="text-finred font-semibold mb-2">Failed to load chart</p>
      <p class="text-gray-400 text-sm mb-4">{{ error }}</p>
      <button @click="loadChart" class="px-4 py-2 bg-finblue text-white rounded-lg hover:bg-finblue/80 transition">
        Retry
      </button>
    </div>

    <!-- Chart Loaded -->
    <template v-else>
      <!-- Header Card -->
      <div class="bg-fincard border border-finborder rounded-xl overflow-hidden">
        <div class="px-5 py-4 border-b border-finborder flex items-center justify-between flex-wrap gap-3">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full bg-finblue shadow-glow-blue"></div>
            <div>
              <h2 class="text-white font-bold font-mono text-xl tracking-wider">{{ ticker }}</h2>
              <p class="text-[10px] text-gray-500 uppercase tracking-widest">Technical Chart — yfinance {{ chartData?.period }}</p>
            </div>
          </div>

          <div class="flex items-center gap-6">
            <!-- Last Price -->
            <div class="text-right">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest">Last Price</p>
              <p class="font-mono font-bold text-2xl text-white">{{ formatNumber(chartData?.last_price) }}</p>
            </div>
            <!-- Change -->
            <div class="text-right">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest">Change</p>
              <p class="font-mono font-bold text-xl" :class="(chartData?.change_pct || 0) >= 0 ? 'text-fingreen' : 'text-finred'">
                {{ (chartData?.change_pct || 0) >= 0 ? '+' : '' }}{{ chartData?.change_pct?.toFixed(2) }}%
              </p>
            </div>
            <!-- MA position -->
            <div class="text-right" v-if="chartData?.ma_slow_value">
              <p class="text-[10px] text-gray-500 uppercase tracking-widest">{{ slowMaLabel }}</p>
              <p class="font-mono text-sm text-gray-300">{{ formatNumber(chartData?.ma_slow_value) }}</p>
              <span
                class="text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded"
                :class="chartData?.above_ma_slow
                  ? 'bg-fingreen/20 text-fingreen border border-fingreen/40'
                  : 'bg-finred/20 text-finred border border-finred/40'"
              >
                {{ chartData?.above_ma_slow ? '▲ Above' : '▼ Below' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Interval Toggle -->
        <div class="px-5 py-3 border-b border-finborder bg-finbase/50 flex items-center gap-2">
          <span class="text-[10px] text-gray-500 uppercase tracking-widest mr-2">Timeframe</span>
          <button
            @click="setInterval('1d')"
            class="px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition"
            :class="interval === '1d'
              ? 'bg-finblue text-white'
              : 'bg-fincard border border-finborder text-gray-400 hover:text-white'"
          >
            Daily
          </button>
          <button
            @click="setInterval('1wk')"
            class="px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition"
            :class="interval === '1wk'
              ? 'bg-finblue text-white'
              : 'bg-fincard border border-finborder text-gray-400 hover:text-white'"
          >
            Weekly
          </button>

          <!-- Legend -->
          <div class="ml-auto flex items-center gap-4 text-[10px] text-gray-400">
            <span class="flex items-center gap-1">
              <span class="w-3 h-0.5 bg-finblue inline-block"></span> {{ maLabels[0] }}
            </span>
            <span class="flex items-center gap-1">
              <span class="w-3 h-0.5 bg-finyellow inline-block"></span> {{ maLabels[1] }}
            </span>
            <span class="flex items-center gap-1">
              <span class="w-3 h-0.5 inline-block" style="background:#AB47BC"></span> {{ maLabels[2] }}
            </span>
          </div>
        </div>

        <!-- Chart -->
        <div class="p-4">
          <apexchart
            type="candlestick"
            height="480"
            :options="chartOptions"
            :series="series"
          ></apexchart>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import VueApexCharts from 'vue3-apexcharts'
import { useMarketStore } from '../stores/marketStore'

const apexchart = VueApexCharts
const route = useRoute()
const marketStore = useMarketStore()

const ticker = computed(() => (route.params.ticker || '').toUpperCase())
const interval = ref('1d')
const period = '1y'
const loading = ref(false)
const error = ref(null)
const chartData = ref(null)

const MA_CONFIG = {
  '1d': { keys: ['ma20', 'ma50', 'ma200'], labels: ['MA20', 'MA50', 'MA200'] },
  '1wk': { keys: ['ma10', 'ma20', 'ma40'], labels: ['MA10', 'MA20', 'MA40'] }
}

const maLabels = computed(() => MA_CONFIG[interval.value].labels)
const slowMaLabel = computed(() => MA_CONFIG[interval.value].labels[2])

const formatNumber = (n) => (n == null ? '—' : Number(n).toLocaleString('id-ID'))

const series = computed(() => {
  if (!chartData.value) return []
  const candles = chartData.value.candles.map(c => ({
    x: c.date,
    y: [c.open, c.high, c.low, c.close]
  }))
  const maKeys = MA_CONFIG[interval.value].keys
  const maColors = ['#2962FF', '#F5A623', '#AB47BC']

  const maSeries = maKeys.map((key, i) => ({
    name: MA_CONFIG[interval.value].labels[i],
    type: 'line',
    data: (chartData.value.ma[key] || []).map(p => ({ x: p.date, y: p.value }))
  }))

  return [{ name: 'Price', type: 'candlestick', data: candles }, ...maSeries]
})

const chartOptions = computed(() => ({
  chart: {
    type: 'candlestick',
    background: 'transparent',
    toolbar: { show: true, tools: { download: false } },
    animations: { enabled: false }
  },
  theme: { mode: 'dark' },
  plotOptions: {
    candlestick: {
      colors: { upward: '#00C076', downward: '#F23645' },
      wick: { useFillColor: true }
    }
  },
  stroke: {
    width: [1, 1.5, 1.5, 1.5],
    curve: 'smooth'
  },
  colors: ['#00C076', '#2962FF', '#F5A623', '#AB47BC'],
  xaxis: {
    type: 'category',
    labels: {
      style: { colors: '#6b7280', fontSize: '10px', fontFamily: 'JetBrains Mono' },
      rotate: -45,
      hideOverlappingLabels: true
    },
    axisBorder: { color: '#1E2736' },
    axisTicks: { color: '#1E2736' },
    tooltip: { enabled: false }
  },
  yaxis: {
    labels: {
      style: { colors: '#6b7280', fontSize: '11px', fontFamily: 'JetBrains Mono' },
      formatter: (v) => v?.toLocaleString('id-ID')
    }
  },
  grid: {
    borderColor: '#1E2736',
    strokeDashArray: 3
  },
  tooltip: {
    theme: 'dark',
    style: { fontFamily: 'JetBrains Mono' }
  },
  legend: {
    show: true,
    position: 'top',
    labels: { colors: '#9ca3af' },
    markers: { width: 10, height: 10 }
  },
  dataLabels: { enabled: false }
}))

const loadChart = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await marketStore.api.get(`/frontend/chart/${ticker.value}`, {
      params: { period, interval: interval.value }
    })
    chartData.value = res.data
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Failed to load chart data'
  } finally {
    loading.value = false
  }
}

const setInterval = (val) => {
  if (interval.value !== val) {
    interval.value = val
  }
}

watch(interval, () => loadChart())

onMounted(() => loadChart())
</script>
