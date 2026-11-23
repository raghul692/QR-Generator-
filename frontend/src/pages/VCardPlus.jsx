import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsPersonVcard, BsTelephone, BsEnvelope, BsGlobe, BsBuilding,
  BsGeoAlt, BsLinkedin, BsTwitter, BsGithub, BsInstagram,
  BsDownload, BsQrCode, BsShare, BsCheckCircle, BsCopy, BsPersonFill,
  BsBoxArrowUpRight, BsBookmarkCheck,
} from 'react-icons/bs'
import { vcardAPI } from '../services/api'

const CARD_THEMES = [
  {
    id: 'executive-dark',
    name: 'Executive Dark',
    headerBg: 'bg-gradient-to-br from-slate-900 to-slate-800',
    avatarBg: 'bg-indigo-600 text-white',
    badgeBg: 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30',
    accentBtn: 'bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800',
    bg: 'bg-slate-900 text-slate-100',
    card: 'bg-slate-800/90 border border-slate-700/80',
    subtext: 'text-slate-400',
  },
  {
    id: 'clean-slate',
    name: 'Clean Monochrome',
    headerBg: 'bg-slate-100',
    avatarBg: 'bg-slate-900 text-white',
    badgeBg: 'bg-slate-200 text-slate-800',
    accentBtn: 'bg-slate-900 text-white hover:bg-slate-800',
    bg: 'bg-slate-50 text-slate-900',
    card: 'bg-white border border-slate-200 shadow-sm',
    subtext: 'text-slate-500',
  },
  {
    id: 'emerald-pro',
    name: 'Emerald Luxe',
    headerBg: 'bg-emerald-950',
    avatarBg: 'bg-emerald-600 text-white',
    badgeBg: 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30',
    accentBtn: 'bg-emerald-500 text-emerald-950 font-semibold hover:bg-emerald-400',
    bg: 'bg-emerald-950 text-emerald-50',
    card: 'bg-emerald-900/80 border border-emerald-800/70',
    subtext: 'text-emerald-300/80',
  },
  {
    id: 'warm-amber',
    name: 'Artisan Bronze',
    headerBg: 'bg-stone-900',
    avatarBg: 'bg-amber-600 text-white',
    badgeBg: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
    accentBtn: 'bg-amber-500 text-stone-950 font-semibold hover:bg-amber-400',
    bg: 'bg-stone-900 text-stone-100',
    card: 'bg-stone-800/80 border border-stone-700',
    subtext: 'text-stone-400',
  },
]

export default function VCardPlus() {
  const [activeFormTab, setActiveFormTab] = useState('profile') // 'profile' | 'contact' | 'socials' | 'theme'
  const [showQRModal, setShowQRModal] = useState(false)

  // vCard Form State
  const [vcard, setVcard] = useState({
    firstName: 'Alex',
    lastName: 'Vance',
    title: 'Chief Technology Officer',
    organization: 'Nova Dynamics',
    department: 'Engineering & Product',
    phone: '+1 (555) 234-5678',
    workPhone: '+1 (555) 876-5432',
    email: 'alex.vance@novadynamics.io',
    workEmail: 'tech@novadynamics.io',
    website: 'https://novadynamics.io',
    street: '742 Tech Boulevard, Suite 500',
    city: 'San Francisco',
    state: 'CA',
    postalCode: '94107',
    country: 'United States',
    note: 'Spearheading scalable architecture, dynamic QR pipelines, and digital identity standards.',
    socials: {
      linkedin: 'https://linkedin.com/in/alexvance',
      twitter: 'https://x.com/alexvance',
      github: 'https://github.com/alexvance',
      instagram: '',
    },
    theme: 'executive-dark',
  })

  const currentTheme = CARD_THEMES.find((t) => t.id === vcard.theme) || CARD_THEMES[0]

  // Full Name & Initials helper
  const fullName = [vcard.firstName, vcard.lastName].filter(Boolean).join(' ') || 'Your Name'
  const initials = `${vcard.firstName?.[0] || 'V'}${vcard.lastName?.[0] || 'P'}`.toUpperCase()

  // Generate RFC 6350 vCard v3.0 text
  const generateVCFText = () => {
    const lines = [
      'BEGIN:VCARD',
      'VERSION:3.0',
      `N:${vcard.lastName || ''};${vcard.firstName || ''};;;`,
      `FN:${fullName}`,
      vcard.organization ? `ORG:${vcard.organization}${vcard.department ? ';' + vcard.department : ''}` : '',
      vcard.title ? `TITLE:${vcard.title}` : '',
      vcard.phone ? `TEL;TYPE=CELL,VOICE:${vcard.phone}` : '',
      vcard.workPhone ? `TEL;TYPE=WORK,VOICE:${vcard.workPhone}` : '',
      vcard.email ? `EMAIL;TYPE=PREF,INTERNET:${vcard.email}` : '',
      vcard.workEmail ? `EMAIL;TYPE=WORK,INTERNET:${vcard.workEmail}` : '',
      vcard.website ? `URL:${vcard.website}` : '',
      (vcard.street || vcard.city || vcard.country)
        ? `ADR;TYPE=WORK:;;${vcard.street || ''};${vcard.city || ''};${vcard.state || ''};${vcard.postalCode || ''};${vcard.country || ''}`
        : '',
      vcard.note ? `NOTE:${vcard.note.replace(/\n/g, '\\n')}` : '',
      'END:VCARD',
    ].filter(Boolean)

    return lines.join('\r\n')
  }

  // Handle 1-Tap Save to Contacts (.vcf)
  const handleSaveToContacts = async () => {
    try {
      // First try backend vcardAPI.download
      const vcfString = generateVCFText()
      const blob = new Blob([vcfString], { type: 'text/vcard;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${(vcard.firstName + '_' + vcard.lastName).toLowerCase() || 'contact'}.vcf`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      toast.success('vCard downloaded! Open file to save directly to iOS/Android Contacts.')
    } catch {
      toast.error('Failed to generate vCard file.')
    }
  }

  // Handle Copy vCard Text
  const handleCopyVCF = () => {
    const vcf = generateVCFText()
    navigator.clipboard.writeText(vcf)
    toast.success('Raw RFC 6350 vCard copied to clipboard!')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsPersonVcard className="text-primary-600 dark:text-primary-400" />
            vCard Plus — Digital Business Card
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Build your interactive digital business card with seamless 1-tap "Save to Contacts" (.vcf) export.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyVCF}
            className="btn-secondary text-xs flex items-center gap-1.5"
            title="Copy RFC 6350 text"
          >
            <BsCopy /> Copy Raw VCF
          </button>
          <button
            type="button"
            onClick={() => setShowQRModal(true)}
            className="btn-primary text-xs flex items-center gap-1.5"
          >
            <BsQrCode /> vCard QR
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Editor Form Panel (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="glass-card p-6 space-y-5">
            {/* Form Tabs */}
            <div className="flex border-b border-gray-200 dark:border-gray-700 pb-2 gap-2 overflow-x-auto">
              {[
                { id: 'profile', label: '1. Identity & Role' },
                { id: 'contact', label: '2. Phone & Email' },
                { id: 'location', label: '3. Office Address' },
                { id: 'socials', label: '4. Socials & Bio' },
                { id: 'theme', label: '5. Styling Theme' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setActiveFormTab(tab.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                    activeFormTab === tab.id
                      ? 'bg-primary-50 dark:bg-primary-900/40 text-primary-600 dark:text-primary-300 font-semibold'
                      : 'text-gray-500 hover:text-gray-800 dark:hover:text-gray-200'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab 1: Profile */}
            {activeFormTab === 'profile' && (
              <div className="space-y-4 animate-fade-in">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      First Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={vcard.firstName}
                      onChange={(e) => setVcard({ ...vcard, firstName: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={vcard.lastName}
                      onChange={(e) => setVcard({ ...vcard, lastName: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Job Title
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Lead Solutions Architect"
                      value={vcard.title}
                      onChange={(e) => setVcard({ ...vcard, title: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Company / Organization
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Nova Systems Inc."
                      value={vcard.organization}
                      onChange={(e) => setVcard({ ...vcard, organization: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Department
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Infrastructure & Cloud Operations"
                    value={vcard.department}
                    onChange={(e) => setVcard({ ...vcard, department: e.target.value })}
                    className="input-field"
                  />
                </div>
              </div>
            )}

            {/* Tab 2: Contact */}
            {activeFormTab === 'contact' && (
              <div className="space-y-4 animate-fade-in">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsTelephone /> Mobile Phone
                    </label>
                    <input
                      type="tel"
                      placeholder="+1 (555) 000-0000"
                      value={vcard.phone}
                      onChange={(e) => setVcard({ ...vcard, phone: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsBuilding /> Work / Office Phone
                    </label>
                    <input
                      type="tel"
                      placeholder="+1 (555) 000-0000"
                      value={vcard.workPhone}
                      onChange={(e) => setVcard({ ...vcard, workPhone: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsEnvelope /> Primary Email
                    </label>
                    <input
                      type="email"
                      placeholder="name@company.com"
                      value={vcard.email}
                      onChange={(e) => setVcard({ ...vcard, email: e.target.value })}
                      className="input-field"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsGlobe /> Website / Portfolio
                    </label>
                    <input
                      type="url"
                      placeholder="https://company.com"
                      value={vcard.website}
                      onChange={(e) => setVcard({ ...vcard, website: e.target.value })}
                      className="input-field"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Tab 3: Location */}
            {activeFormTab === 'location' && (
              <div className="space-y-4 animate-fade-in">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Street Address
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 100 Market Street, Floor 14"
                    value={vcard.street}
                    onChange={(e) => setVcard({ ...vcard, street: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      City
                    </label>
                    <input
                      type="text"
                      placeholder="San Francisco"
                      value={vcard.city}
                      onChange={(e) => setVcard({ ...vcard, city: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      State / Prov
                    </label>
                    <input
                      type="text"
                      placeholder="CA"
                      value={vcard.state}
                      onChange={(e) => setVcard({ ...vcard, state: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      ZIP / Postal
                    </label>
                    <input
                      type="text"
                      placeholder="94105"
                      value={vcard.postalCode}
                      onChange={(e) => setVcard({ ...vcard, postalCode: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Country
                    </label>
                    <input
                      type="text"
                      placeholder="United States"
                      value={vcard.country}
                      onChange={(e) => setVcard({ ...vcard, country: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Tab 4: Socials & Bio */}
            {activeFormTab === 'socials' && (
              <div className="space-y-4 animate-fade-in">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Bio / Executive Summary (Saved to Note)
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Short professional intro or mission..."
                    value={vcard.note}
                    onChange={(e) => setVcard({ ...vcard, note: e.target.value })}
                    className="input-field py-2 text-xs"
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsLinkedin /> LinkedIn Profile URL
                    </label>
                    <input
                      type="url"
                      placeholder="https://linkedin.com/in/..."
                      value={vcard.socials.linkedin}
                      onChange={(e) =>
                        setVcard({
                          ...vcard,
                          socials: { ...vcard.socials, linkedin: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsTwitter /> Twitter / X Profile URL
                    </label>
                    <input
                      type="url"
                      placeholder="https://x.com/..."
                      value={vcard.socials.twitter}
                      onChange={(e) =>
                        setVcard({
                          ...vcard,
                          socials: { ...vcard.socials, twitter: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsGithub /> GitHub Profile URL
                    </label>
                    <input
                      type="url"
                      placeholder="https://github.com/..."
                      value={vcard.socials.github}
                      onChange={(e) =>
                        setVcard({
                          ...vcard,
                          socials: { ...vcard.socials, github: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                      <BsInstagram /> Instagram Profile URL
                    </label>
                    <input
                      type="url"
                      placeholder="https://instagram.com/..."
                      value={vcard.socials.instagram}
                      onChange={(e) =>
                        setVcard({
                          ...vcard,
                          socials: { ...vcard.socials, instagram: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Tab 5: Theme */}
            {activeFormTab === 'theme' && (
              <div className="space-y-4 animate-fade-in">
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Select Card Visual Theme
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {CARD_THEMES.map((theme) => (
                    <button
                      key={theme.id}
                      type="button"
                      onClick={() => setVcard({ ...vcard, theme: theme.id })}
                      className={`p-3.5 rounded-xl border text-left transition-all ${
                        vcard.theme === theme.id
                          ? 'border-indigo-600 ring-2 ring-indigo-500/20 bg-indigo-50/30 dark:bg-indigo-950/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-4 h-4 rounded-full ${theme.avatarBg}`} />
                        <span className="font-semibold text-xs text-gray-900 dark:text-white">
                          {theme.name}
                        </span>
                      </div>
                      <div className={`h-8 rounded-lg ${theme.headerBg} flex items-center px-2 text-[10px] text-white/80`}>
                        {theme.name} Preview
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Bottom Form Actions */}
            <div className="flex items-center justify-between pt-4 border-t dark:border-gray-700">
              <button
                type="button"
                onClick={handleSaveToContacts}
                className="btn-primary text-sm flex items-center gap-2"
              >
                <BsDownload /> Download .VCF File
              </button>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowQRModal(true)}
                  className="btn-secondary text-xs flex items-center gap-1.5"
                >
                  <BsQrCode /> Show QR
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Live Mobile Device Preview Frame (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="text-center mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Live Digital Business Card
            </span>
            <p className="text-[11px] text-gray-400">Interactive 1-tap mobile preview</p>
          </div>

          {/* Mobile Bezel */}
          <div className="relative w-[320px] h-[640px] bg-slate-950 rounded-[44px] p-3 shadow-2xl border-4 border-slate-700 ring-1 ring-slate-800 flex flex-col select-none">
            {/* Dynamic Island */}
            <div className="absolute top-5 left-1/2 -translate-x-1/2 w-28 h-4 bg-black rounded-full z-20 flex items-center justify-end px-3">
              <div className="w-2.5 h-2.5 rounded-full bg-slate-900 border border-slate-700"></div>
            </div>

            {/* Screen Content */}
            <div
              className={`relative flex-1 w-full rounded-[34px] overflow-y-auto overflow-x-hidden flex flex-col p-4 pt-10 transition-colors duration-300 ${currentTheme.bg}`}
            >
              {/* Header profile area */}
              <div className="text-center pt-2 pb-3">
                {/* Initials Avatar */}
                <div
                  className={`w-16 h-16 mx-auto rounded-2xl flex items-center justify-center font-bold text-xl shadow-lg mb-2.5 ${currentTheme.avatarBg}`}
                >
                  {initials}
                </div>
                <h3 className="text-lg font-bold tracking-tight">{fullName}</h3>
                <p className={`text-xs font-medium mt-0.5 ${currentTheme.subtext}`}>
                  {vcard.title || 'Digital Professional'}
                </p>
                {vcard.organization && (
                  <span className={`inline-block text-[10px] px-2.5 py-0.5 rounded-full mt-1.5 font-medium ${currentTheme.badgeBg}`}>
                    {vcard.organization}
                  </span>
                )}
              </div>

              {/* ⚡ PROMINENT 1-TAP SAVE TO CONTACTS BUTTON */}
              <div className="my-2">
                <button
                  type="button"
                  onClick={handleSaveToContacts}
                  className={`w-full min-h-[46px] py-3 px-4 rounded-xl text-center text-xs font-bold shadow-lg flex items-center justify-center gap-2 transition-all active:scale-95 ${currentTheme.accentBtn}`}
                >
                  <BsBookmarkCheck className="text-sm" />
                  <span>Save to Contacts (.vcf)</span>
                </button>
              </div>

              {/* Quick Actions Row */}
              <div className="grid grid-cols-3 gap-2 my-2 text-center">
                {vcard.phone && (
                  <a
                    href={`tel:${vcard.phone}`}
                    className="p-2 rounded-xl bg-white/10 hover:bg-white/15 backdrop-blur-sm flex flex-col items-center gap-1 text-[10px] font-medium"
                  >
                    <BsTelephone className="text-xs" /> Call
                  </a>
                )}
                {vcard.email && (
                  <a
                    href={`mailto:${vcard.email}`}
                    className="p-2 rounded-xl bg-white/10 hover:bg-white/15 backdrop-blur-sm flex flex-col items-center gap-1 text-[10px] font-medium"
                  >
                    <BsEnvelope className="text-xs" /> Email
                  </a>
                )}
                {vcard.website && (
                  <a
                    href={vcard.website}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 rounded-xl bg-white/10 hover:bg-white/15 backdrop-blur-sm flex flex-col items-center gap-1 text-[10px] font-medium"
                  >
                    <BsGlobe className="text-xs" /> Web
                  </a>
                )}
              </div>

              {/* Contact Details Card */}
              <div className={`p-3 rounded-2xl space-y-2 mt-2 text-xs ${currentTheme.card}`}>
                {vcard.phone && (
                  <div className="flex items-center gap-2">
                    <BsTelephone className={`text-xs flex-shrink-0 ${currentTheme.subtext}`} />
                    <span className="font-mono text-[11px] truncate">{vcard.phone}</span>
                  </div>
                )}
                {vcard.email && (
                  <div className="flex items-center gap-2">
                    <BsEnvelope className={`text-xs flex-shrink-0 ${currentTheme.subtext}`} />
                    <span className="text-[11px] truncate">{vcard.email}</span>
                  </div>
                )}
                {(vcard.city || vcard.country) && (
                  <div className="flex items-center gap-2">
                    <BsGeoAlt className={`text-xs flex-shrink-0 ${currentTheme.subtext}`} />
                    <span className="text-[11px] truncate">
                      {[vcard.city, vcard.state, vcard.country].filter(Boolean).join(', ')}
                    </span>
                  </div>
                )}
                {vcard.note && (
                  <p className={`text-[10px] pt-1 border-t border-white/10 leading-relaxed italic ${currentTheme.subtext}`}>
                    "{vcard.note}"
                  </p>
                )}
              </div>

              {/* Social Channels Row */}
              <div className="mt-auto pt-3 flex justify-center items-center gap-3 text-sm opacity-80">
                {vcard.socials.linkedin && (
                  <a href={vcard.socials.linkedin} target="_blank" rel="noreferrer" className="hover:opacity-100">
                    <BsLinkedin />
                  </a>
                )}
                {vcard.socials.twitter && (
                  <a href={vcard.socials.twitter} target="_blank" rel="noreferrer" className="hover:opacity-100">
                    <BsTwitter />
                  </a>
                )}
                {vcard.socials.github && (
                  <a href={vcard.socials.github} target="_blank" rel="noreferrer" className="hover:opacity-100">
                    <BsGithub />
                  </a>
                )}
                {vcard.socials.instagram && (
                  <a href={vcard.socials.instagram} target="_blank" rel="noreferrer" className="hover:opacity-100">
                    <BsInstagram />
                  </a>
                )}
              </div>

              {/* Home indicator bar */}
              <div className="w-20 h-1 bg-white/30 rounded-full mx-auto mt-2"></div>
            </div>
          </div>
        </div>
      </div>

      {/* QR Code Modal */}
      <AnimatePresence>
        {showQRModal && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-sm w-full p-6 text-center space-y-4"
            >
              <h3 className="text-base font-bold text-gray-900 dark:text-white">
                Scan to Save Contact
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Point any smartphone camera at this code to automatically prompt saving {fullName} to address book.
              </p>
              <div className="p-4 bg-white rounded-2xl border inline-block shadow-sm">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                    generateVCFText()
                  )}`}
                  alt="vCard QR"
                  className="w-48 h-48 mx-auto"
                />
              </div>
              <div className="flex justify-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={handleSaveToContacts}
                  className="btn-secondary text-xs flex items-center gap-1.5"
                >
                  <BsDownload /> Download .vcf
                </button>
                <button
                  type="button"
                  onClick={() => setShowQRModal(false)}
                  className="btn-primary text-xs"
                >
                  Done
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
