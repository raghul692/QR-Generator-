import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { getLuminance, getContrastRatio, evaluateScannability } from './scannability.js'

describe('Scannability & Contrast Calculator', () => {
  it('calculates correct relative luminance for pure black and pure white', () => {
    assert.equal(getLuminance('#000000'), 0)
    assert.equal(Math.round(getLuminance('#FFFFFF')), 1)
  })

  it('calculates 21:1 contrast ratio for black on white', () => {
    const ratio = getContrastRatio('#000000', '#FFFFFF')
    assert.equal(ratio, 21.0)
  })

  it('calculates 1:1 contrast ratio for identical colors', () => {
    const ratio = getContrastRatio('#4F46E5', '#4F46E5')
    assert.equal(ratio, 1.0)
  })

  it('classifies high contrast as optimal (AAA)', () => {
    const res = evaluateScannability(15.2)
    assert.equal(res.status, 'optimal')
    assert.equal(res.score, 100)
    assert.match(res.label, /AAA/)
  })

  it('classifies medium contrast (5.5) as good (AA)', () => {
    const res = evaluateScannability(5.5)
    assert.equal(res.status, 'good')
    assert.equal(res.score, 85)
    assert.match(res.label, /AA/)
  })

  it('classifies low contrast (3.5) as caution', () => {
    const res = evaluateScannability(3.5)
    assert.equal(res.status, 'caution')
    assert.equal(res.score, 60)
  })

  it('classifies poor contrast (1.8) as critical risk', () => {
    const res = evaluateScannability(1.8)
    assert.equal(res.status, 'critical')
    assert.equal(res.score, 25)
    assert.match(res.label, /Failure Risk/)
  })
})
