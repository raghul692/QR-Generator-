import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BsGrid1X2, BsQrCode, BsClockHistory, BsLayers,
  BsBarChart, BsGear, BsCloudArrowDown, BsFolder, BsMoonStars, BsSun,
  BsList, BsX, BsQrCodeScan, BsShieldLock, BsStars
} from 'react-icons/bs'
import { useTheme } from '../redux/ThemeContext'

const NAV_GROUPS = [
  {
    title: 'Core Studio',
    items: [
      { to: '/', icon: BsGrid1X2, label: 'Dashboard' },
      { to: '/generator', icon: BsQrCode, label: 'QR Studio 2.0', badge: 'NEW' },
      { to: '/scanner', icon: BsQrCodeScan, label: 'AI Scanner' },
      { to: '/history', icon: BsClockHistory, label: 'QR Archive' },
    ],
  },
  {
    title: 'Batch & Operations',
    items: [
      { to: '/categories', icon: BsFolder, label: 'Categories' },
      { to: '/bulk', icon: BsLayers, label: 'Bulk Generator' },
      { to: '/analytics', icon: BsBarChart, label: 'Bento Analytics' },
      { to: '/export', icon: BsCloudArrowDown, label: 'Exports & Stickers' },
    ],
  },
  {
    title: 'System & Security',
    items: [
      { to: '/backup', icon: BsShieldLock, label: 'Cloud Backups' },
      { to: '/settings', icon: BsGear, label: 'Settings & API Keys' },
    ],
  },
]

export default function MainLayout() {
  const { theme, toggleTheme } = useTheme()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#060910] text-slate-900 dark:text-slate-100 flex transition-colors duration-300">
      {/* Mobile Drawer Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Modern Collapsible Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen w-64 bg-white/95 dark:bg-[#090D16]/95 backdrop-blur-xl border-r border-slate-200 dark:border-white/[0.08] z-40 transform transition-transform duration-300 flex flex-col ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-200 dark:border-white/[0.08]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary-600 via-indigo-600 to-accent-violet flex items-center justify-center shadow-md shadow-primary-500/30 text-white font-black text-xl">
              <BsQrCode />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="text-base font-extrabold tracking-tight text-slate-900 dark:text-white">
                  QRMaster
                </h1>
                <span className="text-[10px] bg-gradient-to-r from-primary-600 to-accent-violet text-white px-1.5 py-0.2 rounded font-black tracking-wider uppercase">
                  PRO
                </span>
              </div>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium">
                Enterprise Studio
              </p>
            </div>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-slate-400 hover:text-white"
          >
            <BsX className="text-2xl" />
          </button>
        </div>

        {/* Navigation Groupings */}
        <nav className="flex-1 p-3.5 space-y-6 overflow-y-auto">
          {NAV_GROUPS.map((group) => (
            <div key={group.title} className="space-y-1">
              <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest px-3 block mb-1.5">
                {group.title}
              </span>
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === '/'}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `nav-link ${isActive ? 'nav-link-active' : ''}`
                  }
                >
                  <item.icon className="text-base flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto text-[9px] font-extrabold bg-primary-500/20 text-primary-600 dark:text-primary-300 px-1.5 py-0.5 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* Sidebar Footer Info */}
        <div className="p-4 border-t border-slate-200 dark:border-white/[0.08] bg-slate-50/50 dark:bg-white/[0.01]">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500 text-xs font-bold">
              ✓
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
                Engine Active
              </p>
              <p className="text-[10px] text-slate-400 truncate">
                FastAPI • 60fps Vector Sync
              </p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Navbar */}
        <header className="sticky top-0 z-20 bg-white/80 dark:bg-[#060910]/80 backdrop-blur-xl border-b border-slate-200 dark:border-white/[0.08]">
          <div className="flex items-center justify-between px-4 lg:px-8 py-3.5">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/[0.06]"
              >
                <BsList className="text-xl" />
              </button>

              <div className="hidden sm:flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                  Global Vector Network
                </span>
              </div>
            </div>

            {/* Quick Actions & Dual Theme Switcher */}
            <div className="flex items-center gap-3">
              <NavLink
                to="/generator"
                className="btn-primary text-xs py-1.5 px-3.5 shadow-none"
              >
                <BsStars className="text-xs" />
                <span>New QR</span>
              </NavLink>

              <button
                onClick={toggleTheme}
                className="p-2 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-100 dark:bg-white/[0.04] text-slate-700 dark:text-slate-300 hover:border-primary-500/50 hover:bg-slate-200 dark:hover:bg-white/[0.08] transition-all"
                title={`Switch to ${theme === 'light' ? 'Dark Velvet' : 'Crisp Light'} mode`}
              >
                {theme === 'light' ? (
                  <BsMoonStars className="text-base text-primary-600" />
                ) : (
                  <BsSun className="text-base text-accent-amber" />
                )}
              </button>

              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary-600 to-indigo-700 flex items-center justify-center text-white font-bold text-xs shadow-inner">
                R
              </div>
            </div>
          </div>
        </header>

        {/* Dynamic Page Outlet with Fade Animation */}
        <main className="flex-1 p-4 lg:p-8 overflow-x-hidden">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}