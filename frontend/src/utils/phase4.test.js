import test from 'node:test'
import assert from 'node:assert/strict'
import {
  isWithinSchedule,
  resolveGeoDestination,
  hasApiKeyScope,
} from './phase4_helpers.js'

test('Phase 4: isWithinSchedule standard daytime schedule', () => {
  // 09:00 to 17:00 business hours
  assert.equal(isWithinSchedule('09:00', '17:00', '12:00'), true)
  assert.equal(isWithinSchedule('09:00', '17:00', '09:00'), true) // Exact start
  assert.equal(isWithinSchedule('09:00', '17:00', '17:00'), true) // Exact end
  assert.equal(isWithinSchedule('09:00', '17:00', '08:59'), false)
  assert.equal(isWithinSchedule('09:00', '17:00', '17:01'), false)
  assert.equal(isWithinSchedule('09:00', '17:00', '23:00'), false)
})

test('Phase 4: isWithinSchedule overnight midnight-spanning schedule', () => {
  // 22:00 to 06:00 night shift
  assert.equal(isWithinSchedule('22:00', '06:00', '23:30'), true)
  assert.equal(isWithinSchedule('22:00', '06:00', '02:15'), true)
  assert.equal(isWithinSchedule('22:00', '06:00', '22:00'), true)
  assert.equal(isWithinSchedule('22:00', '06:00', '06:00'), true)
  assert.equal(isWithinSchedule('22:00', '06:00', '12:00'), false)
  assert.equal(isWithinSchedule('22:00', '06:00', '21:59'), false)
  assert.equal(isWithinSchedule('22:00', '06:00', '06:01'), false)
})

test('Phase 4: isWithinSchedule fallback with empty values', () => {
  assert.equal(isWithinSchedule(null, '17:00', '12:00'), true)
  assert.equal(isWithinSchedule('09:00', null, '12:00'), true)
  assert.equal(isWithinSchedule('', '', '12:00'), true)
})

test('Phase 4: resolveGeoDestination country routing and fallbacks', () => {
  const geoJson = JSON.stringify({
    IN: 'https://in.brand.com/store',
    US: 'https://us.brand.com/store',
    GB: 'https://uk.brand.com/store',
    DEFAULT: 'https://global.brand.com/store',
  })
  const fallback = 'https://brand.com/home'

  // Exact country match (case insensitive)
  assert.equal(resolveGeoDestination(geoJson, 'IN', fallback), 'https://in.brand.com/store')
  assert.equal(resolveGeoDestination(geoJson, 'in', fallback), 'https://in.brand.com/store')
  assert.equal(resolveGeoDestination(geoJson, 'US', fallback), 'https://us.brand.com/store')
  assert.equal(resolveGeoDestination(geoJson, 'gb', fallback), 'https://uk.brand.com/store')

  // Country not explicitly mapped falls back to DEFAULT in json
  assert.equal(resolveGeoDestination(geoJson, 'FR', fallback), 'https://global.brand.com/store')

  // Country not explicitly mapped and no DEFAULT falls back to fallbackUrl
  const noDefaultGeo = JSON.stringify({ IN: 'https://in.brand.com' })
  assert.equal(resolveGeoDestination(noDefaultGeo, 'DE', fallback), fallback)

  // Empty country code falls back to fallbackUrl
  assert.equal(resolveGeoDestination(geoJson, '', fallback), fallback)
  assert.equal(resolveGeoDestination(null, 'IN', fallback), fallback)
  assert.equal(resolveGeoDestination('invalid-json', 'IN', fallback), fallback)
})

test('Phase 4: hasApiKeyScope permission evaluation', () => {
  // admin scope grants all
  assert.equal(hasApiKeyScope('admin', 'qr:read'), true)
  assert.equal(hasApiKeyScope('admin', 'qr:write'), true)
  assert.equal(hasApiKeyScope('ADMIN', 'anything'), true)

  // Granular scopes
  const standardKey = 'qr:read,qr:write,analytics:read'
  assert.equal(hasApiKeyScope(standardKey, 'qr:read'), true)
  assert.equal(hasApiKeyScope(standardKey, 'qr:write'), true)
  assert.equal(hasApiKeyScope(standardKey, 'analytics:read'), true)
  assert.equal(hasApiKeyScope(standardKey, 'bulk:write'), false)
  assert.equal(hasApiKeyScope(standardKey, 'admin'), false)

  // Case insensitive match
  assert.equal(hasApiKeyScope('QR:READ,QR:WRITE', 'qr:read'), true)

  // Edge cases
  assert.equal(hasApiKeyScope('', 'qr:read'), false)
  assert.equal(hasApiKeyScope(null, 'qr:read'), false)
  assert.equal(hasApiKeyScope('qr:read', ''), false)
})
