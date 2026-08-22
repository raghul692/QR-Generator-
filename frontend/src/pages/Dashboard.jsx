import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  BsQrCode, BsClock, BsDownload, BsFolder, BsLayers, BsStar,
} from 'react-icons/bs'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts'
import { dashboardAPI } from '../services/api'
import { Link } from 'react-router-dom'

const COLORS = ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4', '#84CC16', '#EF4444']

const statIcons = {
  total_qr: BsQrCode,
  today_qr: BsClock,
  total_downloads: BsDownload,
  total_categories: BsFolder,
  total_bulk_jobs: BsLayers,
  favorites: BsStar,
}

const statLabels = {
  total_qr: 'Total QR Codes',
  today_qr: "Today's QR Codes",
  total_downloads: 'Total Downloads',
  total_categories: 'Categories',
  total_bulk_jobs: 'Bulk Jobs',
  favorites: 'Favorites',
}

const statColors = {
  total_qr: 'from-primary-500 to-primary-700',
  today_qr: 'from-green-500 to-green-700',
  total_downloads: 'from-blue-500 to-blue-700',
  total_categories: 'from-purple-500 to-purple-700',
  total_bulk_jobs: 'from-orange-500 to-orange-700',
  favorites: 'from-pink-500 to-pink-700',
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardAPI.getStats().then((r) => r.data),
  })

  const { data: charts } = useQuery({
    queryKey: ['dashboard-charts'],
    queryFn: () => dashboardAPI.getCharts().then((r) => r.data),
  })

  const statKeys = ['total_qr', 'today_qr', 'total_downloads', 'total_categories', 'total_bulk_jobs', 'favorites']

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Welcome to QRMaster Pro — your QR code management overview</p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {statKeys.map((key, i) => {
          const Icon = statIcons[key]
          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="stat-card"
            >
              <div className={`w-12 h-12 bg-gradient-to-br ${statColors[key]} rounded-xl flex items-center justify-center mb-3`}>
                <Icon className="text-white text-2xl" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {statsLoading ? '...' : stats?.[key] ?? 0}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{statLabels[key]}</p>
            </motion.div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* QR Type Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">QR Type Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={charts?.qr_type_distribution || []}
                dataKey="value"
                nameKey="label"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={(entry) => entry.label}
              >
                {(charts?.qr_type_distribution || []).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Daily Generation */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Daily Generation (7 days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts?.daily_generation || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#6366F1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Category Distribution */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Category Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={charts?.category_distribution || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" allowDecimals={false} />
              <YAxis dataKey="label" type="category" tick={{ fontSize: 11 }} width={80} />
              <Tooltip />
              <Bar dataKey="value" fill="#8B5CF6" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Download Trends */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Download Trends (7 days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={charts?.download_trends || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#10B981" strokeWidth={3} dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick actions */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Link to="/generator" className="btn-primary text-center">Generate QR</Link>
          <Link to="/scanner" className="btn-secondary text-center">Scan QR</Link>
          <Link to="/bulk" className="btn-secondary text-center">Bulk Generate</Link>
          <Link to="/history" className="btn-secondary text-center">View History</Link>
        </div>
      </div>
    </div>
  )
}