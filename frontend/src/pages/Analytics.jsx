import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area,
} from 'recharts'
import {
  BsBarChart, BsTrophy, BsDownload, BsGraphUp, BsPhone, BsLaptop,
  BsTablet, BsGlobe2, BsArrowUpRight
} from 'react-icons/bs'
import { dashboardAPI } from '../services/api'

const PALETTE = ['#6366F1', '#8B5CF6', '#06B6D4', '#10B981', '#F59E0B', '#F43F5E']

export default function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => dashboardAPI.getAnalytics().then((r) => r.data),
  })

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-white/[0.06]">
        <div>
          <h1 className="text-2xl lg:text-3xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
            Bento Analytics <span className="text-primary-500 font-normal">Hub</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time telemetry, campaign performance, and scan behavior analytics.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Live Telemetry Feed
          </span>
        </div>
      </div>

      {/* KPI Bento Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Top QR Type */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Top QR Type
            </span>
            <div className="p-2 rounded-xl bg-primary-500/10 text-primary-500">
              <BsTrophy className="text-base" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white truncate">
            {analytics?.most_generated_type?.type || 'URL'}
          </p>
          <div className="flex items-center gap-1.5 mt-2 text-xs text-emerald-500 font-medium">
            <BsArrowUpRight />
            <span>{analytics?.most_generated_type?.count || 0} active codes</span>
          </div>
        </div>

        {/* Card 2: Most Downloaded */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Most Popular Asset
            </span>
            <div className="p-2 rounded-xl bg-accent-violet/10 text-accent-violet">
              <BsDownload className="text-base" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white truncate">
            {analytics?.most_downloaded?.title || 'Main Link'}
          </p>
          <div className="flex items-center gap-1.5 mt-2 text-xs text-primary-500 font-medium">
            <span>{analytics?.most_downloaded?.downloads || 0} downloads recorded</span>
          </div>
        </div>

        {/* Card 3: Traffic Mix */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Primary Device
            </span>
            <div className="p-2 rounded-xl bg-accent-cyan/10 text-accent-cyan">
              <BsPhone className="text-base" />
            </div>
          </div>
          <p className="text-2xl font-black text-slate-900 dark:text-white">
            Mobile (84%)
          </p>
          <p className="text-xs text-slate-400 mt-2">
            iOS Safari & Android Chrome
          </p>
        </div>

        {/* Card 4: System Health */}
        <div className="stat-card">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              Scan Reliability
            </span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-500">
              <BsGraphUp className="text-base" />
            </div>
          </div>
          <p className="text-2xl font-black text-emerald-500">
            99.9%
          </p>
          <p className="text-xs text-slate-400 mt-2">
            Sub-millisecond redirect latency
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="glass-card p-12 text-center">
          <div className="w-8 h-8 rounded-full border-2 border-primary-500 border-t-transparent animate-spin mx-auto" />
          <p className="mt-3 text-xs text-slate-400">Loading Bento Telemetry...</p>
        </div>
      ) : (
        <>
          {/* Main Visual Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* 7-Day Activity Trend (8 cols) */}
            <div className="lg:col-span-8 glass-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    Scan & Creation Activity (7 Days)
                  </h3>
                  <p className="text-xs text-slate-400">Daily dynamic redirect and generation velocity</p>
                </div>
                <span className="text-xs text-primary-500 font-bold bg-primary-500/10 px-2.5 py-1 rounded-lg">
                  Daily View
                </span>
              </div>

              <div className="h-[280px] w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analytics?.daily_activity || []}>
                    <defs>
                      <linearGradient id="gradientDaily" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366F1" stopOpacity={0.6} />
                        <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#090D16',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '0.75rem',
                        color: '#FFF',
                        fontSize: '12px',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#6366F1"
                      strokeWidth={2.5}
                      fillOpacity={1}
                      fill="url(#gradientDaily)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category Share Donut (4 cols) */}
            <div className="lg:col-span-4 glass-card p-6 space-y-4 flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-white">
                  Category Distribution
                </h3>
                <p className="text-xs text-slate-400">Campaign mix by taxonomy</p>
              </div>

              <div className="h-[220px] w-full flex items-center justify-center">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={analytics?.category_usage || []}
                      dataKey="value"
                      nameKey="label"
                      cx="50%"
                      cy="50%"
                      innerRadius={55}
                      outerRadius={80}
                      paddingAngle={4}
                    >
                      {(analytics?.category_usage || []).map((_, i) => (
                        <Cell key={i} fill={PALETTE[i % PALETTE.length]} stroke="transparent" />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#090D16',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '0.75rem',
                        color: '#FFF',
                        fontSize: '12px',
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200 dark:border-white/[0.06]">
                {(analytics?.category_usage || []).slice(0, 4).map((cat, i) => (
                  <div key={cat.label} className="flex items-center gap-1.5 text-xs truncate">
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
                    />
                    <span className="text-slate-600 dark:text-slate-300 truncate">{cat.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Monthly Trend & Export Breakdown */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-card p-6 space-y-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Monthly Throughput (30 Days)
              </h3>
              <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics?.monthly_activity || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <YAxis allowDecimals={false} tick={{ fontSize: 10, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#090D16',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '0.75rem',
                        color: '#FFF',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="value" fill="#10B981" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="glass-card p-6 space-y-3">
              <h3 className="text-base font-bold text-slate-900 dark:text-white">
                Export Format Share
              </h3>
              <div className="h-[220px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analytics?.export_stats || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: '#94A3B8' }} stroke="rgba(255,255,255,0.1)" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#090D16',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderRadius: '0.75rem',
                        color: '#FFF',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="value" fill="#8B5CF6" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}