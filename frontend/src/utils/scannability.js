/**
 * QRMaster Pro — Scannability and Contrast Diagnostics.
 *
 * Implements WCAG 2.2 Relative Luminance and Optical Contrast calculation
 * to determine QR code camera readability before generation.
 */

export function getLuminance(hex) {
  if (!hex || typeof hex !== 'string') return 0
  const cleanHex = hex.replace('#', '')
  if (cleanHex.length !== 6) return 0
  const r = parseInt(cleanHex.substring(0, 2), 16) / 255
  const g = parseInt(cleanHex.substring(2, 4), 16) / 255
  const b = parseInt(cleanHex.substring(4, 6), 16) / 255
  const a = [r, g, b].map((v) => (v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)))
  return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2]
}

export function getContrastRatio(hex1, hex2) {
  const l1 = getLuminance(hex1)
  const l2 = getLuminance(hex2)
  const lighter = Math.max(l1, l2)
  const darker = Math.min(l1, l2)
  return Number(((lighter + 0.05) / (darker + 0.05)).toFixed(1))
}

export function evaluateScannability(contrastRatio) {
  const contrastNum = Number(contrastRatio) || 1
  if (contrastNum < 3.0) {
    return {
      status: 'critical',
      label: 'High Scan Failure Risk (<3.0:1)',
      score: 25,
      className: 'text-rose-700 bg-rose-50/90 dark:text-rose-300 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800',
    }
  }
  if (contrastNum < 4.5) {
    return {
      status: 'caution',
      label: 'Low Optical Contrast (Caution)',
      score: 60,
      className: 'text-amber-700 bg-amber-50/90 dark:text-amber-300 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800',
    }
  }
  if (contrastNum < 7.0) {
    return {
      status: 'good',
      label: 'Good Scannability (AA)',
      score: 85,
      className: 'text-indigo-700 bg-indigo-50/90 dark:text-indigo-300 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800',
    }
  }
  return {
    status: 'optimal',
    label: 'Optimal Scannability (AAA)',
    score: 100,
    className: 'text-emerald-700 bg-emerald-50/90 dark:text-emerald-300 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800',
  }
}
