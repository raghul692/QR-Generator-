import { useMemo } from 'react'
import { BsShieldCheck, BsExclamationTriangleFill, BsCheckCircleFill, BsInfoCircle } from 'react-icons/bs'

// Convert hex to RGB
function hexToRgb(hex) {
  if (!hex) return { r: 0, g: 0, b: 0 }
  let cleanHex = hex.replace('#', '')
  if (cleanHex.length === 3) {
    cleanHex = cleanHex.split('').map((c) => c + c).join('')
  }
  const num = parseInt(cleanHex, 16)
  return {
    r: (num >> 16) & 255,
    g: (num >> 8) & 255,
    b: num & 255,
  }
}

// Calculate relative luminance
function getLuminance({ r, g, b }) {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4)
  })
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
}

// Contrast ratio
function getContrastRatio(hex1, hex2) {
  const lum1 = getLuminance(hexToRgb(hex1))
  const lum2 = getLuminance(hexToRgb(hex2))
  const brightest = Math.max(lum1, lum2)
  const darkest = Math.min(lum1, lum2)
  return (brightest + 0.05) / (darkest + 0.05)
}

export default function ScannabilityMeter({
  foregroundColor = '#000000',
  backgroundColor = '#FFFFFF',
  errorCorrection = 'H',
  hasLogo = false,
}) {
  const analysis = useMemo(() => {
    const ratio = getContrastRatio(foregroundColor, backgroundColor)

    let score = Math.min(100, Math.round((ratio / 7) * 90 + 10))
    if (ratio < 2.5) score = Math.max(25, Math.round(ratio * 15))

    let status = 'optimal'
    let message = 'Optimal contrast. Guaranteed fast reading across all smartphone cameras.'

    if (ratio < 2.8) {
      status = 'poor'
      message = 'Low contrast detected. Some mobile cameras will fail to scan this code reliably.'
    } else if (ratio < 4.5) {
      status = 'moderate'
      message = 'Moderate contrast. Scannable in good lighting, but high contrast is recommended for print.'
    }

    // Logo safety check
    let logoWarning = null
    if (hasLogo && (errorCorrection === 'L' || errorCorrection === 'M')) {
      logoWarning = 'Logo detected with low error correction (L/M). Recommended: Set Error Correction to Q or H (30%) to ensure scan reliability.'
    }

    return {
      ratio: ratio.toFixed(2),
      score,
      status,
      message,
      logoWarning,
    }
  }, [foregroundColor, backgroundColor, errorCorrection, hasLogo])

  const statusConfig = {
    optimal: {
      color: 'text-emerald-500',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      barColor: 'bg-emerald-500',
      badge: '98% Excellent',
      Icon: BsCheckCircleFill,
    },
    moderate: {
      color: 'text-amber-500',
      bg: 'bg-amber-500/10 border-amber-500/20',
      barColor: 'bg-amber-500',
      badge: '75% Moderate',
      Icon: BsInfoCircle,
    },
    poor: {
      color: 'text-rose-500',
      bg: 'bg-rose-500/10 border-rose-500/20',
      barColor: 'bg-rose-500',
      badge: `${analysis.score}% Low Contrast`,
      Icon: BsExclamationTriangleFill,
    },
  }[analysis.status]

  return (
    <div className="glass-panel p-4 space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BsShieldCheck className="text-primary-500 text-base" />
          <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
            Scannability & Contrast Guard
          </span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold border ${statusConfig.bg} ${statusConfig.color}`}>
          {statusConfig.badge}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-200 dark:bg-white/[0.08] h-2 rounded-full overflow-hidden">
        <div
          className={`h-full ${statusConfig.barColor} transition-all duration-500 rounded-full`}
          style={{ width: `${analysis.score}%` }}
        />
      </div>

      {/* Description */}
      <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed flex items-start gap-1.5">
        <statusConfig.Icon className={`text-xs mt-0.5 flex-shrink-0 ${statusConfig.color}`} />
        <span>{analysis.message} (Contrast: {analysis.ratio}:1)</span>
      </p>

      {/* Logo warning if present */}
      {analysis.logoWarning && (
        <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 text-[11px] flex items-start gap-2">
          <BsExclamationTriangleFill className="text-xs mt-0.5 flex-shrink-0" />
          <span>{analysis.logoWarning}</span>
        </div>
      )}
    </div>
  )
}
