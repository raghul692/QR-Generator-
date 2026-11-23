import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BsGlobe2,
  BsPlusLg,
  BsCheckCircleFill,
  BsHourglassSplit,
  BsShieldCheck,
  BsTrash,
  BsArrowRepeat,
  BsInfoCircle,
  BsX,
  BsCopy,
} from 'react-icons/bs'
import { domainAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

export default function CustomDomains() {
  const { currentWorkspace } = useAuth()
  const [domains, setDomains] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [verifyingId, setVerifyingId] = useState(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [newDomain, setNewDomain] = useState('')
  const [copiedKey, setCopiedKey] = useState('')

  const fetchDomains = async () => {
    try {
      setLoading(true)
      const res = await domainAPI.list()
      setDomains(res.data.domains || [])
    } catch (err) {
      setError(err.message || 'Failed to fetch custom domains')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDomains()
  }, [currentWorkspace])

  const handleAddDomain = async (e) => {
    e.preventDefault()
    if (!newDomain.trim()) return
    try {
      await domainAPI.create({ domain: newDomain.trim() })
      setNewDomain('')
      setShowAddModal(false)
      fetchDomains()
    } catch (err) {
      alert(err.message || 'Failed to register domain')
    }
  }

  const handleVerifyDomain = async (domainId) => {
    setVerifyingId(domainId)
    try {
      const res = await domainAPI.verify(domainId)
      alert(res.data.message || 'Domain verified successfully!')
      fetchDomains()
    } catch (err) {
      alert(err.message || 'Verification check failed. Please check DNS records.')
    } finally {
      setVerifyingId(null)
    }
  }

  const handleDeleteDomain = async (domainId, domainName) => {
    if (!confirm(`Are you sure you want to remove custom domain '${domainName}'?`)) return
    try {
      await domainAPI.delete(domainId)
      fetchDomains()
    } catch (err) {
      alert(err.message || 'Failed to remove domain')
    }
  }

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text)
    setCopiedKey(key)
    setTimeout(() => setCopiedKey(''), 2000)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsGlobe2 className="text-indigo-600 dark:text-indigo-400" />
            Custom Branded Domains (CNAME)
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            White-label your dynamic QR links with custom branded subdomains and automated SSL certificates.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2 text-sm self-start sm:self-auto"
        >
          <BsPlusLg />
          <span>Add Custom Domain</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Domain Cards */}
      <div className="space-y-4">
        {domains.length === 0 && !loading && (
          <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center max-w-lg mx-auto">
            <div className="w-12 h-12 rounded-full bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto mb-3">
              <BsGlobe2 className="text-2xl" />
            </div>
            <h3 className="text-base font-bold text-gray-900 dark:text-white mb-1">
              No Custom Domains Registered
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Connect your brand domain (e.g., <code className="font-mono">qr.yourbrand.com</code>) to deliver branded QR redirect experiences.
            </p>
            <button onClick={() => setShowAddModal(true)} className="btn-primary text-xs px-4 py-2">
              Connect First Domain
            </button>
          </div>
        )}

        {domains.map((d) => {
          const isVerified = d.status === 'verified'
          return (
            <div
              key={d.id}
              className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-4 shadow-sm"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                    <BsGlobe2 className="text-xl" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white font-mono">
                      https://{d.domain}
                    </h2>
                    <p className="text-xs text-gray-400">
                      Workspace: <span className="font-mono">{d.workspace_id}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1 ${
                      isVerified
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                        : 'bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-300'
                    }`}
                  >
                    {isVerified ? <BsCheckCircleFill /> : <BsHourglassSplit />}
                    {d.status.toUpperCase()}
                  </span>

                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-medium flex items-center gap-1 ${
                      d.ssl_status === 'active'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-300'
                        : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                    }`}
                  >
                    <BsShieldCheck /> SSL: {d.ssl_status.toUpperCase()}
                  </span>

                  <button
                    onClick={() => handleDeleteDomain(d.id, d.domain)}
                    className="text-red-500 hover:text-red-700 dark:hover:text-red-400 p-2 rounded-lg"
                    title="Remove domain"
                  >
                    <BsTrash className="text-base" />
                  </button>
                </div>
              </div>

              {/* DNS Instructions Card */}
              <div className="bg-gray-50 dark:bg-gray-900/60 rounded-xl p-4 space-y-3">
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                  <BsInfoCircle /> Required DNS Configuration Records
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                  {/* CNAME */}
                  <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between text-gray-400 mb-1">
                      <span className="font-semibold text-gray-700 dark:text-gray-300">1. CNAME Routing</span>
                      <button
                        onClick={() => copyToClipboard(d.dns_instructions.cname_target, `cname-${d.id}`)}
                        className="text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        <BsCopy /> {copiedKey === `cname-${d.id}` ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <p className="text-gray-500">Host: <code className="font-mono text-gray-800 dark:text-gray-200">{d.dns_instructions.cname_host}</code></p>
                    <p className="text-gray-500">Points to: <code className="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{d.dns_instructions.cname_target}</code></p>
                  </div>

                  {/* TXT Challenge */}
                  <div className="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between text-gray-400 mb-1">
                      <span className="font-semibold text-gray-700 dark:text-gray-300">2. TXT Challenge</span>
                      <button
                        onClick={() => copyToClipboard(d.dns_instructions.txt_value, `txt-${d.id}`)}
                        className="text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1"
                      >
                        <BsCopy /> {copiedKey === `txt-${d.id}` ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <p className="text-gray-500">Host: <code className="font-mono text-gray-800 dark:text-gray-200">{d.dns_instructions.txt_host}</code></p>
                    <p className="text-gray-500 truncate">Value: <code className="font-mono text-indigo-600 dark:text-indigo-400">{d.dns_instructions.txt_value}</code></p>
                  </div>
                </div>

                {!isVerified && (
                  <div className="flex items-center justify-between pt-2">
                    <p className="text-xs text-amber-600 dark:text-amber-400">
                      DNS propagation may take a few minutes after adding records at your DNS registrar.
                    </p>
                    <button
                      onClick={() => handleVerifyDomain(d.id)}
                      disabled={verifyingId === d.id}
                      className="btn-primary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
                    >
                      <BsArrowRepeat className={verifyingId === d.id ? 'animate-spin' : ''} />
                      <span>{verifyingId === d.id ? 'Checking DNS...' : 'Verify DNS Now'}</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Modal: Add Domain */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full p-6 border border-gray-200 dark:border-gray-700 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Add Custom Domain</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-gray-600">
                <BsX className="text-2xl" />
              </button>
            </div>
            <form onSubmit={handleAddDomain} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Custom Domain or Subdomain
                </label>
                <input
                  type="text"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  placeholder="e.g. qr.yourbrand.com or links.company.org"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none font-mono"
                  required
                />
                <p className="text-[11px] text-gray-400 mt-1">
                  We recommend using a dedicated subdomain such as <code className="font-mono">qr.yourbrand.com</code>.
                </p>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary text-sm px-4 py-2">
                  Register Domain
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
