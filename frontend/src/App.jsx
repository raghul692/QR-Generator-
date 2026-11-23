import { useEffect } from 'react'
import { Routes, Route, useParams } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import Dashboard from './pages/Dashboard'
import Generator from './pages/Generator'
import DynamicQR from './pages/DynamicQR'
import Scanner from './pages/Scanner'
import History from './pages/History'
import Categories from './pages/Categories'
import BulkGenerator from './pages/BulkGenerator'
import Analytics from './pages/Analytics'
import Export from './pages/Export'
import Backup from './pages/Backup'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'

function DynamicRedirectFallback() {
  const { shortCode } = useParams()
  useEffect(() => {
    if (shortCode) {
      const rawBase = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').trim()
      const cleanBase = rawBase.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '')
      window.location.replace(`${cleanBase}/r/${shortCode}`)
    }
  }, [shortCode])

  return (
    <div className="flex items-center justify-center min-h-[50vh]">
      <div className="text-center p-8 glass-card max-w-sm">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-3"></div>
        <p className="text-gray-700 dark:text-gray-200 font-medium">Resolving QR destination...</p>
        <p className="text-xs text-gray-400 mt-1">Routing through dynamic redirect service</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/generator" element={<Generator />} />
        <Route path="/dynamic" element={<DynamicQR />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/history" element={<History />} />
        <Route path="/categories" element={<Categories />} />
        <Route path="/bulk" element={<BulkGenerator />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/export" element={<Export />} />
        <Route path="/backup" element={<Backup />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/r/:shortCode" element={<DynamicRedirectFallback />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}