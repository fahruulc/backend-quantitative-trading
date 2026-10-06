import { defineStore } from 'pinia'
import { marketAPI } from '../services/api'

export const useMarketStore = defineStore('market', {
  state: () => ({
    // Market Data
    macroData: null,
    sectorData: null,
    stockSignals: null,
    fullReport: null,

    // Token & Cache Stats
    tokenUsage: null,
    cacheStats: null,

    // UI State
    loading: false,
    error: null,
    lastUpdated: null,

    // Demo Mode
    demoMode: false
  }),

  getters: {
    // Check if data is fresh (< 5 minutes old)
    isDataFresh: (state) => {
      if (!state.lastUpdated) return false
      const fiveMinutes = 5 * 60 * 1000
      return (Date.now() - state.lastUpdated) < fiveMinutes
    },

    // Get token alert level
    tokenAlertLevel: (state) => {
      if (!state.tokenUsage) return 'ok'
      return state.tokenUsage.alert?.toLowerCase() || 'ok'
    },

    // Get token percentage
    tokenPercentage: (state) => {
      if (!state.tokenUsage) return 0
      return state.tokenUsage.percentage || 0
    }
  },

  actions: {
    // Fetch full market report (Phase 1-4 pipeline)
    async fetchFullReport() {
      this.loading = true
      this.error = null

      try {
        const response = await marketAPI.getFullReport()
        this.fullReport = response.data

        // Extract components
        this.macroData = {
          timestamp: response.data.timestamp,
          status: response.data.macro_status,
          reasoning: response.data.macro_reasoning,
          usd: response.data.usd,
          oil: response.data.oil,
          gold: response.data.gold,
          copper: response.data.copper,
          btc: response.data.btc,
          yield_rate: response.data.yield_rate,
          eido: response.data.eido
        }

        this.sectorData = {
          top_sector: response.data.top_sector,
          ai_insight: response.data.ai_insight
        }

        this.stockSignals = response.data.signals || []
        this.lastUpdated = Date.now()

        // Also fetch token usage
        await this.fetchTokenUsage()

      } catch (err) {
        this.error = err.response?.data?.detail || err.message || 'Failed to fetch market data'
        console.error('Error fetching full report:', err)
      } finally {
        this.loading = false
      }
    },

    // Fetch only macro data
    async fetchMacroData() {
      try {
        const response = await marketAPI.getMacro()
        this.macroData = response.data
      } catch (err) {
        console.error('Error fetching macro data:', err)
      }
    },

    // Fetch only sectors data
    async fetchSectorsData() {
      try {
        const response = await marketAPI.getSectors()
        this.sectorData = response.data.sector_data
        this.macroData = response.data.macro_data
      } catch (err) {
        console.error('Error fetching sectors data:', err)
      }
    },

    // Fetch only stocks data
    async fetchStocksData() {
      try {
        const response = await marketAPI.getStocks()
        this.stockSignals = response.data.picks || []
        this.sectorData = { ai_insight: response.data.insight }
      } catch (err) {
        console.error('Error fetching stocks data:', err)
      }
    },

    // Fetch token usage statistics
    async fetchTokenUsage() {
      try {
        const response = await marketAPI.getTokenUsage()
        this.tokenUsage = response.data
      } catch (err) {
        console.error('Error fetching token usage:', err)
      }
    },

    // Fetch cache statistics
    async fetchCacheStats() {
      try {
        const response = await marketAPI.getCacheStats()
        this.cacheStats = response.data
      } catch (err) {
        console.error('Error fetching cache stats:', err)
      }
    },

    // Toggle demo mode
    async toggleDemoMode(enabled) {
      try {
        const response = await marketAPI.toggleDemoMode(enabled)
        this.demoMode = enabled
        return response.data
      } catch (err) {
        console.error('Error toggling demo mode:', err)
        throw err
      }
    },

    // Trigger manual pre-fetch
    async triggerPrefetch() {
      try {
        const response = await marketAPI.triggerPrefetch()
        return response.data
      } catch (err) {
        console.error('Error triggering prefetch:', err)
        throw err
      }
    },

    // Clear all data
    clearData() {
      this.macroData = null
      this.sectorData = null
      this.stockSignals = null
      this.fullReport = null
      this.error = null
      this.lastUpdated = null
    }
  }
})
