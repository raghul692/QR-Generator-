import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsUpload, BsDownload, BsLayers, BsXCircle, BsCheckCircleFill, BsExclamationTriangleFill } from 'react-icons/bs'
import { bulkAPI, qrAPI } from '../services/api'

export default function BulkGenerator() {
  const queryClient = useQueryClient()
  const [qrType, setQrType] = useState('url')
  const [jobName, setJobName] = useState('')
  const [activeJob, setActiveJob] = useState(null)
  const eventSourceRef = useRef(null)

  const { data: types } = useQuery({
    queryKey: ['qr-types'],
    queryFn: () => qrAPI.getTypes().then((r) => r.data),
  })

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['bulk-jobs'],
    queryFn: () => bulkAPI.list().then((r) => r.data),
    refetchInterval: activeJob ? 3000 : false,
  })

  // SSE Stream Management
  useEffect(() => {
    if (!activeJob?.id || ['completed', 'completed_with_errors', 'failed', 'cancelled'].includes(activeJob.status)) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      return
    }

    const streamUrl = bulkAPI.getStreamUrl(activeJob.id)
    const es = new EventSource(streamUrl)
    eventSourceRef.current = es

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setActiveJob((prev) => ({
          ...prev,
          processed: data.processed,
          total: data.total,
          status: data.status,
          heartbeat: data.heartbeat,
          error_log: data.error_log,
        }))

        if (['completed', 'completed_with_errors', 'failed', 'cancelled'].includes(data.status)) {
          es.close()
          eventSourceRef.current = null
          queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
          if (data.status === 'completed') {
            toast.success(`Bulk job #${data.id} completed! (${data.processed}/${data.total} generated)`)
          } else if (data.status === 'completed_with_errors') {
            toast('Job completed with some skipped rows.', { icon: '⚠️' })
          } else if (data.status === 'cancelled') {
            toast('Bulk job cancelled.', { icon: '🛑' })
          } else {
            toast.error(`Bulk job failed: ${data.error_log || 'Unknown error'}`)
          }
        }
      } catch (err) {
        console.error('SSE parse error:', err)
      }
    }

    es.onerror = () => {
      // Fallback: close SSE if network/connection drops
      es.close()
      eventSourceRef.current = null
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
    }
  }, [activeJob?.id, activeJob?.status, queryClient])

  const uploadMutation = useMutation({
    mutationFn: (formData) => bulkAPI.upload(formData),
    onSuccess: (res) => {
      const data = res.data
      if (data.status === 'pending' || data.status === 'processing') {
        setActiveJob({
          id: data.id,
          status: data.status,
          processed: data.processed_rows || 0,
          total: data.total_rows || 1,
        })
        toast.success(`Job #${data.id} queued. Processing in background...`)
      } else {
        toast.success(`Bulk job completed: ${data.processed_rows}/${data.total_rows} generated`)
      }
      queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('qr_type', qrType)
    formData.append('job_name', jobName || file.name)
    formData.append('async_mode', 'true')
    uploadMutation.mutate(formData)
  }

  const handleCancel = async () => {
    if (!activeJob?.id) return
    try {
      await bulkAPI.cancel(activeJob.id)
      setActiveJob((prev) => (prev ? { ...prev, status: 'cancelled' } : null))
      toast('Cancellation requested.', { icon: '🛑' })
      queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
    } catch (err) {
      toast.error(`Cancel failed: ${err.message}`)
    }
  }

  const handleDownload = async (id) => {
    try {
      const res = await bulkAPI.download(id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `bulk_qr_${id}.zip`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Downloaded ZIP')
    } catch (err) {
      toast.error(err.message)
    }
  }

  const progressPercent = activeJob && activeJob.total > 0
    ? Math.min(100, Math.round((activeJob.processed / activeJob.total) * 100))
    : 0

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Bulk QR Generator</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Generate batch QR codes from CSV or Excel files with real-time SSE progress streaming.
        </p>
      </div>

      {/* Active Job Progress Card */}
      <AnimatePresence>
        {activeJob && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-5 rounded-2xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 backdrop-blur-md shadow-sm space-y-3"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="relative flex h-3 w-3">
                  {['pending', 'processing'].includes(activeJob.status) && (
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  )}
                  <span className={`relative inline-flex rounded-full h-3 w-3 ${
                    activeJob.status === 'completed' ? 'bg-emerald-500' :
                    activeJob.status === 'failed' ? 'bg-rose-500' :
                    activeJob.status === 'cancelled' ? 'bg-amber-500' :
                    'bg-indigo-600'
                  }`}></span>
                </span>
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 dark:text-white">
                    Bulk Job #{activeJob.id} — <span className="capitalize">{activeJob.status}</span>
                  </h4>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Processed {activeJob.processed || 0} of {activeJob.total || 0} QR codes ({progressPercent}%)
                  </p>
                </div>
              </div>

              {['pending', 'processing'].includes(activeJob.status) ? (
                <button
                  type="button"
                  onClick={handleCancel}
                  className="px-3 py-1.5 text-xs font-medium text-rose-700 bg-rose-100 hover:bg-rose-200 dark:text-rose-300 dark:bg-rose-900/40 rounded-lg transition-colors flex items-center gap-1.5 focus-visible:ring-2 focus-visible:ring-rose-500"
                >
                  <BsXCircle /> Cancel Job
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => setActiveJob(null)}
                  className="text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  Dismiss
                </button>
              )}
            </div>

            {/* Progress Track */}
            <div className="w-full bg-gray-200 dark:bg-gray-700 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-indigo-600 dark:bg-indigo-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${progressPercent}%` }}
              ></div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Upload */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Upload File</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">QR Type</label>
            <select value={qrType} onChange={(e) => setQrType(e.target.value)} className="input-field">
              {types?.map((t) => <option key={t.key} value={t.key}>{t.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Job Name (optional)</label>
            <input type="text" value={jobName} onChange={(e) => setJobName(e.target.value)}
              placeholder="e.g. Marketing Campaign" className="input-field" />
          </div>
        </div>
        <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-12 cursor-pointer hover:border-primary-500 transition-colors focus-within:ring-2 focus-within:ring-primary-500">
          <BsUpload className="text-4xl text-gray-400 mb-3" />
          <p className="text-gray-600 dark:text-gray-300 font-medium">Upload CSV or Excel file</p>
          <p className="text-sm text-gray-400 mt-1">Supports chunked processing (25/chunk) up to 15 MB</p>
          <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUpload} className="hidden" />
        </label>
        {uploadMutation.isPending && (
          <div className="flex items-center justify-center mt-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-2 text-gray-500">Initiating bulk job queue...</span>
          </div>
        )}
      </div>

      {/* Job history */}
      <div className="glass-card overflow-hidden">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white p-6 pb-4">Bulk Job History</h3>
        {isLoading ? (
          <p className="p-6 text-gray-400">Loading...</p>
        ) : jobs?.length === 0 ? (
          <div className="p-12 text-center">
            <BsLayers className="text-5xl text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No bulk jobs yet. Upload a file to get started!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="table-header">Job Name</th>
                  <th className="table-header">File</th>
                  <th className="table-header">Type</th>
                  <th className="table-header">Progress</th>
                  <th className="table-header">Status</th>
                  <th className="table-header">Date</th>
                  <th className="table-header">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {jobs?.map((job) => (
                  <motion.tr key={job.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="table-cell font-medium">{job.job_name}</td>
                    <td className="table-cell text-xs">{job.source_filename}</td>
                    <td className="table-cell">{job.qr_type}</td>
                    <td className="table-cell">{job.processed_rows}/{job.total_rows}</td>
                    <td className="table-cell">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        job.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300' :
                        job.status === 'failed' ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300' :
                        job.status === 'cancelled' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300' :
                        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                      }`}>{job.status}</span>
                    </td>
                    <td className="table-cell text-xs">{job.created_at?.split('T')[0]}</td>
                    <td className="table-cell">
                      {job.zip_path && job.status.startsWith('completed') && (
                        <button onClick={() => handleDownload(job.id)} className="btn-secondary text-xs flex items-center gap-1">
                          <BsDownload /> ZIP
                        </button>
                      )}
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
