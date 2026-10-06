import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Overview',
        component: () => import('../views/OverviewPage.vue'),
        meta: { title: 'Dashboard Overview' }
      },
      {
        path: 'macro-sensors',
        name: 'MacroSensors',
        component: () => import('../views/MacroSensorsPage.vue'),
        meta: { title: 'Macro Sensors' }
      },
      {
        path: 'sector-rotation',
        name: 'SectorRotation',
        component: () => import('../views/SectorRotationPage.vue'),
        meta: { title: 'Sector Rotation' }
      },
      {
        path: 'stock-signals',
        name: 'StockSignals',
        component: () => import('../views/StockSignalsPage.vue'),
        meta: { title: 'Stock Signals' }
      },
      {
        path: 'heatmap',
        name: 'Heatmap',
        component: () => import('../views/HeatmapPage.vue'),
        meta: { title: 'Market Heatmap' }
      },
      {
        path: 'fundamental/:ticker',
        name: 'FundamentalDetail',
        component: () => import('../views/FundamentalDetailPage.vue'),
        meta: { title: 'Fundamental Analysis' }
      },
      {
        path: 'technical/:ticker',
        name: 'TechnicalChart',
        component: () => import('../views/TechnicalChartPage.vue'),
        meta: { title: 'Technical Chart' }
      },
      {
        path: 'bandarmology/:ticker',
        name: 'Bandarmology',
        component: () => import('../views/BandarmologyPage.vue'),
        meta: { title: 'Bandarmology Analysis' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Update page title on route change
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - Market Intelligence` : 'Market Intelligence'
  next()
})

export default router
