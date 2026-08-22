import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsCloudArrowUp, BsCloudArrowDown, BsArrowClockwise, BsDownload, BsShieldCheck } from 'react-icons/bs'
import { backupAPI } from '../services/api'

export default function Backup() {
  const queryClient = useQueryClient()

  const { data: backups, isLoading } = useQuery({
    queryKey: ['backups'],
    queryFn: () => backupAPI.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (type) => backupAPI.create({ backup_type: type }),
    onSuccess: () => {
      toast.success('Backup created successfully!')
      queryClient.invalidateQueries({ queryKey: ['backups'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const restoreMutation = useMutation({
    mutationFn: (id) => backupAPI.restore(id),
    onSuccess: () => {
      toast.success('Backup restored successfully!')
      queryClient.invalidateQueries({ queryKey: ['backups'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleDownload = async (id) => {
    try {
      const res = await backupAPI.download(id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `backup_${id}.zip`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Backup downloaded')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const formatSize = (bytes) => {
    if (!bytes) return '—'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Backup & Restore</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Create and restore backups of your database and QR images</p>
      </div>

      {/* Create backup */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { type: 'full', label: 'Full Backup', desc: 'Database + QR Images', color: 'from-primary-500 to-primary-700' },
          { type: 'db', label: 'Database Only', desc: 'SQL dump of all tables', color: 'from-blue-500 to-blue-700' },
          { type: 'images', label: 'Images Only', desc: 'All generated QR images', color: 'from-green-500 to-green-700' },
        ].map((opt) => (
          <motion.div key={opt.type} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 text-center">
            <div className={`w-14 h-14 bg-gradient-to-br ${opt.color} rounded-xl flex items-center justify-center mx-auto mb-3`}>
              <BsCloudArrowUp className="text-white text-2xl" />
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{opt.label}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-4">{opt.desc}</p>
            <button onClick={() => createMutation.mutate(opt.type)}
              disabled={createMutation.isPending}
              className="btn-primary w-full">Create Backup</button>
          </motion.div>
        ))}
      </div>

      {/* Backup history */}
      <div className="glass-card overflow-hidden">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white p-6 pb-4">Backup History</h3>
        {isLoading ? (
          <p className="p-6 text-gray-400">Loading...</p>
        ) : backups?.length === 0 ? (
          <div className="p-12 text-center">
            <BsShieldCheck className="text-5xl text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No backups yet. Create one above!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="table-header">ID</th>
                  <th className="table-header">Type</th>
                  <th className="table-header">Size</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Date</th>
                  <th className="table-header">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {backups?.map((b) => (
                  <motion.tr key={b.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="table-cell">#{b.id}</td>
                    <td className="table-cell">
                      <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded text-xs font-medium">
                        {b.backup_type}
                      </span>
                    </td>
                    <td className="table-cell">{formatSize(b.file_size)}</td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        b.status === 'success' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                        'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300'
                      }`}>{b.status}</span>
                    </td>
                    <td className="table-cell text-xs">{b.created_at?.split('T')[0]}</td>
                    <td className="table-cell">
                      <div className="flex gap-1">
                        {b.file_path && (
                          <button onClick={() => handleDownload(b.id)} className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded" title="Download">
                            <BsDownload className="text-gray-600 dark:text-gray-300" />
                          </button>
                        )}
                        <button onClick={() => { if (confirm('Restore this backup? This will overwrite current data.')) restoreMutation.mutate(b.id) }}
                          className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded" title="Restore">
                          <BsArrowClockwise className="text-gray-600 dark:text-gray-300" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}