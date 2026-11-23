import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BsBroadcast,
  BsPlusLg,
  BsCheckCircleFill,
  BsExclamationTriangleFill,
  BsPlayFill,
  BsTrash,
  BsCopy,
  BsX,
  BsClockHistory,
  BsCodeSquare,
} from 'react-icons/bs'
import { webhookAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

const ALL_EVENTS = [
  { key: 'scan.created', label: 'Scan Recorded (scan.created)', desc: 'Fires when a dynamic QR is scanned' },
  { key: 'qr.limit_reached', label: 'Scan Limit Reached (qr.limit_reached)', desc: 'Fires when max_scans threshold is reached' },
  { key: 'qr.expired', label: 'QR Expired (qr.expired)', desc: 'Fires when an active QR reaches expires_at' },
]

export default function Webhooks() {
  const { currentWorkspace } = useAuth()
  const [webhooks, setWebhooks] = useState([])
  const [selectedWebhook, setSelectedWebhook] = useState(null)
  const [deliveries, setDeliveries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copiedKey, setCopiedKey] = useState('')
  const [testingId, setTestingId] = useState(null)

  // Modal
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [targetUrl, setTargetUrl] = useState('')
  const [selectedEvents, setSelectedEvents] = useState(['scan.created', 'qr.limit_reached'])
  const [createdWebhook, setCreatedWebhook] = useState(null)

  const fetchWebhooks = async () => {
    try {
      setLoading(true)
      const res = await webhookAPI.list()
      setWebhooks(res.data || [])
    } catch (err) {
      setError(err.message || 'Failed to fetch webhooks')
    } finally {
      setLoading(false)
    }
  }

  const loadDeliveries = async (subId) => {
    try {
      const res = await webhookAPI.getDeliveries(subId)
      setDeliveries(res.data || [])
    } catch (err) {
      console.error('Failed to load delivery logs:', err)
    }
  }

  useEffect(() => {
    fetchWebhooks()
  }, [currentWorkspace])

  const handleSelectWebhook = (sub) => {
    setSelectedWebhook(sub)
    loadDeliveries(sub.id)
  }

  const handleToggleEvent = (evKey) => {
    if (selectedEvents.includes(evKey)) {
      setSelectedEvents(selectedEvents.filter((k) => k !== evKey))
    } else {
      setSelectedEvents([...selectedEvents, evKey])
    }
  }

  const handleCreateWebhook = async (e) => {
    e.preventDefault()
    if (!targetUrl.trim() || selectedEvents.length === 0) return
    try {
      const res = await webhookAPI.create({
        target_url: targetUrl.trim(),
        events: selectedEvents.join(','),
      })
      setCreatedWebhook(res.data)
      setTargetUrl('')
      fetchWebhooks()
    } catch (err) {
      alert(err.message || 'Failed to register webhook')
    }
  }

  const handleTestPing = async (subId) => {
    setTestingId(subId)
    try {
      const res = await webhookAPI.test(subId)
      alert(`Test ping dispatched! Response status: ${res.data.result?.status_code || 'Delivered'}`)
      loadDeliveries(subId)
    } catch (err) {
      alert(err.message || 'Failed to dispatch test ping')
    } finally {
      setTestingId(null)
    }
  }

  const handleDeleteWebhook = async (subId) => {
    if (!confirm('Are you sure you want to remove this webhook endpoint?')) return
    try {
      await webhookAPI.delete(subId)
      if (selectedWebhook?.id === subId) {
        setSelectedWebhook(null)
        setDeliveries([])
      }
      fetchWebhooks()
    } catch (err) {
      alert(err.message || 'Failed to delete webhook')
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
            <BsBroadcast className="text-indigo-600 dark:text-indigo-400" />
            Real-Time Webhooks & HMAC Signatures
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Stream scan events and lifecycle notifications to your servers with cryptographic HMAC-SHA256 signatures.
          </p>
        </div>
        <button
          onClick={() => {
            setCreatedWebhook(null)
            setShowCreateModal(true)
          }}
          className="btn-primary flex items-center gap-2 text-sm self-start sm:self-auto"
        >
          <BsPlusLg />
          <span>Add Webhook</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-sm text-red-600 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Main Grid: Endpoints list on left, Delivery logs on right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Endpoints List */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 space-y-3">
          <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2">
            Subscribed Endpoints ({webhooks.length})
          </h2>

          {webhooks.length === 0 && !loading && (
            <p className="text-xs text-gray-400 p-4 text-center">
              No webhook endpoints configured yet.
            </p>
          )}

          <div className="space-y-2">
            {webhooks.map((sub) => {
              const isSelected = selectedWebhook?.id === sub.id
              return (
                <div
                  key={sub.id}
                  onClick={() => handleSelectWebhook(sub)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                    isSelected
                      ? 'border-indigo-600 bg-indigo-50/40 dark:bg-indigo-950/30 dark:border-indigo-500'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-xs font-mono font-bold text-gray-900 dark:text-white truncate">
                      {sub.target_url}
                    </p>
                    <span
                      className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                        sub.is_active
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-300'
                      }`}
                    >
                      {sub.is_active ? 'Active' : 'Paused'}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1 mt-2">
                    {sub.events.map((ev) => (
                      <span
                        key={ev}
                        className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-mono"
                      >
                        {ev}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between mt-3 pt-2 border-t border-gray-100 dark:border-gray-700/60 text-[11px] text-gray-400">
                    <span>Last: {sub.last_status_code ? `HTTP ${sub.last_status_code}` : 'Never'}</span>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleTestPing(sub.id)
                        }}
                        disabled={testingId === sub.id}
                        className="p-1 hover:text-indigo-600 dark:hover:text-indigo-400 rounded"
                        title="Send Test Ping"
                      >
                        <BsPlayFill className="text-base" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteWebhook(sub.id)
                        }}
                        className="p-1 hover:text-red-600 rounded"
                        title="Delete Webhook"
                      >
                        <BsTrash className="text-xs" />
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Selected Webhook Deliveries & Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedWebhook ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-gray-200 dark:border-gray-700">
                <div>
                  <h2 className="text-base font-bold text-gray-900 dark:text-white font-mono break-all">
                    {selectedWebhook.target_url}
                  </h2>
                  <p className="text-xs text-gray-400 mt-0.5">
                    Workspace: <span className="font-mono">{selectedWebhook.workspace_id}</span> • HMAC SHA-256 Signed
                  </p>
                </div>
                <button
                  onClick={() => handleTestPing(selectedWebhook.id)}
                  disabled={testingId === selectedWebhook.id}
                  className="btn-primary text-xs px-3.5 py-1.5 flex items-center gap-1.5 self-start sm:self-auto"
                >
                  <BsPlayFill />
                  <span>{testingId === selectedWebhook.id ? 'Sending...' : 'Send Test Ping'}</span>
                </button>
              </div>

              {/* Delivery Logs Table */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                  <BsClockHistory /> Delivery Attempts ({deliveries.length})
                </h3>

                {deliveries.length === 0 ? (
                  <p className="text-xs text-gray-400 py-6 text-center">
                    No events dispatched yet for this endpoint. Trigger a test ping or scan a dynamic QR code.
                  </p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-gray-200 dark:border-gray-700 text-gray-400 uppercase">
                          <th className="py-2 px-3">Status</th>
                          <th className="py-2 px-3">Event</th>
                          <th className="py-2 px-3">Latency</th>
                          <th className="py-2 px-3">Timestamp</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100 dark:divide-gray-700/60 font-mono">
                        {deliveries.map((del) => {
                          const isSuccess = del.response_status && del.response_status >= 200 && del.response_status < 300
                          return (
                            <tr key={del.id} className="hover:bg-gray-50/50 dark:hover:bg-gray-700/30">
                              <td className="py-2.5 px-3">
                                <span
                                  className={`px-2 py-0.5 rounded font-bold ${
                                    isSuccess
                                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300'
                                      : 'bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-300'
                                  }`}
                                >
                                  {del.response_status ? `HTTP ${del.response_status}` : 'ERR'}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-gray-700 dark:text-gray-200">
                                {del.event_type}
                              </td>
                              <td className="py-2.5 px-3 text-gray-500">
                                {del.execution_duration_ms ? `${del.execution_duration_ms}ms` : '—'}
                              </td>
                              <td className="py-2.5 px-3 text-gray-400">
                                {del.delivered_at ? del.delivered_at.replace('T', ' ').slice(0, 19) : '—'}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
              <BsBroadcast className="text-3xl text-gray-300 dark:text-gray-600 mx-auto mb-2" />
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Select an endpoint from the left or create a new webhook subscription.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Modal: Create Webhook */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full p-6 border border-gray-200 dark:border-gray-700 shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                {createdWebhook ? 'Webhook Created Successfully' : 'Add Webhook Subscription'}
              </h3>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">
                <BsX className="text-2xl" />
              </button>
            </div>

            {createdWebhook ? (
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700 text-amber-900 dark:text-amber-200 text-xs">
                  <p className="font-bold mb-1">🔐 Webhook Signing Secret</p>
                  <p className="mb-2">Copy this secret key to verify the <code className="font-mono">X-QRMaster-Signature</code> header on incoming requests.</p>
                  <div className="flex items-center gap-2 bg-white dark:bg-gray-900 p-2 rounded-lg border border-amber-200 dark:border-amber-800 font-mono text-xs">
                    <span className="flex-1 truncate select-all">{createdWebhook.secret}</span>
                    <button
                      onClick={() => copyToClipboard(createdWebhook.secret, 'secret')}
                      className="text-indigo-600 dark:text-indigo-400 font-bold hover:underline"
                    >
                      {copiedKey === 'secret' ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <p className="mt-2 text-[11px] text-amber-700 dark:text-amber-400 font-medium">
                    This secret key will not be shown again!
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="w-full btn-primary text-sm py-2"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleCreateWebhook} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Destination Webhook URL
                  </label>
                  <input
                    type="url"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    placeholder="https://api.yourdomain.com/qrmaster-webhooks"
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none font-mono"
                    required
                  />
                  <p className="text-[11px] text-gray-400 mt-1">
                    Must be a publicly accessible HTTPS endpoint. Internal IPs and loopback addresses are blocked.
                  </p>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Events to Stream
                  </label>
                  <div className="space-y-2">
                    {ALL_EVENTS.map((ev) => {
                      const checked = selectedEvents.includes(ev.key)
                      return (
                        <label
                          key={ev.key}
                          className="flex items-start gap-2.5 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50/50 dark:hover:bg-gray-750 cursor-pointer text-xs"
                        >
                          <input
                            type="checkbox"
                            checked={checked}
                            onChange={() => handleToggleEvent(ev.key)}
                            className="mt-0.5 rounded text-indigo-600 focus:ring-indigo-500"
                          />
                          <div>
                            <p className="font-semibold text-gray-900 dark:text-white">{ev.label}</p>
                            <p className="text-gray-400 text-[11px]">{ev.desc}</p>
                          </div>
                        </label>
                      )
                    })}
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary text-sm px-4 py-2">
                    Register Webhook
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
