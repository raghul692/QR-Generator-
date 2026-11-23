import { useEffect, Suspense, lazy } from 'react'
import { Routes, Route, useParams } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'

// Route-level code-splitting with dynamic imports
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Generator = lazy(() => import('./pages/Generator'))
const DynamicQR = lazy(() => import('./pages/DynamicQR'))
const LandingPages = lazy(() => import('./pages/LandingPages'))
const VCardPlus = lazy(() => import('./pages/VCardPlus'))
const MenuBuilder = lazy(() => import('./pages/MenuBuilder'))
const LinkInBio = lazy(() => import('./pages/LinkInBio'))
const Scanner = lazy(() => import('./pages/Scanner'))
const History = lazy(() => import('./pages/History'))
const Categories = lazy(() => import('./pages/Categories'))
const BulkGenerator = lazy(() => import('./pages/BulkGenerator'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Export = lazy(() => import('./pages/Export'))
const Backup = lazy(() => import('./pages/Backup'))
const Settings = lazy(() => import('./pages/Settings'))
const Auth = lazy(() => import('./pages/Auth'))
const Workspaces = lazy(() => import('./pages/Workspaces'))
const CustomDomains = lazy(() => import('./pages/CustomDomains'))
const Webhooks = lazy(() => import('./pages/Webhooks'))
const DeveloperDocs = lazy(() => import('./pages/DeveloperDocs'))
const NotFound = lazy(() => import('./pages/NotFound'))

function RouteLoadingFallback() {
  return (
    <div className="flex items-center justify-center min-h-[45vh]" role="status" aria-label="Loading page">
      <div className="text-center p-6 glass-card max-w-xs w-full animate-pulse">
        <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"></div>
        <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mx-auto mb-2"></div>
        <div className="h-3 bg-slate-100 dark:bg-slate-800 rounded w-1/2 mx-auto"></div>
      </div>
    </div>
  )
}

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
        <Route
          path="/"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Dashboard />
            </Suspense>
          }
        />
        <Route
          path="/generator"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Generator />
            </Suspense>
          }
        />
        <Route
          path="/dynamic"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <DynamicQR />
            </Suspense>
          }
        />
        <Route
          path="/landing-pages"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <LandingPages />
            </Suspense>
          }
        />
        <Route
          path="/vcard-plus"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <VCardPlus />
            </Suspense>
          }
        />
        <Route
          path="/menu-builder"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <MenuBuilder />
            </Suspense>
          }
        />
        <Route
          path="/link-in-bio"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <LinkInBio />
            </Suspense>
          }
        />
        <Route
          path="/scanner"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Scanner />
            </Suspense>
          }
        />
        <Route
          path="/history"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <History />
            </Suspense>
          }
        />
        <Route
          path="/categories"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Categories />
            </Suspense>
          }
        />
        <Route
          path="/bulk"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <BulkGenerator />
            </Suspense>
          }
        />
        <Route
          path="/analytics"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Analytics />
            </Suspense>
          }
        />
        <Route
          path="/export"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Export />
            </Suspense>
          }
        />
        <Route
          path="/backup"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Backup />
            </Suspense>
          }
        />
        <Route
          path="/settings"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Settings />
            </Suspense>
          }
        />
        <Route
          path="/workspaces"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Workspaces />
            </Suspense>
          }
        />
        <Route
          path="/domains"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <CustomDomains />
            </Suspense>
          }
        />
        <Route
          path="/webhooks"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Webhooks />
            </Suspense>
          }
        />
        <Route
          path="/developers"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <DeveloperDocs />
            </Suspense>
          }
        />
        <Route
          path="/auth"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <Auth />
            </Suspense>
          }
        />
        <Route path="/r/:shortCode" element={<DynamicRedirectFallback />} />
        <Route
          path="*"
          element={
            <Suspense fallback={<RouteLoadingFallback />}>
              <NotFound />
            </Suspense>
          }
        />
      </Route>
    </Routes>
  )
}
