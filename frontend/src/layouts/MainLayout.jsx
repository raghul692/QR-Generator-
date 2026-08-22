import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BsGrid1X2, BsQrCode, BsClockHistory, BsCamera, BsLayers,
  BsBarChart, BsGear, BsCloudArrowDown, BsFolder, BsMoon, BsSun,
  BsList, BsX, BsQrCodeScan,
} from 'react-icons/bs'
import { useTheme } from '../redux/ThemeContext'

const navItems = [
  { to: '/', icon: BsGrid1X2, label: 'Dashboard' },
  { to: '/generator', icon: BsQrCode, label: 'QR Generator' },
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
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
              <BsQrCode className="text-white text-2xl" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">QRMaster</h1>
              <p className="text-xs text-primary-600 dark:text-primary-400 font-medium">Pro</p>
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
              <item.icon className="text-xl" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top navbar */}
        <header className="sticky top-0 z-20 bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between px-4 lg:px-8 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-600 dark:text-gray-300"
              >
                <BsList className="text-2xl" />
              </button>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white hidden sm:block">
                Enterprise QR Code Platform
              </h2>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="p-2.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title="Toggle theme"
              >
                {theme === 'light' ? <BsMoon className="text-xl" /> : <BsSun className="text-xl" />}
              </button>
              <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                Q
              </div>
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