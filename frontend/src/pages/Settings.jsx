import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsGear, BsSave, BsPalette, BsQrCode, BsCloud, BsGlobe, BsShieldLock, BsClockHistory, BsCheckCircleFill } from 'react-icons/bs'
import { apiKeyAPI, settingsAPI, retentionAPI } from '../services/api'
import { BsKey, BsPlusLg, BsTrash } from 'react-icons/bs'
import { useTheme } from '../context/ThemeContext'

export default function Settings() {
  const queryClient = useQueryClient()
  const { theme, setTheme } = useTheme()
  const [localSettings, setLocalSettings] = useState({})
  const [newKeyName, setNewKeyName] = useState('')
  const [generatedKey, setGeneratedKey] = useState(null)

  const [retentionDays, setRetentionDays] = useState(90)
  const [purging, setPurging] = useState(false)

  const { data: retentionSummary, refetch: refetchRetention } = useQuery({
    queryKey: ['retention-summary'],
    queryFn: () => retentionAPI.getSummary().then((r) => r.data),
  })

  const handlePurgeLogs = async () => {
    if (!confirm(`Purge all scan logs older than ${retentionDays} days? This cannot be undone.`)) return
    setPurging(true)
    try {
      const res = await retentionAPI.purgeScanLogs(retentionDays)
      toast.success(`Purged ${res.data.deleted_count} scan logs older than ${retentionDays} days`)
      refetchRetention()
    } catch (err) {
      toast.error(err.message || 'Failed to purge scan logs')
    } finally {
      setPurging(false)
    }
  }

  const handleAnonymizeIPs = async () => {
    if (!confirm('Anonymize IP addresses older than 30 days for GDPR compliance?')) return
    try {
      const res = await retentionAPI.anonymizeIPs(30)
      toast.success(`Anonymized ${res.data.anonymized_count} IP addresses`)
      refetchRetention()
    } catch (err) {
      toast.error(err.message || 'Failed to anonymize IPs')
    }
  }

  const { data: apiKeys } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeyAPI.list().then((r) => r.data),
  })

  const createKeyMutation = useMutation({
    mutationFn: (data) => apiKeyAPI.create(data),
    onSuccess: (res) => {
      setGeneratedKey(res.data)
      setNewKeyName('')
      toast.success('Developer API Key generated!')
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const revokeKeyMutation = useMutation({
    mutationFn: (id) => apiKeyAPI.revoke(id),
    onSuccess: () => {
      toast.success('API Key revoked')
      queryClient.invalidateQueries({ queryKey: ['api-keys'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleCreateKey = (e) => {
    e.preventDefault()
    if (!newKeyName.trim()) {
      toast.error('Enter key description/name')
      return
    }
    createKeyMutation.mutate({ name: newKeyName, rate_limit: 100 })
  }

  const { data: settings } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsAPI.getDict().then((r) => r.data),
  })

  useEffect(() => {
    if (settings) {
      setLocalSettings(settings)
    }
  }, [settings])

  const updateMutation = useMutation({
    mutationFn: (settingsMap) => settingsAPI.bulkUpdate(settingsMap),
    onSuccess: () => {
      toast.success('Settings saved successfully!')
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleChange = (key, value) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    updateMutation.mutate(localSettings)
  }

  const handleThemeChange = (newTheme) => {
    setTheme(newTheme)
    handleChange('theme', newTheme)
  }

  const settingCategories = [
    { key: 'qr', label: 'QR Defaults', icon: BsQrCode, settings: ['default_qr_size', 'default_error_correction', 'default_foreground_color', 'default_background_color', 'default_margin', 'default_qr_style'] },
    { key: 'ui', label: 'Appearance', icon: BsPalette, settings: ['theme', 'language'] },
    { key: 'export', label: 'Export', icon: BsGear, settings: ['export_format'] },
    { key: 'backup', label: 'Backup', icon: BsCloud, settings: ['auto_backup_enabled', 'auto_backup_frequency'] },
  ]

  const getSettingLabel = (key) => {
    const labels = {
      default_qr_size: 'Default QR Size (px)',
      default_error_correction: 'Default Error Correction',
      default_foreground_color: 'Default Foreground Color',
      default_background_color: 'Default Background Color',
      default_margin: 'Default Margin',
      default_qr_style: 'Default QR Style',
      theme: 'Theme',
      language: 'Language',
      export_format: 'Default Export Format',
      auto_backup_enabled: 'Auto Backup Enabled',
      auto_backup_frequency: 'Auto Backup Frequency',
    }
    return labels[key] || key
  }

  const renderField = (key) => {
    const value = localSettings[key] || ''
    if (key.includes('color')) {
      return <input type="color" value={value} onChange={(e) => handleChange(key, e.target.value)} className="w-full h-10 rounded-lg cursor-pointer" />
    }
    if (key === 'theme') {
      return (
        <div className="flex gap-2">
          <button onClick={() => handleThemeChange('light')} className={`btn-secondary ${value === 'light' ? 'ring-2 ring-primary-500' : ''}`}>Light</button>
          <button onClick={() => handleThemeChange('dark')} className={`btn-secondary ${value === 'dark' ? 'ring-2 ring-primary-500' : ''}`}>Dark</button>
        </div>
      )
    }
    if (key === 'default_error_correction') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="L">L (7%)</option><option value="M">M (15%)</option>
          <option value="Q">Q (25%)</option><option value="H">H (30%)</option>
        </select>
      )
    }
    if (key === 'default_qr_style') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="square">Square</option><option value="rounded">Rounded</option>
          <option value="circular">Circular</option><option value="dots">Dots</option>
        </select>
      )
    }
    if (key === 'export_format') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="png">PNG</option><option value="jpg">JPG</option>
          <option value="svg">SVG</option><option value="pdf">PDF</option>
        </select>
      )
    }
    if (key === 'auto_backup_frequency') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option>
        </select>
      )
    }
    if (key === 'auto_backup_enabled') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="false">Disabled</option><option value="true">Enabled</option>
        </select>
      )
    }
    if (key === 'language') {
      return (
        <select value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field">
          <option value="en">English</option><option value="es">Spanish</option><option value="fr">French</option>
        </select>
      )
    }
    return <input type="text" value={value} onChange={(e) => handleChange(key, e.target.value)} className="input-field" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Configure your QRMaster Pro preferences & developer API access</p>
        </div>
        <button onClick={handleSave} disabled={updateMutation.isPending}
          className="btn-primary flex items-center gap-2">
          <BsSave /> Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {settingCategories.map((cat, i) => (
          <motion.div key={cat.key} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }} className="glass-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <cat.icon className="text-primary-600" /> {cat.label}
            </h3>
            <div className="space-y-4">
              {cat.settings.map((key) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {getSettingLabel(key)}
                  </label>
                  {renderField(key)}
                </div>
              ))}
            </div>
          </motion.div>
        ))}

        {/* Enterprise Data Retention & GDPR Panel */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
            <BsShieldLock className="text-primary-600" /> Enterprise Data Retention & GDPR Governance
          </h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
            Configure automated retention policies for scan logs and enforce GDPR Article 17 ("Right to Erasure") compliance.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-400">Total Scan Records</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {retentionSummary?.total_scan_logs?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-400">Records &gt; 90 Days</p>
              <p className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">
                {retentionSummary?.expired_scan_logs_90d?.toLocaleString() || 0}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-400">Oldest Scan Log</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white mt-2 truncate">
                {retentionSummary?.oldest_scan_at ? retentionSummary.oldest_scan_at.split('T')[0] : 'None recorded'}
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30 mb-4">
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                Scan Log Retention Window
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Automatically purge analytics events older than the designated threshold.
              </p>
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
              <select
                value={retentionDays}
                onChange={(e) => setRetentionDays(Number(e.target.value))}
                className="input-field py-1.5 text-sm"
              >
                <option value={30}>30 Days (Strict)</option>
                <option value={60}>60 Days</option>
                <option value={90}>90 Days (Enterprise Standard)</option>
                <option value={180}>180 Days</option>
                <option value={365}>365 Days (Annual)</option>
              </select>
              <button
                type="button"
                onClick={handlePurgeLogs}
                disabled={purging}
                className="btn-secondary text-xs px-3 py-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 border-red-200 dark:border-red-800 whitespace-nowrap"
              >
                {purging ? 'Purging...' : 'Run Purge Now'}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30">
            <div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                GDPR IP Address Anonymization
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                Zero-out or truncate stored client IP addresses older than 30 days.
              </p>
            </div>
            <button
              type="button"
              onClick={handleAnonymizeIPs}
              className="btn-secondary text-xs px-3.5 py-2 whitespace-nowrap"
            >
              Anonymize Stale IPs
            </button>
          </div>
        </motion.div>

        {/* Developer API Keys Panel */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <BsKey className="text-primary-600" /> Developer API Keys
          </h3>
          <p className="text-sm text-gray-500 mb-4">Generate API keys for programmatic QR generation via REST API (`X-API-Key` header).</p>

          <form onSubmit={handleCreateKey} className="flex gap-3 mb-6">
            <input
              type="text"
              placeholder="Key Name (e.g. Mobile App, E-Commerce Store)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="input-field flex-1"
            />
            <button type="submit" disabled={createKeyMutation.isPending} className="btn-primary flex items-center gap-2">
              <BsPlusLg /> Generate Key
            </button>
          </form>

          {generatedKey && (
            <div className="p-4 mb-6 bg-amber-50 dark:bg-amber-900/30 border border-amber-300 rounded-xl text-amber-900 dark:text-amber-200">
              <p className="font-semibold text-sm">🔑 Copy Your New API Key:</p>
              <code className="block bg-black/10 p-2 rounded text-xs font-mono my-2 select-all">{generatedKey.api_key}</code>
              <p className="text-xs text-amber-700 dark:text-amber-300">{generatedKey.warning}</p>
            </div>
          )}

          <div className="space-y-3">
            {apiKeys?.length === 0 ? (
              <p className="text-sm text-gray-400">No active API keys found.</p>
            ) : (
              apiKeys?.map((k) => (
                <div key={k.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-xl border">
                  <div>
                    <span className="font-semibold text-sm text-gray-900 dark:text-white">{k.name}</span>
                    <span className="ml-3 text-xs font-mono text-gray-500">{k.key_prefix}...</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-400">Created: {k.created_at?.split('T')[0]}</span>
                    <button onClick={() => { if (confirm('Revoke key?')) revokeKeyMutation.mutate(k.id) }} className="p-1.5 text-red-500 hover:bg-red-50 rounded">
                      <BsTrash />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}