import { useState, useEffect, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsCamera, BsUpload, BsCopy, BsBoxArrowUpRight, BsQrCodeScan, BsStopCircle } from 'react-icons/bs'
import { Html5Qrcode } from 'html5-qrcode'
import { scannerAPI } from '../services/api'

export default function Scanner() {
  const [scanResults, setScanResults] = useState([])
  const [scanning, setScanning] = useState(false)
  const [cameraActive, setCameraActive] = useState(false)
  const html5QrCodeRef = useRef(null)

  const classifyText = (text) => {
    const t = text.trim().toLowerCase()
    if (t.startsWith('http://') || t.startsWith('https://')) return 'url'
    if (t.startsWith('mailto:')) return 'email'
    if (t.startsWith('tel:')) return 'phone'
    if (t.startsWith('smsto:')) return 'sms'
    if (t.startsWith('wifi:')) return 'wifi'
    if (t.startsWith('begin:vcard')) return 'vcard'
    if (t.startsWith('upi://')) return 'upi'
    if (t.startsWith('geo:')) return 'geo'
    return 'text'
  }

  const startCamera = async () => {
    try {
      const qrScanner = new Html5Qrcode('camera-reader')
      html5QrCodeRef.current = qrScanner
      await qrScanner.start(
        { facingMode: 'environment' },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        (decodedText) => {
          toast.success('QR Code detected via Camera!')
          setScanResults((prev) => [
            { data: decodedText, qr_type: classifyText(decodedText) },
            ...prev,
          ])
          stopCamera()
        },
        () => {
          // Frame decode error - expected while scanning empty frames
        }
      )
      setCameraActive(true)
    } catch (err) {
      toast.error('Could not access camera: ' + (err.message || 'Check camera permissions'))
      setCameraActive(false)
    }
  }

  const stopCamera = async () => {
    if (html5QrCodeRef.current && cameraActive) {
      try {
        await html5QrCodeRef.current.stop()
        html5QrCodeRef.current.clear()
      } catch (err) {
        console.warn('Camera stop error:', err)
      }
      setCameraActive(false)
    }
  }

  useEffect(() => {
    return () => {
      if (html5QrCodeRef.current && html5QrCodeRef.current.isScanning) {
        html5QrCodeRef.current.stop().catch(console.error)
      }
    }
  }, [])

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

        {/* Live Camera Scanner */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              <BsCamera /> Live Camera Scanner
            </h3>
            {cameraActive ? (
              <button
                type="button"
                onClick={stopCamera}
                className="btn-secondary text-xs flex items-center gap-1.5 text-red-500 border-red-300"
              >
                <BsStopCircle /> Stop Camera
              </button>
            ) : (
              <button
                type="button"
                onClick={startCamera}
                className="btn-primary text-xs flex items-center gap-1.5"
              >
                <BsCamera /> Start Camera
              </button>
            )}
          </div>

          <div
            id="camera-reader"
            className={`w-full max-w-sm mx-auto overflow-hidden rounded-xl bg-gray-950 ${
              cameraActive ? 'min-h-[280px]' : 'h-48 flex flex-col items-center justify-center text-center p-6'
            }`}
          >
            {!cameraActive && (
              <div className="text-gray-400 space-y-2">
                <BsCamera className="text-4xl mx-auto text-gray-500" />
                <p className="text-sm font-medium text-gray-300">Camera is idle</p>
                <p className="text-xs text-gray-500">Click "Start Camera" above to scan live QR codes directly from your device camera.</p>
              </div>
            )}
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