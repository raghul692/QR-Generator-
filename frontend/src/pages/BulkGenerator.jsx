import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsUpload, BsDownload, BsLayers, BsFileEarmark } from 'react-icons/bs'
import { bulkAPI, qrAPI } from '../services/api'

export default function BulkGenerator() {
  const queryClient = useQueryClient()
  const [qrType, setQrType] = useState('url')
  const [jobName, setJobName] = useState('')

  const { data: types } = useQuery({
    queryKey: ['qr-types'],
    queryFn: () => qrAPI.getTypes().then((r) => r.data),
  })

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['bulk-jobs'],
    queryFn: () => bulkAPI.list().then((r) => r.data),
  })

  const uploadMutation = useMutation({
    mutationFn: (formData) => bulkAPI.upload(formData),
    onSuccess: (res) => {
      toast.success(`Bulk job completed: ${res.data.processed_rows}/${res.data.total_rows} QR codes generated`)
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
    uploadMutation.mutate(formData)
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Bulk QR Generator</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Generate QR codes in bulk from CSV or Excel files</p>
      </div>

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
        <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-12 cursor-pointer hover:border-primary-500 transition-colors">
          <BsUpload className="text-4xl text-gray-400 mb-3" />
          <p className="text-gray-600 dark:text-gray-300 font-medium">Upload CSV or Excel file</p>
          <p className="text-sm text-gray-400 mt-1">Each row will generate one QR code</p>
          <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUpload} className="hidden" />
        </label>
        {uploadMutation.isPending && (
          <div className="flex items-center justify-center mt-4">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            <span className="ml-2 text-gray-500">Processing bulk job...</span>
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
                        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                      }`}>{job.status}</span>
                    </td>
                    <td className="table-cell text-xs">{job.created_at?.split('T')[0]}</td>
                    <td className="table-cell">
                      {job.zip_path && (
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