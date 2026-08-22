import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsFileEarmarkSpreadsheet, BsFileEarmarkText, BsFileEarmarkPdf, BsDownload } from 'react-icons/bs'
import { exportAPI } from '../services/api'

const exportOptions = [
  { format: 'csv', label: 'CSV Report', icon: BsFileEarmarkText, desc: 'Comma-separated values for spreadsheets', color: 'from-green-500 to-green-700' },
  { format: 'excel', label: 'Excel Report', icon: BsFileEarmarkSpreadsheet, desc: 'Formatted Excel spreadsheet (.xlsx)', color: 'from-blue-500 to-blue-700' },
  { format: 'pdf', label: 'PDF Report', icon: BsFileEarmarkPdf, desc: 'Professional PDF report with statistics', color: 'from-red-500 to-red-700' },
]

export default function Export() {
  const exportMutation = useMutation({
    mutationFn: async (format) => {
      const apiMap = { csv: exportAPI.csv, excel: exportAPI.excel, pdf: exportAPI.pdf }
      const res = await apiMap[format]()
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      const ext = format === 'excel' ? 'xlsx' : format
      a.download = `qr_history_report.${ext}`
      a.click()
      window.URL.revokeObjectURL(url)
    },
    onSuccess: () => toast.success('Report exported successfully!'),
    onError: (err) => toast.error(err.message),
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Export</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Export your QR history data in various formats</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {exportOptions.map((opt, i) => (
          <motion.div
            key={opt.format}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-6 text-center"
          >
            <div className={`w-16 h-16 bg-gradient-to-br ${opt.color} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
              <opt.icon className="text-white text-3xl" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{opt.label}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">{opt.desc}</p>
            <button
              onClick={() => exportMutation.mutate(opt.format)}
              disabled={exportMutation.isPending}
              className="btn-primary w-full flex items-center justify-center gap-2"
            >
              <BsDownload /> Export
            </button>
          </motion.div>
        ))}
      </div>

      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Export Information</h3>
        <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-2">
          <li>• Reports include all QR history records with title, type, downloads, and dates</li>
          <li>• PDF reports include summary statistics and a formatted table</li>
          <li>• CSV/Excel files are compatible with all major spreadsheet applications</li>
          <li>• Exports are generated in real-time from your current database</li>
        </ul>
      </div>
    </div>
  )
}