import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BsShieldLock, BsQrCode, BsCheckCircleFill, BsPersonBadge, BsBuildingCheck } from 'react-icons/bs'
import { useAuth } from '../context/AuthContext'

export default function Auth() {
  const navigate = useNavigate()
  const { login, signup, demoLogin, user } = useAuth()
  const [tab, setTab] = useState('demo') // 'demo' | 'login' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) {
      setError('Please provide both email and password.')
      return
    }
    setError('')
    setLoading(true)
    try {
      if (tab === 'signup') {
        await signup(email, password)
      } else {
        await login(email, password)
      }
      navigate('/workspaces')
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.')
    } finally {
      setLoading(false)
    }
  }

  const handleDemoSelect = (roleKey) => {
    demoLogin(roleKey)
    navigate('/workspaces')
  }

  return (
    <div className="max-w-md mx-auto py-12 px-4 sm:px-6">
      <div className="text-center mb-8">
        <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-indigo-500/20">
          <BsQrCode className="text-white text-3xl" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">QRMaster Pro</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          SaaS Multi-Tenancy & Enterprise Identity
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {/* Navigation Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/50">
          <button
            onClick={() => setTab('demo')}
            className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === 'demo'
                ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400 bg-white dark:bg-gray-800'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            Enterprise Demo
          </button>
          <button
            onClick={() => setTab('login')}
            className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === 'login'
                ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400 bg-white dark:bg-gray-800'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setTab('signup')}
            className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors ${
              tab === 'signup'
                ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400 dark:border-indigo-400 bg-white dark:bg-gray-800'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
            }`}
          >
            Sign Up
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-300">
              {error}
            </div>
          )}

          {tab === 'demo' ? (
            <div className="space-y-4">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Select an enterprise role to test multi-tenancy and RBAC:
              </p>

              <button
                type="button"
                onClick={() => handleDemoSelect('admin')}
                className="w-full text-left p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-gray-800 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/20 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-900/50 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                    <BsBuildingCheck className="text-xl" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      Enterprise Admin (Owner)
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Full workspace CRUD, member management, DNS & billing
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2 py-0.5 rounded font-mono bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300">
                  Owner
                </span>
              </button>

              <button
                type="button"
                onClick={() => handleDemoSelect('marketing')}
                className="w-full text-left p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-gray-800 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/20 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-100 dark:bg-emerald-900/50 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                    <BsPersonBadge className="text-xl" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      Marketing Lead (Editor)
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Create/edit QR codes, campaigns, and landing pages
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2 py-0.5 rounded font-mono bg-emerald-100 dark:bg-emerald-900/60 text-emerald-700 dark:text-emerald-300">
                  Editor
                </span>
              </button>

              <button
                type="button"
                onClick={() => handleDemoSelect('auditor')}
                className="w-full text-left p-4 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-indigo-500 dark:hover:border-indigo-500 bg-white dark:bg-gray-800 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/20 transition-all flex items-center justify-between group"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center text-slate-600 dark:text-slate-300">
                    <BsShieldLock className="text-xl" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400">
                      Security Auditor (Viewer)
                    </h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Read-only audit access to scan logs & GDPR compliance
                    </p>
                  </div>
                </div>
                <span className="text-xs px-2 py-0.5 rounded font-mono bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  Viewer
                </span>
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@company.com"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm transition-colors disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : tab === 'signup' ? 'Create Account' : 'Sign In'}
              </button>
            </form>
          )}

          {user && (
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Logged in as <strong className="text-gray-900 dark:text-white">{user.email}</strong> ({user.role})
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
