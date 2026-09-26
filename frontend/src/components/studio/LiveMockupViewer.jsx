import { useEffect, useRef, useState } from 'react'
import QRCodeStyling from 'qr-code-styling'
import {
  BsEye, BsDownload, BsPhone, BsGrid, BsCreditCard2Front,
  BsShare, BsCheck2, BsFiles, BsFileEarmarkPdf, BsQrCode
} from 'react-icons/bs'
import toast from 'react-hot-toast'

export default function LiveMockupViewer({
  value = 'https://qrmaster.pro',
  title = 'My QR Code',
  customization = {},
  onSave,
  isSaving = false,
  savedId = null,
  onDownloadBackend,
}) {
  const [activeMockup, setActiveMockup] = useState('canvas') // 'canvas', 'phone', 'table', 'card'
  const qrRef = useRef(null)
  const qrCodeInstance = useRef(null)
  const [copied, setCopied] = useState(false)

  // Initialize or update QRCodeStyling
  useEffect(() => {
    const isGradient = customization.gradient_enabled
    const dotsColor = customization.foreground_color || '#000000'
    const bgColor = customization.transparent_background ? 'transparent' : (customization.background_color || '#FFFFFF')

    const options = {
      width: 280,
      height: 280,
      data: value || 'https://qrmaster.pro',
      margin: customization.margin || 4,
      qrOptions: {
        typeNumber: 0,
        mode: 'Byte',
        errorCorrectionLevel: customization.error_correction || 'H',
      },
      imageOptions: {
        hideBackgroundDots: true,
        imageSize: (customization.logo_size || 25) / 100,
        margin: 4,
        crossOrigin: 'anonymous',
      },
      dotsOptions: {
        type: customization.dotsType || 'dots',
        color: isGradient ? undefined : dotsColor,
        gradient: isGradient
          ? {
              type: 'linear',
              rotation: 45,
              colorStops: [
                { offset: 0, color: customization.gradient_start || '#6366F1' },
                { offset: 1, color: customization.gradient_end || '#8B5CF6' },
              ],
            }
          : undefined,
      },
      backgroundOptions: {
        color: bgColor,
      },
      cornersSquareOptions: {
        type: customization.cornerSquareType || 'extra-rounded',
        color: customization.cornerSquareColor || dotsColor,
      },
      cornersDotOptions: {
        type: customization.cornerDotType || 'dot',
        color: customization.cornerDotColor || dotsColor,
      },
    }

    if (customization.logo_url) {
      options.image = customization.logo_url
    }

    if (!qrCodeInstance.current) {
      qrCodeInstance.current = new QRCodeStyling(options)
      if (qrRef.current) {
        qrRef.current.innerHTML = ''
        qrCodeInstance.current.append(qrRef.current)
      }
    } else {
      qrCodeInstance.current.update(options)
    }
  }, [value, customization])

  // Direct client-side download helper
  const handleClientDownload = (extension) => {
    if (!qrCodeInstance.current) return
    const safeTitle = (title || 'qr_code').toLowerCase().replace(/\s+/g, '_')
    qrCodeInstance.current.download({
      name: `${safeTitle}`,
      extension: extension,
    })
    toast.success(`Downloaded as ${extension.toUpperCase()}`)
  }

  // Copy raw image data to clipboard
  const handleCopyImage = async () => {
    if (!qrCodeInstance.current) return
    try {
      const rawData = await qrCodeInstance.current.getRawData('png')
      const blob = new Blob([rawData], { type: 'image/png' })
      await navigator.clipboard.write([
        new ClipboardItem({ 'image/png': blob })
      ])
      setCopied(true)
      toast.success('QR Code copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast.error('Failed to copy. Please download instead.')
    }
  }

  return (
    <div className="space-y-4">
      {/* Mockup Switcher Header */}
      <div className="glass-card p-4 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BsEye className="text-primary-500" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Live Real-World Preview
            </h3>
          </div>
          <span className="text-[10px] bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 px-2 py-0.5 rounded-full font-bold">
            60 FPS Live Sync
          </span>
        </div>

        {/* View Selection Pills */}
        <div className="grid grid-cols-4 gap-1 p-1 rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.06]">
          {[
            { id: 'canvas', label: 'Studio', icon: BsGrid },
            { id: 'phone', label: 'Phone', icon: BsPhone },
            { id: 'table', label: 'Table Tent', icon: BsQrCode },
            { id: 'card', label: 'Card', icon: BsCreditCard2Front },
          ].map((mode) => (
            <button
              key={mode.id}
              type="button"
              onClick={() => setActiveMockup(mode.id)}
              className={`py-1.5 px-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                activeMockup === mode.id
                  ? 'bg-white dark:bg-obsidian-800 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <mode.icon className="text-xs" />
              <span className="hidden sm:inline">{mode.label}</span>
            </button>
          ))}
        </div>

        {/* VIEW 1: Pure Canvas View */}
        {activeMockup === 'canvas' && (
          <div className="relative min-h-[320px] rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 dark:from-obsidian-950 dark:to-obsidian-850 p-6 flex flex-col items-center justify-center border border-slate-200 dark:border-white/[0.08] overflow-hidden group">
            {/* Subtle background grid pattern */}
            <div className="absolute inset-0 bg-[radial-gradient(#6366f1_1px,transparent_1px)] [background-size:16px_16px] opacity-10 pointer-events-none" />

            <div
              ref={qrRef}
              className="relative z-10 transition-transform duration-300 group-hover:scale-[1.02] drop-shadow-md rounded-xl overflow-hidden p-2 bg-white/90 dark:bg-black/80 backdrop-blur"
            />

            <div className="mt-4 flex items-center gap-2">
              <button
                type="button"
                onClick={handleCopyImage}
                className="btn-ghost text-xs bg-white/80 dark:bg-white/[0.06] border border-slate-200 dark:border-white/[0.08] shadow-sm"
              >
                {copied ? <BsCheck2 className="text-emerald-500" /> : <BsFiles />}
                <span>{copied ? 'Copied!' : 'Copy Image'}</span>
              </button>
            </div>
          </div>
        )}

        {/* VIEW 2: Smartphone Mockup */}
        {activeMockup === 'phone' && (
          <div className="min-h-[340px] rounded-2xl bg-gradient-to-b from-slate-900 via-slate-950 to-black p-4 flex flex-col items-center justify-center border border-slate-800 text-white relative overflow-hidden shadow-2xl">
            {/* Realistic iPhone shell */}
            <div className="w-[240px] rounded-[36px] bg-slate-900 border-4 border-slate-700 shadow-2xl p-3 flex flex-col items-center relative overflow-hidden">
              {/* Dynamic Island */}
              <div className="w-20 h-4 bg-black rounded-full mb-3 flex items-center justify-end px-2">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
              </div>

              {/* Simulated Scanner Notification banner */}
              <div className="w-full bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-2 mb-3 text-left shadow-lg">
                <div className="flex items-center gap-1.5">
                  <div className="p-1 rounded bg-primary-500 text-white text-[10px]">
                    <BsQrCode />
                  </div>
                  <span className="text-[10px] font-bold text-slate-200 truncate">
                    Camera • Tap to Open
                  </span>
                </div>
                <p className="text-[10px] text-primary-300 font-mono truncate mt-0.5">
                  {value}
                </p>
              </div>

              {/* Center QR container */}
              <div className="p-2 bg-white rounded-2xl shadow-inner flex items-center justify-center my-auto">
                <div
                  dangerouslySetInnerHTML={{
                    __html: qrRef.current ? qrRef.current.innerHTML : ''
                  }}
                  className="scale-[0.6] origin-center -m-12"
                />
              </div>

              {/* Home indicator bar */}
              <div className="w-24 h-1 bg-white/40 rounded-full mt-4" />
            </div>
          </div>
        )}

        {/* VIEW 3: Restaurant Table Tent Mockup */}
        {activeMockup === 'table' && (
          <div className="min-h-[340px] rounded-2xl bg-gradient-to-br from-amber-50 to-orange-100 dark:from-stone-950 dark:to-neutral-900 p-6 flex flex-col items-center justify-center border border-slate-200 dark:border-stone-800 relative overflow-hidden">
            {/* Wooden / Acrylic Table Stand Card */}
            <div className="w-[220px] bg-white dark:bg-stone-900 rounded-2xl shadow-2xl border border-stone-200 dark:border-stone-700 p-4 text-center transform -rotate-1 hover:rotate-0 transition-transform duration-300">
              <span className="text-[10px] font-black uppercase tracking-widest text-primary-600 dark:text-primary-400 block mb-1">
                Scan For Menu / Info
              </span>
              <h4 className="text-xs font-bold text-slate-900 dark:text-white mb-2 truncate">
                {title || 'Welcome'}
              </h4>

              <div className="p-2 bg-slate-50 dark:bg-black rounded-xl border border-dashed border-slate-300 dark:border-stone-700 inline-block mb-3">
                <div
                  dangerouslySetInnerHTML={{
                    __html: qrRef.current ? qrRef.current.innerHTML : ''
                  }}
                  className="scale-[0.55] origin-center -m-14"
                />
              </div>

              <div className="bg-primary-600 text-white py-1 px-3 rounded-full text-[10px] font-bold tracking-wide inline-block shadow-sm">
                SCAN WITH PHONE CAMERA
              </div>
            </div>
            {/* Stand shadow base */}
            <div className="w-48 h-3 bg-black/20 dark:bg-black/50 rounded-full blur-sm mt-3" />
          </div>
        )}

        {/* VIEW 4: Matte Business Card Mockup */}
        {activeMockup === 'card' && (
          <div className="min-h-[340px] rounded-2xl bg-gradient-to-br from-slate-200 to-slate-300 dark:from-neutral-950 dark:to-stone-900 p-6 flex flex-col items-center justify-center border border-slate-200 dark:border-neutral-800">
            {/* Luxury Card */}
            <div className="w-[280px] h-[170px] bg-slate-900 dark:bg-[#0c0d12] rounded-2xl p-4 text-white shadow-2xl border border-white/10 relative overflow-hidden flex items-center justify-between">
              <div className="space-y-1 z-10">
                <div className="w-6 h-6 rounded-lg bg-gradient-to-tr from-primary-500 to-accent-violet flex items-center justify-center text-xs font-bold mb-2">
                  Q
                </div>
                <p className="text-xs font-black tracking-wide text-white">{title || 'Contact Card'}</p>
                <p className="text-[9px] text-slate-400 uppercase tracking-widest font-mono">Tap & Scan</p>
                <span className="inline-block mt-2 text-[9px] text-accent-cyan bg-accent-cyan/10 border border-accent-cyan/30 px-1.5 py-0.5 rounded">
                  NFC + QR Enabled
                </span>
              </div>

              <div className="p-1 bg-white rounded-xl shadow-lg flex-shrink-0 z-10">
                <div
                  dangerouslySetInnerHTML={{
                    __html: qrRef.current ? qrRef.current.innerHTML : ''
                  }}
                  className="scale-[0.45] origin-center -m-16"
                />
              </div>

              {/* Background ambient shine */}
              <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-primary-500/20 rounded-full blur-2xl pointer-events-none" />
            </div>
          </div>
        )}

        {/* Primary Save Action */}
        <button
          type="button"
          onClick={onSave}
          disabled={isSaving}
          className="btn-primary w-full text-sm font-bold tracking-wide py-3 shadow-glow-md"
        >
          {isSaving ? 'Saving to Database...' : 'Save QR & Generate Dynamic Link'}
        </button>

        {/* Download Deck */}
        <div className="pt-2 border-t border-slate-200 dark:border-white/[0.06] space-y-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Export Options
          </span>
          <div className="grid grid-cols-4 gap-1.5">
            <button
              type="button"
              onClick={() => handleClientDownload('png')}
              className="btn-secondary py-2 text-xs font-bold"
            >
              PNG
            </button>
            <button
              type="button"
              onClick={() => handleClientDownload('svg')}
              className="btn-secondary py-2 text-xs font-bold"
            >
              SVG
            </button>
            <button
              type="button"
              onClick={() => handleClientDownload('jpeg')}
              className="btn-secondary py-2 text-xs font-bold"
            >
              JPG
            </button>
            <button
              type="button"
              onClick={() => {
                if (savedId && onDownloadBackend) {
                  onDownloadBackend('pdf')
                } else {
                  toast('Save QR first to generate high-DPI PDF', { icon: 'ℹ️' })
                  handleClientDownload('png')
                }
              }}
              className="btn-secondary py-2 text-xs font-bold text-primary-600 dark:text-primary-400"
            >
              PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
