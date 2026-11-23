/**
 * Phase 4 Utility Helpers.
 * Webhook signature verification, geo-fencing lookup, time-of-day scheduler, and API key scopes.
 */

export function isWithinSchedule(startTime, endTime, currentTime = '12:00') {
  if (!startTime || !endTime) return true
  const cleanStart = startTime.trim()
  const cleanEnd = endTime.trim()
  const cleanCurrent = currentTime.trim()

  if (cleanStart <= cleanEnd) {
    return cleanCurrent >= cleanStart && cleanCurrent <= cleanEnd
  }
  // Spans midnight (e.g. 22:00 to 06:00)
  return cleanCurrent >= cleanStart || cleanCurrent <= cleanEnd
}

export function resolveGeoDestination(geoRoutingJson, countryCode, fallbackUrl) {
  if (!geoRoutingJson || !countryCode) return fallbackUrl
  try {
    const geoMap = typeof geoRoutingJson === 'string' ? JSON.parse(geoRoutingJson) : geoRoutingJson
    const code = countryCode.trim().toUpperCase()
    if (geoMap[code]) return geoMap[code]
    if (geoMap['DEFAULT']) return geoMap['DEFAULT']
    return fallbackUrl
  } catch {
    return fallbackUrl
  }
}

export function hasApiKeyScope(grantedScopesStr, requiredScope) {
  if (!grantedScopesStr || !requiredScope) return false
  const scopes = grantedScopesStr.split(',').map((s) => s.trim().toLowerCase())
  return scopes.includes('admin') || scopes.includes(requiredScope.toLowerCase())
}
