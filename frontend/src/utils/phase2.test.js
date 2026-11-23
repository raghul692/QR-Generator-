import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { formatVCardRFC6350, sanitizeSlug, buildUTMUrl } from './phase2_helpers.js'

describe('Phase 2 Frontend Utilities', () => {
  describe('vCard RFC 6350 Generator', () => {
    it('generates standard RFC 6350 format with FN and N', () => {
      const vcard = formatVCardRFC6350({
        firstName: 'Jane',
        lastName: 'Doe',
        title: 'Lead Architect',
        organization: 'Acme Corp',
        phone: '+15551234567',
        email: 'jane@acme.com',
        website: 'https://acme.com',
      })

      assert.match(vcard, /^BEGIN:VCARD/)
      assert.match(vcard, /VERSION:3\.0/)
      assert.match(vcard, /N:Doe;Jane;;;/)
      assert.match(vcard, /FN:Jane Doe/)
      assert.match(vcard, /ORG:Acme Corp/)
      assert.match(vcard, /TITLE:Lead Architect/)
      assert.match(vcard, /TEL;TYPE=CELL,VOICE:\+15551234567/)
      assert.match(vcard, /EMAIL;TYPE=PREF,INTERNET:jane@acme\.com/)
      assert.match(vcard, /URL:https:\/\/acme\.com/)
      assert.match(vcard, /END:VCARD$/)
    })

    it('handles partial contact data gracefully', () => {
      const vcard = formatVCardRFC6350({
        firstName: 'Solo',
      })
      assert.match(vcard, /FN:Solo/)
      assert.match(vcard, /N:;Solo;;;/)
    })
  })

  describe('Slug Sanitization for Landing Pages', () => {
    it('converts titles to lowercase URL-safe slugs', () => {
      assert.equal(sanitizeSlug('Summer VIP Sale 2026!'), 'summer-vip-sale-2026')
      assert.equal(sanitizeSlug('  Special & Limited Offer!  '), 'special-limited-offer')
      assert.equal(sanitizeSlug('already-clean_slug'), 'already-clean_slug')
    })
  })

  describe('UTM Attribution URL Builder', () => {
    it('appends UTM parameters without overriding existing query params', () => {
      const base = 'https://store.example.com/item?ref=homepage'
      const utmUrl = buildUTMUrl(base, {
        source: 'qr_flyer',
        medium: 'print',
        campaign: 'summer_launch',
      })

      assert.match(utmUrl, /ref=homepage/)
      assert.match(utmUrl, /utm_source=qr_flyer/)
      assert.match(utmUrl, /utm_medium=print/)
      assert.match(utmUrl, /utm_campaign=summer_launch/)
    })

    it('handles invalid URLs safely without crashing', () => {
      assert.equal(buildUTMUrl('invalid-url', { source: 'qr' }), 'invalid-url')
    })
  })
})
