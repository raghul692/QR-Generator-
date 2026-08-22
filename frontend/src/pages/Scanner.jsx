import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsCamera, BsUpload, BsCopy, BsBoxArrowUpRight, BsQrCodeScan } from 'react-icons/bs'
import { scannerAPI } from '../services/api'

export default function Scanner() {
  const [scanResults, setScanResults] = useState([])
  const [scanning, setScanning] = useState(false)

  const scanMutation = useMutation({
    mutationFn: (file) => scannerAPI.scan(file),
    onSuccess: (res) => {
      setScanResults(res.data.results)
      if (res.data.count > 0) {
        toast.success(`Found ${res.data.count} QR code(s)!`)
      } else {
        toast.error('No QR codes found in the image')
      }
      setScanning(false)
    },
    onError: (err) => {
      toast.error(err.message)
      setScanning(false)
    },
  })

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setScanning(true)
    scanMutation.mutate(file)
  }

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }

  const handleOpenUrl = (url) => {
    if (url.startsWith('http')) {
      window.open(url, '_blank')
    } else {
      toast.error('This is not a URL')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">QR Code Scanner</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Scan QR codes from images or use your camera</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload area */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Upload Image</h3>
          <label className="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-12 cursor-pointer hover:border-primary-500 transition-colors">
            <BsUpload className="text-4xl text-gray-400 mb-3" />
            <p className="text-gray-600 dark:text-gray-300 font-medium">Click to upload an image</p>
            <p className="text-sm text-gray-400 mt-1">PNG, JPG, etc.</p>
            <input type="file" accept="image/*" onChange={handleFileUpload} className="hidden" />
          </label>
          {scanning && (
            <div className="flex items-center justify-center mt-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <span className="ml-2 text-gray-500">Scanning...</span>
            </div>
          )}
        </div>

        {/* Camera info */}
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Camera Scanner</h3>
          <div className="flex flex-col items-center justify-center p-12 text-center">
            <BsCamera className="text-4xl text-gray-400 mb-3" />
            <p className="text-gray-600 dark:text-gray-300 font-medium mb-2">Live Camera Scanner</p>
            <p className="text-sm text-gray-400 mb-4">Use your device camera to scan QR codes in real-time</p>
            <p className="text-xs text-gray-400">Camera access requires HTTPS or localhost</p>
          </div>
        </div>
      </div>

      {/* Results */}
      {scanResults.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <BsQrCodeScan /> Scan Results ({scanResults.length})
          </h3>
          <div className="space-y-3">
            {scanResults.map((result, i) => (
              <div key={i} className="flex items-center justify-between bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-400 mb-1">Type: {result.qr_type}</p>
                  <p className="text-sm text-gray-900 dark:text-white font-mono break-all">{result.data}</p>
                </div>
                <div className="flex gap-2 ml-4">
                  <button onClick={() => handleCopy(result.data)} className="btn-secondary text-xs" title="Copy">
                    <BsCopy />
                  </button>
                  {result.data.startsWith('http') && (
                    <button onClick={() => handleOpenUrl(result.data)} className="btn-primary text-xs" title="Open URL">
                      <BsBoxArrowUpRight />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  )
}