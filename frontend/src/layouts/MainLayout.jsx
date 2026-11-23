import { useState } from 'react'
import { NavLink, Link, Outlet } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BsGrid1X2, BsQrCode, BsClockHistory, BsCamera, BsLayers,
  BsBarChart, BsGear, BsCloudArrowDown, BsFolder, BsMoon, BsSun,
  BsList, BsX, BsQrCodeScan, BsLightningCharge,
  BsLayoutTextWindowReverse, BsCupHot, BsPersonVcard, BsLink,
  BsBuilding, BsGlobe, BsShieldLock, BsBroadcast, BsCodeSlash,
} from 'react-icons/bs'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { to: '/', icon: BsGrid1X2, label: 'Dashboard' },
  { to: '/generator', icon: BsQrCode, label: 'QR Generator' },
  { to: '/dynamic', icon: BsLightningCharge, label: 'Dynamic QRs' },
  { to: '/workspaces', icon: BsBuilding, label: 'Workspaces & Team' },
  { to: '/domains', icon: BsGlobe, label: 'Custom Domains' },
  { to: '/webhooks', icon: BsBroadcast, label: 'Webhooks' },
  { to: '/developers', icon: BsCodeSlash, label: 'Developer APIs' },
  { to: '/landing-pages', icon: BsLayoutTextWindowReverse, label: 'Landing Pages' },
  { to: '/vcard-plus', icon: BsPersonVcard, label: 'vCard Plus' },
  { to: '/menu-builder', icon: BsCupHot, label: 'Digital Menu' },
  { to: '/link-in-bio', icon: BsLink, label: 'Link in Bio' },
  { to: '/scanner', icon: BsQrCodeScan, label: 'QR Scanner' },
  { to: '/history', icon: BsClockHistory, label: 'History' },
  { to: '/categories', icon: BsFolder, label: 'Categories' },
  { to: '/bulk', icon: BsLayers, label: 'Bulk Generator' },
  { to: '/analytics', icon: BsBarChart, label: 'Analytics' },
  { to: '/export', icon: BsCloudArrowDown, label: 'Export' },
  { to: '/backup', icon: BsCloudArrowDown, label: 'Backup & Restore' },
  { to: '/settings', icon: BsGear, label: 'Settings' },
]

export default function MainLayout() {
  const { theme, toggleTheme } = useTheme()
  const { user, currentWorkspace } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-40 transform transition-transform duration-300 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-md shadow-primary-500/20">
              <BsQrCode className="text-white text-2xl" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white leading-tight">QRMaster</h1>
              <p className="text-xs text-primary-600 dark:text-primary-400 font-medium">Enterprise SaaS</p>
            </div>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-gray-500">
            <BsX className="text-2xl" />
          </button>
        </div>

        <nav className="p-4 space-y-1 overflow-y-auto h-[calc(100vh-100px)]">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `nav-link ${isActive ? 'nav-link-active' : ''}`
              }
            >
              <item.icon className="text-xl flex-shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top navbar */}
        <header className="sticky top-0 z-20 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between px-4 lg:px-8 py-3.5">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden min-w-[44px] min-h-[44px] flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white rounded-lg p-2 focus-visible:ring-2 focus-visible:ring-primary-500"
                aria-label="Open navigation menu"
              >
                <BsList className="text-2xl" />
              </button>

              {/* Active Workspace Pill */}
              <Link
                to="/workspaces"
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750 hover:border-indigo-400 dark:hover:border-indigo-500 transition-colors text-xs"
                title="Switch Workspace"
              >
                <BsBuilding className="text-indigo-600 dark:text-indigo-400" />
                <span className="font-semibold text-gray-900 dark:text-white max-w-[120px] sm:max-w-none truncate">
                  {currentWorkspace === 'ws_legacy_default' ? 'Default Workspace' : currentWorkspace}
                </span>
                <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">
                  RLS
                </span>
              </Link>
            </div>

            <div className="flex items-center gap-3">
              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className="min-w-[40px] min-h-[40px] flex items-center justify-center rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors focus-visible:ring-2 focus-visible:ring-primary-500"
                aria-label="Toggle dark/light theme"
                title="Toggle theme"
              >
                {theme === 'light' ? <BsMoon className="text-lg" /> : <BsSun className="text-lg" />}
              </button>

              {/* User Identity / Auth Link */}
              <Link
                to="/auth"
                className="flex items-center gap-2 p-1.5 sm:px-3 sm:py-1.5 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-500 transition-colors text-xs"
                title="Account & Auth"
              >
                <div className="w-7 h-7 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-lg flex items-center justify-center text-white font-bold text-xs">
                  {user?.role ? user.role[0].toUpperCase() : 'U'}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="font-medium text-gray-900 dark:text-white leading-tight truncate max-w-[120px]">
                    {user?.email || 'Sign In'}
                  </p>
                  <p className="text-[10px] text-gray-400 capitalize">
                    {user?.role || 'Guest'}
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-8 overflow-x-hidden">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}
