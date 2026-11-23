import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsLightningCharge, BsSearch, BsPlusLg, BsPencil, BsTrash, BsBoxArrowUpRight,
  BsCopy, BsLock, BsUnlock, BsEye, BsClockHistory, BsCheckCircle, BsXCircle,
} from 'react-icons/bs'
import { dynamicAPI } from '../services/api'

export default function DynamicQR() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [analyticsItem, setAnalyticsItem] = useState(null)

  // Form states
  const [createForm, setCreateForm] = useState({
    title: '',
    target_url: '',
    password: '',
    expires_at: '',
  })

  const [editForm, setEditForm] = useState({
    title: '',
    target_url: '',
    is_active: true,
    password: '',
    expires_at: '',
  })

  // Queries
  const { data: dynamicQRs = [], isLoading } = useQuery({
    queryKey: ['dynamic-qrs'],
    queryFn: () => dynamicAPI.list().then((r) => r.data),
  })

  const { data: selectedAnalytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['dynamic-analytics', analyticsItem?.id],
    queryFn: () => dynamicAPI.getAnalytics(analyticsItem.id).then((r) => r.data),
    enabled: Boolean(analyticsItem?.id),
  })

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data) => dynamicAPI.create(data),
    onSuccess: (res) => {
      toast.success(`Dynamic QR created! Short code: ${res.data.short_code}`)
      queryClient.invalidateQueries({ queryKey: ['dynamic-qrs'] })
      setShowCreateModal(false)
      setCreateForm({ title: '', target_url: '', password: '', expires_at: '' })
    },
    onError: (err) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => dynamicAPI.update(id, data),
    onSuccess: () => {
      toast.success('Dynamic QR destination updated!')
      queryClient.invalidateQueries({ queryKey: ['dynamic-qrs'] })
      setEditingItem(null)
    },
    onError: (err) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => dynamicAPI.delete(id),
    onSuccess: () => {
      toast.success('Dynamic QR deleted')
      queryClient.invalidateQueries({ queryKey: ['dynamic-qrs'] })
    },
    onError: (err) => toast.error(err.message),
  })

  // Handlers
  const handleCopyLink = (url) => {
    navigator.clipboard.writeText(url)
    toast.success('Short link copied to clipboard!')
  }

  const handleOpenEdit = (item) => {
    setEditingItem(item)
    setEditForm({
      title: item.title,
      target_url: item.target_url,
      is_active: item.is_active,
      password: '',
      expires_at: item.expires_at ? item.expires_at.slice(0, 16) : '',
    })
  }

  const handleCreateSubmit = (e) => {
    e.preventDefault()
    if (!createForm.title.trim() || !createForm.target_url.trim()) {
      toast.error('Title and destination URL are required')
      return
    }
    createMutation.mutate({
      title: createForm.title.trim(),
      target_url: createForm.target_url.trim(),
      password: createForm.password ? createForm.password : undefined,
      expires_at: createForm.expires_at ? new Date(createForm.expires_at).toISOString() : undefined,
    })
  }

  const handleEditSubmit = (e) => {
    e.preventDefault()
    if (!editForm.target_url.trim()) {
      toast.error('Destination URL cannot be empty')
      return
    }
    updateMutation.mutate({
      id: editingItem.id,
      data: {
        title: editForm.title.trim(),
        target_url: editForm.target_url.trim(),
        is_active: editForm.is_active,
        password: editForm.password ? editForm.password : undefined,
        expires_at: editForm.expires_at ? new Date(editForm.expires_at).toISOString() : undefined,
      },
    })
  }

  // Filtered list
  const filtered = dynamicQRs.filter((item) => {
    const matchesSearch =
      item.title?.toLowerCase().includes(search.toLowerCase()) ||
      item.short_code?.toLowerCase().includes(search.toLowerCase()) ||
      item.target_url?.toLowerCase().includes(search.toLowerCase())

    if (!matchesSearch) return false

    if (statusFilter === 'active') return item.is_active && !item.is_expired
    if (statusFilter === 'inactive') return !item.is_active
    if (statusFilter === 'expired') return item.is_expired
    return true
  })

  const totalDynamic = dynamicQRs.length
  const activeCount = dynamicQRs.filter((d) => d.is_active && !d.is_expired).length
  const totalScans = dynamicQRs.reduce((acc, curr) => acc + (curr.scan_count || 0), 0)
  const expiredCount = dynamicQRs.filter((d) => d.is_expired).length

  return (
    <div className="space-y-6">
      {/* Page Title & Action */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsLightningCharge className="text-amber-500" /> Dynamic QR Codes
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Redirectable QR codes. Update your target destination anytime after printing, protect with passwords, and track live scan activity.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary text-sm flex items-center gap-2 self-start sm:self-auto"
        >
          <BsPlusLg /> New Dynamic QR
        </button>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-card p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Dynamic QRs</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{totalDynamic}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400">Active Campaigns</p>
          <p className="text-2xl font-bold text-emerald-600 mt-1">{activeCount}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400">Total Scans</p>
          <p className="text-2xl font-bold text-primary-600 mt-1">{totalScans}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400">Expired / Inactive</p>
          <p className="text-2xl font-bold text-rose-500 mt-1">{expiredCount}</p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="glass-card p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <BsSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by title, target URL, or short code..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field pl-10"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field sm:w-48"
          >
            <option value="all">All Statuses</option>
            <option value="active">Active Only</option>
            <option value="inactive">Inactive</option>
            <option value="expired">Expired</option>
          </select>
        </div>
      </div>

      {/* Dynamic QRs Table */}
      <div className="glass-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-sm">Loading dynamic QR codes...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center">
            <BsLightningCharge className="text-5xl text-gray-300 dark:text-gray-600 mx-auto mb-3" />
            <p className="text-gray-500">No dynamic QR codes found. Create your first campaign above!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="table-header">Title & Short Link</th>
                  <th className="table-header">Target Destination URL</th>
                  <th className="table-header">Scans</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Security</th>
                  <th className="table-header">Created</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filtered.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="table-cell">
                      <div className="font-semibold text-gray-900 dark:text-white">{item.title}</div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="font-mono text-xs px-2 py-0.5 rounded bg-primary-50 dark:bg-primary-900/40 text-primary-600 dark:text-primary-300 font-medium">
                          /r/{item.short_code}
                        </span>
                        <button
                          type="button"
                          onClick={() => handleCopyLink(item.redirect_url)}
                          className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-500"
                          title="Copy redirect URL"
                        >
                          <BsCopy className="text-xs" />
                        </button>
                      </div>
                    </td>
                    <td className="table-cell max-w-xs truncate">
                      <a
                        href={item.target_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary-600 hover:underline flex items-center gap-1.5 text-sm"
                        title={item.target_url}
                      >
                        <span className="truncate">{item.target_url}</span>
                        <BsBoxArrowUpRight className="text-xs flex-shrink-0" />
                      </a>
                    </td>
                    <td className="table-cell">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300">
                        {item.scan_count || 0} scans
                      </span>
                    </td>
                    <td className="table-cell">
                      {item.is_expired ? (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 flex items-center gap-1 w-fit">
                          <BsXCircle /> Expired
                        </span>
                      ) : item.is_active ? (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 flex items-center gap-1 w-fit">
                          <BsCheckCircle /> Active
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 w-fit">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="table-cell">
                      {item.has_password ? (
                        <span className="text-amber-500 flex items-center gap-1 text-xs" title="Password protected">
                          <BsLock /> PIN Protected
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">—</span>
                      )}
                    </td>
                    <td className="table-cell text-xs text-gray-500">
                      {item.created_at?.split('T')[0]}
                    </td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          type="button"
                          onClick={() => setAnalyticsItem(item)}
                          className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-600 dark:text-gray-300"
                          title="View Scan Telemetry"
                        >
                          <BsEye />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleOpenEdit(item)}
                          className="p-1.5 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded text-blue-600 dark:text-blue-400"
                          title="Edit Target Destination"
                        >
                          <BsPencil />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            if (confirm(`Delete dynamic QR "${item.title}"?`)) {
                              deleteMutation.mutate(item.id)
                            }
                          }}
                          className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-red-500"
                          title="Delete Dynamic QR"
                        >
                          <BsTrash />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Dynamic QR Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-lg w-full p-6 space-y-4"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Create New Dynamic QR</h3>
              <form onSubmit={handleCreateSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Campaign / QR Title *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Summer Promo Menu"
                    value={createForm.title}
                    onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Target Destination URL *
                  </label>
                  <input
                    type="url"
                    required
                    placeholder="https://example.com/summer-promo"
                    value={createForm.target_url}
                    onChange={(e) => setCreateForm({ ...createForm, target_url: e.target.value })}
                    className="input-field"
                  />
                  <p className="text-xs text-gray-400 mt-1">You can change this URL at any time later without reprinting the QR code.</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Access Password (Optional)
                    </label>
                    <input
                      type="password"
                      placeholder="PIN / Password"
                      value={createForm.password}
                      onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Expiration Date (Optional)
                    </label>
                    <input
                      type="datetime-local"
                      value={createForm.expires_at}
                      onChange={(e) => setCreateForm({ ...createForm, expires_at: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="btn-secondary text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending}
                    className="btn-primary text-sm"
                  >
                    {createMutation.isPending ? 'Creating...' : 'Create Dynamic QR'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Edit Target URL Modal */}
      <AnimatePresence>
        {editingItem && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-lg w-full p-6 space-y-4"
            >
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">Edit Dynamic Destination</h3>
              <p className="text-xs text-gray-500">Short code: <span className="font-mono font-bold text-primary-600">/r/{editingItem.short_code}</span></p>
              <form onSubmit={handleEditSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    required
                    value={editForm.title}
                    onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Target Destination URL *
                  </label>
                  <input
                    type="url"
                    required
                    value={editForm.target_url}
                    onChange={(e) => setEditForm({ ...editForm, target_url: e.target.value })}
                    className="input-field"
                  />
                  <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">Existing printed QR codes will immediately point to this new destination.</p>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="isActive"
                    checked={editForm.is_active}
                    onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                    className="w-4 h-4 rounded text-primary-600"
                  />
                  <label htmlFor="isActive" className="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                    Campaign is Active (Uncheck to temporarily pause redirects)
                  </label>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      New Password (Optional)
                    </label>
                    <input
                      type="password"
                      placeholder="Leave blank to keep unchanged"
                      value={editForm.password}
                      onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Expiration Date (Optional)
                    </label>
                    <input
                      type="datetime-local"
                      value={editForm.expires_at}
                      onChange={(e) => setEditForm({ ...editForm, expires_at: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setEditingItem(null)}
                    className="btn-secondary text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={updateMutation.isPending}
                    className="btn-primary text-sm"
                  >
                    {updateMutation.isPending ? 'Saving...' : 'Update Destination'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Analytics Modal */}
      <AnimatePresence>
        {analyticsItem && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-lg w-full p-6 space-y-4"
            >
              <div className="flex items-center justify-between border-b pb-3">
                <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <BsEye className="text-primary-600" /> Analytics for "{analyticsItem.title}"
                </h3>
                <button
                  onClick={() => setAnalyticsItem(null)}
                  className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  ✕
                </button>
              </div>

              {analyticsLoading ? (
                <div className="py-8 text-center text-gray-400">Loading scan telemetry...</div>
              ) : selectedAnalytics ? (
                <div className="space-y-4 text-sm">
                  <div className="grid grid-cols-2 gap-3 bg-gray-50 dark:bg-gray-800 p-4 rounded-xl">
                    <div>
                      <p className="text-xs text-gray-400">Total Scans</p>
                      <p className="text-xl font-bold text-primary-600">{selectedAnalytics.total_scans}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">Short Code</p>
                      <p className="text-sm font-mono font-semibold text-gray-800 dark:text-gray-200">
                        {selectedAnalytics.short_code}
                      </p>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Device Breakdown</h4>
                    {Object.keys(selectedAnalytics.device_distribution || {}).length === 0 ? (
                      <p className="text-xs text-gray-400">No device data yet.</p>
                    ) : (
                      <div className="space-y-1">
                        {Object.entries(selectedAnalytics.device_distribution).map(([dev, cnt]) => (
                          <div key={dev} className="flex justify-between text-xs py-1 border-b dark:border-gray-700">
                            <span>{dev}</span>
                            <span className="font-semibold">{cnt}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Recent Scans</h4>
                    {selectedAnalytics.recent_scans?.length === 0 ? (
                      <p className="text-xs text-gray-400">No scans recorded yet.</p>
                    ) : (
                      <div className="max-h-40 overflow-y-auto space-y-1.5 text-xs">
                        {selectedAnalytics.recent_scans?.map((s) => (
                          <div key={s.id} className="p-2 bg-gray-50 dark:bg-gray-800 rounded flex justify-between">
                            <div>
                              <p className="font-medium text-gray-800 dark:text-gray-200">{s.browser || 'Unknown'}</p>
                              <p className="text-gray-400 text-[10px]">{s.device_type} • IP: {s.ip_address || '—'}</p>
                            </div>
                            <span className="text-gray-400 text-[10px]">{s.scanned_at?.split('T')[0]}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-xs text-gray-400">No analytics available.</p>
              )}

              <div className="pt-2 text-right">
                <button
                  type="button"
                  onClick={() => setAnalyticsItem(null)}
                  className="btn-primary text-xs"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
