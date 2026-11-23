/**
 * RFC 6350 vCard formatting helper
 */
export function formatVCardRFC6350({
  firstName = '',
  lastName = '',
  title = '',
  organization = '',
  phone = '',
  email = '',
  website = '',
}) {
  const fullName = [firstName, lastName].filter(Boolean).join(' ')
  const lines = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    `N:${lastName};${firstName};;;`,
    `FN:${fullName}`,
  ]

  if (organization) lines.push(`ORG:${organization}`)
  if (title) lines.push(`TITLE:${title}`)
  if (phone) lines.push(`TEL;TYPE=CELL,VOICE:${phone}`)
  if (email) lines.push(`EMAIL;TYPE=PREF,INTERNET:${email}`)
  if (website) lines.push(`URL:${website}`)

  lines.push('END:VCARD')
  return lines.join('\r\n')
}

/**
 * Slug generator for landing pages
 */
export function sanitizeSlug(input = '') {
  return input
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_-]/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

/**
 * UTM Builder for dynamic QR redirects
 */
export function buildUTMUrl(targetUrl, { source, medium, campaign }) {
  try {
    const url = new URL(targetUrl)
    if (source) url.searchParams.set('utm_source', source)
    if (medium) url.searchParams.set('utm_medium', medium)
    if (campaign) url.searchParams.set('utm_campaign', campaign)
    return url.toString()
  } catch {
    return targetUrl
  }
}
