import test from 'node:test'
import assert from 'node:assert/strict'
import {
  hasPermission,
  slugifyWorkspace,
  formatCustomDomain,
  isValidDomainFormat,
  calculateRetentionCutoff,
} from './phase3_helpers.js'

test('Phase 3: hasPermission role hierarchy enforcement', () => {
  assert.equal(hasPermission('owner', 'admin'), true)
  assert.equal(hasPermission('owner', 'viewer'), true)
  assert.equal(hasPermission('admin', 'admin'), true)
  assert.equal(hasPermission('admin', 'editor'), true)
  assert.equal(hasPermission('editor', 'admin'), false)
  assert.equal(hasPermission('viewer', 'editor'), false)
  assert.equal(hasPermission('unknown', 'viewer'), false)
})

test('Phase 3: slugifyWorkspace URL-safe slug generator', () => {
  assert.equal(slugifyWorkspace('Acme Marketing & Growth'), 'acme-marketing-growth')
  assert.equal(slugifyWorkspace('   QR Enterprise 2026!  '), 'qr-enterprise-2026')
  assert.equal(slugifyWorkspace(''), '')
})

test('Phase 3: formatCustomDomain cleaner and normalizer', () => {
  assert.equal(formatCustomDomain('https://qr.brand.com/'), 'qr.brand.com')
  assert.equal(formatCustomDomain('http://LINKS.COMPANY.ORG:8080/path'), 'links.company.org')
  assert.equal(formatCustomDomain('   qr.mysite.io   '), 'qr.mysite.io')
})

test('Phase 3: isValidDomainFormat regex validation', () => {
  assert.equal(isValidDomainFormat('qr.brand.com'), true)
  assert.equal(isValidDomainFormat('https://links.enterprise.org'), true)
  assert.equal(isValidDomainFormat('invalid_domain'), false)
  assert.equal(isValidDomainFormat(''), false)
  assert.equal(isValidDomainFormat('127.0.0.1'), false)
})

test('Phase 3: calculateRetentionCutoff timestamp calculation', () => {
  const cutoff = calculateRetentionCutoff(90)
  assert.ok(typeof cutoff === 'string')
  const date = new Date(cutoff)
  assert.ok(!isNaN(date.getTime()))
  // Cutoff should be approximately 90 days before today
  const diffDays = Math.round((Date.now() - date.getTime()) / (1000 * 60 * 60 * 24))
  assert.equal(diffDays, 90)
})
