import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsUpload, BsDownload, BsLayers, BsFileEarmarkSpreadsheet,
  BsCheckCircleFill, BsClock, BsCloudArrowDown, BsFiletypeCsv
} from 'react-icons/bs'
import { bulkAPI, qrAPI } from '../services/api'

export default function BulkGenerator() {
  const queryClient = useQueryClient()
  const [qrType, setQrType] = useState('url')
  const [jobName, setJobName] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const { data: types = [] } = useQuery({
    queryKey: ['qr-types'],
    queryFn: () => qrAPI.getTypes().then((r) => r.data),
  })

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ['bulk-jobs'],
    queryFn: () => bulkAPI.list().then((r) => r.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (formData) => bulkAPI.upload(formData),
    onSuccess: (res) => {
      toast.success(`Batch completed: ${res.data.processed_rows}/${res.data.total_rows} QRs generated!`)
      queryClient.invalidateQueries({ queryKey: ['bulk-jobs'] })
    },
    onError: (err) => toast.error(err.response?.data?.detail || err.message || 'Bulk upload failed'),
  })

  const processFile = (file) => {
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('qr_type', qrType)
    formData.append('job_name', jobName || file.name.replace(/\.[^/.]+$/, ''))
    uploadMutation.mutate(formData)
  }

  const handleDownload = async (id, name) => {
    try {
      const res = await bulkAPI.download(id)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `bulk_${name || id}.zip`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Downloaded ZIP archive!')
    } catch (err) {
      toast.error('Failed to download ZIP file')
    }
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-white/[0.06]">
        <div>
          <h1 className="text-2xl lg:text-3xl font-black text-slate-900 dark:text-white tracking-tight flex items-center gap-2.5">
            Bulk QR <span className="text-primary-500 font-normal">Factory</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Batch-process hundreds of dynamic QR codes from CSV or Excel spreadsheets in seconds.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-accent-violet/10 text-accent-violet border border-accent-violet/20 flex items-center gap-1.5">
            <BsLayers />
            High-Throughput Batch Engine
          </span>
        </div>
      </div>

      {/* Upload & Config Studio */}
      <div className="glass-card p-6 space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Select Batch QR Type
            </label>
            <select
              value={qrType}
              onChange={(e) => setQrType(e.target.value)}
              className="input-field"
            >
              {types.map((t) => (
                <option key={t.key} value={t.key}>
                  {t.label} ({t.key.toUpperCase()})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Job / Campaign Name
            </label>
            <input
              type="text"
              value={jobName}
              onChange={(e) => setJobName(e.target.value)}
              placeholder="e.g. Q3 Conference Attendees, Product Labels"
              className="input-field"
            />
          </div>
        </div>

        {/* Drag & Drop Zone */}
        <label
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setIsDragging(false)
            const file = e.dataTransfer.files?.[0]
            if (file) processFile(file)
          }}
          className={`relative flex flex-col items-center justify-center border-2 border-dashed rounded-2xl p-10 cursor-pointer transition-all duration-300 ${
            isDragging
              ? 'border-primary-500 bg-primary-500/10 shadow-glow-sm'
              : 'border-slate-300 dark:border-white/[0.15] bg-slate-50/50 dark:bg-white/[0.01] hover:border-primary-500/60 hover:bg-slate-100/50 dark:hover:bg-white/[0.03]'
          }`}
        >
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-primary-600 to-accent-violet flex items-center justify-center text-white text-2xl shadow-md mb-3">
            <BsUpload />
          </div>
          <p className="text-sm font-bold text-slate-900 dark:text-white">
            Drag & drop your CSV or Excel file here
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Supports .CSV, .XLSX, and .XLS up to 10,000 rows
          </p>

          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(e) => processFile(e.target.files?.[0])}
            className="hidden"
          />

          {uploadMutation.isPending && (
            <div className="absolute inset-0 bg-white/80 dark:bg-obsidian-950/80 backdrop-blur-sm rounded-2xl flex items-center justify-center gap-3">
              <div className="w-6 h-6 rounded-full border-2 border-primary-500 border-t-transparent animate-spin" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                Generating Vector Batch & Archiving to ZIP...
              </span>
            </div>
          )}
        </label>
      </div>

      {/* Bulk Jobs Table */}
      <div className="glass-card overflow-hidden">
        <div className="p-5 border-b border-slate-200 dark:border-white/[0.06] flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BsFileEarmarkSpreadsheet className="text-primary-500" />
            Batch Generation History
          </h3>
          <span className="text-xs font-semibold text-slate-400">
            {jobs.length} Jobs Total
          </span>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <BsLayers className="text-3xl mx-auto mb-2 opacity-40" />
            <p className="text-sm font-medium">No bulk jobs run yet</p>
            <p className="text-xs text-slate-500 mt-1">Upload a CSV above to generate batch QR archives.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/[0.06] bg-slate-50/50 dark:bg-white/[0.01]">
                  <th className="table-header">Job Name</th>
                  <th className="table-header">Type</th>
                  <th className="table-header">Processed</th>
                  <th className="table-header">Status</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-white/[0.04]">
                {jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50/50 dark:hover:bg-white/[0.02] transition-colors">
                    <td className="table-cell font-semibold text-slate-900 dark:text-white">
                      {job.job_name}
                    </td>
                    <td className="table-cell uppercase font-mono text-xs text-primary-500">
                      {job.qr_type}
                    </td>
                    <td className="table-cell">
                      <span className="font-mono text-xs">
                        {job.processed_rows} / {job.total_rows}
                      </span>
                    </td>
                    <td className="table-cell">
                      <span className={`badge-pill ${
                        job.status === 'completed'
                          ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                      }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="table-cell text-right">
                      {job.status === 'completed' && (
                        <button
                          type="button"
                          onClick={() => handleDownload(job.id, job.job_name)}
                          className="btn-secondary py-1.5 px-3 text-xs font-semibold gap-1.5"
                        >
                          <BsDownload className="text-xs" />
                          <span>ZIP</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}