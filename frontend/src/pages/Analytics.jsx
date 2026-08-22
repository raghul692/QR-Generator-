import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area,
} from 'recharts'
import { BsBarChart, BsTrophy, BsDownload, BsGraphUp } from 'react-icons/bs'
import { dashboardAPI } from '../services/api'

const COLORS = ['#6366F1', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981', '#06B6D4', '#84CC16', '#EF4444']

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => dashboardAPI.getAnalytics().then((r) => r.data),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Detailed insights into your QR code usage</p>
      </div>

      {/* Top stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center">
              <BsTrophy className="text-white text-2xl" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Most Generated Type</h3>
              {analytics?.most_generated_type ? (
                <p className="text-2xl font-bold text-primary-600">{analytics.most_generated_type.type}</p>
              ) : <p className="text-gray-400">No data</p>}
            </div>
          </div>
          {analytics?.most_generated_type && (
            <p className="text-sm text-gray-500">{analytics.most_generated_type.count} QR codes generated</p>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-700 rounded-xl flex items-center justify-center">
              <BsDownload className="text-white text-2xl" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white">Most Downloaded</h3>
              {analytics?.most_downloaded ? (
                <p className="text-2xl font-bold text-green-600">{analytics.most_downloaded.title}</p>
              ) : <p className="text-gray-400">No data</p>}
            </div>
          </div>
          {analytics?.most_downloaded && (
            <p className="text-sm text-gray-500">{analytics.most_downloaded.downloads} downloads</p>
          )}
        </motion.div>
      </div>

      {isLoading ? (
        <div className="glass-card p-12 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-2 text-gray-400">Loading analytics...</p>
        </div>
      ) : (
        <>
          {/* Activity charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Daily Activity (7 days)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={analytics?.daily_activity || []}>
                  <defs>
                    <linearGradient id="colorDaily" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366F1" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Area type="monotone" dataKey="value" stroke="#6366F1" fillOpacity={1} fill="url(#colorDaily)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Weekly Activity (14 days)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={analytics?.weekly_activity || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Line type="monotone" dataKey="value" stroke="#8B5CF6" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Monthly Activity (30 days)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={analytics?.monthly_activity || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="label" tick={{ fontSize: 10 }} />
                  <YAxis allowDecimals={false} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#10B981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Category Usage</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie data={analytics?.category_usage || []} dataKey="value" nameKey="label"
                    cx="50%" cy="50%" outerRadius={90} label={(e) => e.label}>
                    {(analytics?.category_usage || []).map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Export stats */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Export Statistics</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={analytics?.export_stats || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#F59E0B" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}