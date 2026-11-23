/**
 * Phase 3 Utility Helpers.
 * Multi-Tenancy, Role Hierarchy, Domain Formatters, and Retention calculations.
 */

export const ROLE_HIERARCHY = {
  owner: 4,
  admin: 3,
  editor: 2,
  viewer: 1,
}

export function hasPermission(userRole, requiredRole) {
  if (!userRole || !requiredRole) return false
  const userLevel = ROLE_HIERARCHY[userRole.toLowerCase()] || 0
  const reqLevel = ROLE_HIERARCHY[requiredRole.toLowerCase()] || 0
  return userLevel >= reqLevel
}

export function slugifyWorkspace(name) {
  if (!name || typeof name !== 'string') return ''
  return name
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function formatCustomDomain(input) {
  if (!input || typeof input !== 'string') return ''
  return input
    .trim()
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/\/.*$/, '')
    .split(':')[0]
}

export function isValidDomainFormat(domain) {
  const clean = formatCustomDomain(domain)
  const regex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,63}$/
  return regex.test(clean)
}

export function calculateRetentionCutoff(retentionDays = 90) {
  const now = new Date()
  const cutoff = new Date(now.getTime() - retentionDays * 24 * 60 * 60 * 1000)
  return cutoff.toISOString()
}
