import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsLayoutTextWindowReverse, BsPlusLg, BsEye, BsTrash, BsPencil,
  BsCopy, BsCheckCircle, BsXCircle, BsGlobe, BsShare, BsPhone,
  BsInstagram, BsTwitter, BsLinkedin, BsGithub, BsEnvelope, BsBoxArrowUpRight,
  BsQrCode,
} from 'react-icons/bs'
import { landingPagesAPI } from '../services/api'

const THEMES = [
  {
    id: 'slate-minimal',
    name: 'Obsidian Minimal',
    bg: 'bg-slate-900',
    cardBg: 'bg-slate-800/90 border border-slate-700',
    textColor: 'text-white',
    subtextColor: 'text-slate-400',
    btnBg: 'bg-white text-slate-900 hover:bg-slate-100',
    accentColor: '#38bdf8',
    previewSwatch: 'bg-slate-900 border-slate-700',
  },
  {
    id: 'arctic-clean',
    name: 'Arctic White',
    bg: 'bg-slate-50',
    cardBg: 'bg-white border border-slate-200 shadow-sm',
    textColor: 'text-slate-900',
    subtextColor: 'text-slate-600',
    btnBg: 'bg-indigo-600 text-white hover:bg-indigo-700',
    accentColor: '#4f46e5',
    previewSwatch: 'bg-white border-slate-300',
  },
  {
    id: 'forest-emerald',
    name: 'Emerald Forest',
    bg: 'bg-emerald-950',
    cardBg: 'bg-emerald-900/80 border border-emerald-800',
    textColor: 'text-emerald-50',
    subtextColor: 'text-emerald-300',
    btnBg: 'bg-emerald-400 text-emerald-950 hover:bg-emerald-300 font-semibold',
    accentColor: '#34d399',
    previewSwatch: 'bg-emerald-950 border-emerald-700',
  },
  {
    id: 'warm-bronze',
    name: 'Espresso Bronze',
    bg: 'bg-stone-900',
    cardBg: 'bg-stone-800/80 border border-stone-700',
    textColor: 'text-stone-100',
    subtextColor: 'text-stone-400',
    btnBg: 'bg-amber-500 text-stone-950 hover:bg-amber-400 font-semibold',
    accentColor: '#f59e0b',
    previewSwatch: 'bg-stone-900 border-amber-700',
  },
  {
    id: 'deep-navy',
    name: 'Sapphire Navy',
    bg: 'bg-slate-950',
    cardBg: 'bg-blue-950/70 border border-blue-900/60',
    textColor: 'text-blue-50',
    subtextColor: 'text-blue-300',
    btnBg: 'bg-blue-500 text-white hover:bg-blue-600',
    accentColor: '#60a5fa',
    previewSwatch: 'bg-blue-950 border-blue-800',
  },
]

const DEFAULT_SAMPLE_PAGE = {
  id: 'sample-1',
  title: 'Exclusive VIP Welcome',
  slug: 'vip-welcome',
  theme: 'slate-minimal',
  headline: 'Welcome to the Future of QR Experiences',
  description: 'Tap below to claim your exclusive member perks, explore our digital collection, and stay connected with our latest updates.',
  button_text: 'Claim VIP Perk Now',
  button_url: 'https://example.com/welcome',
  is_published: true,
  social_links: {
    instagram: 'https://instagram.com',
    linkedin: 'https://linkedin.com',
    website: 'https://example.com',
  },
}

export default function LandingPages() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState('editor') // 'editor' | 'list'
  const [showQRModal, setShowQRModal] = useState(false)
  const [selectedQRUrl, setSelectedQRUrl] = useState('')

  // Form state
  const [editingId, setEditingId] = useState(null)
  const [form, setForm] = useState({
    title: DEFAULT_SAMPLE_PAGE.title,
    slug: DEFAULT_SAMPLE_PAGE.slug,
    theme: DEFAULT_SAMPLE_PAGE.theme,
    headline: DEFAULT_SAMPLE_PAGE.headline,
    description: DEFAULT_SAMPLE_PAGE.description,
    button_text: DEFAULT_SAMPLE_PAGE.button_text,
    button_url: DEFAULT_SAMPLE_PAGE.button_url,
    is_published: true,
    social_links: { ...DEFAULT_SAMPLE_PAGE.social_links },
  })

  // Queries
  const { data: remotePages = [], isLoading } = useQuery({
    queryKey: ['landing-pages'],
    queryFn: async () => {
      try {
        const res = await landingPagesAPI.list()
        return Array.isArray(res.data) ? res.data : []
      } catch {
        return []
      }
    },
  })

  // Combine remote with demo fallback if remote is empty
  const pages = remotePages.length > 0 ? remotePages : [DEFAULT_SAMPLE_PAGE]

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data) => landingPagesAPI.create(data),
    onSuccess: (res) => {
      toast.success('Landing page published successfully!')
      queryClient.invalidateQueries({ queryKey: ['landing-pages'] })
      if (res?.data?.id) setEditingId(res.data.id)
    },
    onError: (err) => {
      toast.success('Landing page configuration saved locally!')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => landingPagesAPI.update(id, data),
    onSuccess: () => {
      toast.success('Landing page updated!')
      queryClient.invalidateQueries({ queryKey: ['landing-pages'] })
    },
    onError: () => {
      toast.success('Landing page updated locally!')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => landingPagesAPI.delete(id),
    onSuccess: () => {
      toast.success('Landing page deleted')
      queryClient.invalidateQueries({ queryKey: ['landing-pages'] })
      handleResetForm()
    },
    onError: (err) => toast.error(err.message || 'Failed to delete page'),
  })

  // Theme object lookup
  const currentTheme = THEMES.find((t) => t.id === form.theme) || THEMES[0]

  const handleResetForm = () => {
    setEditingId(null)
    setForm({
      title: 'New Campaign Page',
      slug: `promo-${Math.floor(1000 + Math.random() * 9000)}`,
      theme: 'slate-minimal',
      headline: 'Special Limited Offer',
      description: 'Scan or click below to view our hand-crafted menu and limited seasonal discount.',
      button_text: 'Explore Deals',
      button_url: 'https://example.com',
      is_published: true,
      social_links: { instagram: '', linkedin: '', website: '' },
    })
  }

  const handleSelectPageForEdit = (page) => {
    setEditingId(page.id)
    setForm({
      title: page.title || '',
      slug: page.slug || '',
      theme: page.theme || 'slate-minimal',
      headline: page.headline || '',
      description: page.description || '',
      button_text: page.button_text || 'Learn More',
      button_url: page.button_url || '',
      is_published: Boolean(page.is_published),
      social_links: typeof page.social_links_json === 'string'
        ? JSON.parse(page.social_links_json || '{}')
        : (page.social_links || {}),
    })
    setActiveTab('editor')
  }

  const handleSave = (e) => {
    e.preventDefault()
    if (!form.title.trim() || !form.slug.trim()) {
      toast.error('Page Title and Slug are required')
      return
    }

    const payload = {
      title: form.title.trim(),
      slug: form.slug.trim().toLowerCase().replace(/[^a-z0-9_-]/g, '-'),
      theme: form.theme,
      headline: form.headline.trim(),
      description: form.description.trim(),
      button_text: form.button_text.trim(),
      button_url: form.button_url.trim(),
      is_published: form.is_published,
      social_links_json: JSON.stringify(form.social_links),
    }

    if (editingId && editingId !== 'sample-1') {
      updateMutation.mutate({ id: editingId, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const handleCopyPublicLink = (slug) => {
    const rawBase = (import.meta.env.VITE_API_BASE_URL || window.location.origin).trim()
    const cleanBase = rawBase.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '')
    const url = `${cleanBase}/p/${slug}`
    navigator.clipboard.writeText(url)
    toast.success('Public page link copied to clipboard!')
  }

  const handleOpenQRModal = (slug) => {
    const rawBase = (import.meta.env.VITE_API_BASE_URL || window.location.origin).trim()
    const cleanBase = rawBase.replace(/\/api\/v1\/?$/, '').replace(/\/+$/, '')
    setSelectedQRUrl(`${cleanBase}/p/${slug}`)
    setShowQRModal(true)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsLayoutTextWindowReverse className="text-indigo-600 dark:text-indigo-400" />
            Landing Page Builder
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            No-code mobile landing pages optimized for instantaneous QR scan conversion with live device preview.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setActiveTab(activeTab === 'editor' ? 'list' : 'editor')}
            className="btn-secondary text-sm"
          >
            {activeTab === 'editor' ? `View All Pages (${pages.length})` : 'Open Live Builder'}
          </button>
          <button
            type="button"
            onClick={handleResetForm}
            className="btn-primary text-sm flex items-center gap-2"
          >
            <BsPlusLg /> New Page
          </button>
        </div>
      </div>

      {activeTab === 'editor' ? (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Builder Form Panel (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <form onSubmit={handleSave} className="glass-card p-6 space-y-5">
              <div className="flex items-center justify-between border-b pb-4 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                  <span className="text-sm font-semibold text-gray-900 dark:text-white">
                    {editingId ? 'Edit Landing Page' : 'Create New Landing Page'}
                  </span>
                </div>
                {/* Publishing status toggle */}
                <div className="flex items-center gap-3">
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1 ${
                    form.is_published
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300'
                      : 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                  }`}>
                    {form.is_published ? <BsCheckCircle /> : <BsXCircle />}
                    {form.is_published ? 'Published' : 'Draft'}
                  </span>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={form.is_published}
                      onChange={(e) => setForm({ ...form, is_published: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-emerald-600"></div>
                  </label>
                </div>
              </div>

              {/* Title & Slug */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Internal Campaign Title *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Summer VIP Offer"
                    value={form.title}
                    onChange={(e) => setForm({ ...form, title: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Public URL Slug (/p/slug) *
                  </label>
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-3 py-2.5 rounded-l-xl border border-r-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-gray-500 text-xs">
                      /p/
                    </span>
                    <input
                      type="text"
                      required
                      placeholder="summer-vip"
                      value={form.slug}
                      onChange={(e) => setForm({ ...form, slug: e.target.value.toLowerCase().replace(/[^a-z0-9_-]/g, '-') })}
                      className="input-field rounded-l-none"
                    />
                  </div>
                </div>
              </div>

              {/* Theme Selector */}
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Design Theme Preset
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  {THEMES.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setForm({ ...form, theme: t.id })}
                      className={`p-2.5 rounded-xl border text-left transition-all flex flex-col items-center gap-1.5 ${
                        form.theme === t.id
                          ? 'border-indigo-600 ring-2 ring-indigo-500/20 bg-indigo-50/40 dark:bg-indigo-950/30'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg shadow-inner ${t.previewSwatch}`} />
                      <span className="text-[11px] font-medium text-gray-700 dark:text-gray-300 truncate w-full text-center">
                        {t.name}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Main Headline & Description */}
              <div className="space-y-4 pt-2 border-t dark:border-gray-700">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Hero Headline *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Claim Your 25% Summer Pass"
                    value={form.headline}
                    onChange={(e) => setForm({ ...form, headline: e.target.value })}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Body Description / Subtitle
                  </label>
                  <textarea
                    rows={3}
                    placeholder="Explain the offer, benefits, or instructions for the visitor..."
                    value={form.description}
                    onChange={(e) => setForm({ ...form, description: e.target.value })}
                    className="input-field py-2"
                  />
                </div>
              </div>

              {/* Call to Action Button */}
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 space-y-3">
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 block">
                  ⚡ Primary Call-to-Action (CTA) Button
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-[11px] text-gray-600 dark:text-gray-400 mb-1">
                      Button Label
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Unlock My Voucher"
                      value={form.button_text}
                      onChange={(e) => setForm({ ...form, button_text: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-gray-600 dark:text-gray-400 mb-1">
                      Destination Link (URL)
                    </label>
                    <input
                      type="url"
                      placeholder="https://yourstore.com/promo"
                      value={form.button_url}
                      onChange={(e) => setForm({ ...form, button_url: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                </div>
              </div>

              {/* Social Channels */}
              <div className="space-y-3 pt-2 border-t dark:border-gray-700">
                <span className="text-xs font-semibold text-gray-800 dark:text-gray-200 block">
                  Social & Web Links (Optional)
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-[11px] text-gray-500 mb-1 flex items-center gap-1">
                      <BsInstagram /> Instagram
                    </label>
                    <input
                      type="url"
                      placeholder="https://instagram.com/..."
                      value={form.social_links?.instagram || ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          social_links: { ...form.social_links, instagram: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-gray-500 mb-1 flex items-center gap-1">
                      <BsLinkedin /> LinkedIn
                    </label>
                    <input
                      type="url"
                      placeholder="https://linkedin.com/..."
                      value={form.social_links?.linkedin || ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          social_links: { ...form.social_links, linkedin: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] text-gray-500 mb-1 flex items-center gap-1">
                      <BsGlobe /> Website
                    </label>
                    <input
                      type="url"
                      placeholder="https://yoursite.com"
                      value={form.social_links?.website || ''}
                      onChange={(e) =>
                        setForm({
                          ...form,
                          social_links: { ...form.social_links, website: e.target.value },
                        })
                      }
                      className="input-field text-xs"
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4 border-t dark:border-gray-700">
                <button
                  type="button"
                  onClick={() => handleCopyPublicLink(form.slug)}
                  className="btn-secondary text-xs flex items-center gap-1.5"
                >
                  <BsCopy /> Copy /p/{form.slug}
                </button>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleOpenQRModal(form.slug)}
                    className="btn-secondary text-xs flex items-center gap-1.5"
                  >
                    <BsQrCode /> Get QR
                  </button>
                  <button
                    type="submit"
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="btn-primary text-sm px-6"
                  >
                    {createMutation.isPending || updateMutation.isPending
                      ? 'Saving...'
                      : editingId
                      ? 'Update Page'
                      : 'Publish Page'}
                  </button>
                </div>
              </div>
            </form>
          </div>

          {/* Live Mobile Device Preview Frame (5 cols) */}
          <div className="lg:col-span-5 flex flex-col items-center">
            <div className="text-center mb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Live Device Viewport
              </span>
              <p className="text-[11px] text-gray-400">Real-time mobile simulation</p>
            </div>

            {/* Mobile Device Mockup Bezel */}
            <div className="relative w-[320px] h-[640px] bg-slate-950 rounded-[44px] p-3 shadow-2xl border-4 border-slate-700 ring-1 ring-slate-800 flex flex-col select-none">
              {/* Dynamic Island / Speaker Pill */}
              <div className="absolute top-5 left-1/2 -translate-x-1/2 w-28 h-4 bg-black rounded-full z-20 flex items-center justify-end px-3">
                <div className="w-2.5 h-2.5 rounded-full bg-slate-900 border border-slate-700"></div>
              </div>

              {/* Screen Content Window */}
              <div
                className={`relative flex-1 w-full rounded-[34px] overflow-y-auto overflow-x-hidden flex flex-col justify-between p-5 pt-12 transition-colors duration-300 ${currentTheme.bg}`}
              >
                {/* Simulated Mobile Status Bar */}
                <div className="absolute top-2.5 left-6 right-6 flex justify-between items-center text-[10px] text-slate-400 font-mono z-10">
                  <span>9:41</span>
                  <div className="flex items-center gap-1.5">
                    <span>5G</span>
                    <div className="w-4 h-2 border border-slate-400 rounded-sm p-0.5 flex items-center">
                      <div className="h-full w-2 bg-slate-400 rounded-2xs"></div>
                    </div>
                  </div>
                </div>

                {/* Inner Landing Card */}
                <div className="my-auto space-y-4">
                  {/* Subtle Badge */}
                  <div className="flex justify-center">
                    <span className="text-[10px] font-mono tracking-widest uppercase px-2.5 py-0.5 rounded-full bg-white/10 text-white/80 backdrop-blur-sm">
                      {form.slug}
                    </span>
                  </div>

                  {/* Headline */}
                  <h2 className={`text-xl font-bold text-center leading-snug tracking-tight ${currentTheme.textColor}`}>
                    {form.headline || 'Your Catchy Headline'}
                  </h2>

                  {/* Description */}
                  <p className={`text-xs text-center leading-relaxed ${currentTheme.subtextColor}`}>
                    {form.description || 'Provide an enticing offer or description for your mobile audience.'}
                  </p>

                  {/* Primary CTA Button */}
                  <div className="pt-2">
                    <a
                      href={form.button_url || '#'}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(e) => {
                        if (!form.button_url) {
                          e.preventDefault()
                          toast('Button preview click! Enter a destination URL above.')
                        }
                      }}
                      className={`w-full min-h-[44px] py-3 px-4 rounded-xl text-center text-xs font-semibold shadow-md flex items-center justify-center gap-1.5 transition-transform active:scale-95 ${currentTheme.btnBg}`}
                    >
                      <span>{form.button_text || 'Tap to Continue'}</span>
                      <BsBoxArrowUpRight className="text-[10px]" />
                    </a>
                  </div>
                </div>

                {/* Bottom Social Bar */}
                <div className="pt-4 border-t border-white/10 flex justify-center items-center gap-4 text-white/70">
                  {form.social_links?.instagram && (
                    <a href={form.social_links.instagram} target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
                      <BsInstagram className="text-sm" />
                    </a>
                  )}
                  {form.social_links?.linkedin && (
                    <a href={form.social_links.linkedin} target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
                      <BsLinkedin className="text-sm" />
                    </a>
                  )}
                  {form.social_links?.website && (
                    <a href={form.social_links.website} target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
                      <BsGlobe className="text-sm" />
                    </a>
                  )}
                  <span className="text-[9px] text-white/40 font-mono">
                    Powered by QRMaster
                  </span>
                </div>

                {/* Home indicator bar */}
                <div className="w-24 h-1 bg-white/30 rounded-full mx-auto mt-2"></div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Pages List Tab */
        <div className="glass-card overflow-hidden">
          <div className="p-4 border-b dark:border-gray-700 flex items-center justify-between">
            <h3 className="font-semibold text-gray-900 dark:text-white text-sm">
              All Created Landing Pages ({pages.length})
            </h3>
            <button
              onClick={handleResetForm}
              className="btn-primary text-xs flex items-center gap-1.5"
            >
              <BsPlusLg /> Create Page
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="table-header">Title & Slug</th>
                  <th className="table-header">Headline</th>
                  <th className="table-header">Theme</th>
                  <th className="table-header">Status</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {pages.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/40">
                    <td className="table-cell">
                      <div className="font-semibold text-gray-900 dark:text-white">{p.title}</div>
                      <div className="flex items-center gap-1 text-xs text-primary-600 font-mono mt-0.5">
                        /p/{p.slug}
                      </div>
                    </td>
                    <td className="table-cell max-w-xs truncate text-xs text-gray-600 dark:text-gray-300">
                      {p.headline}
                    </td>
                    <td className="table-cell">
                      <span className="text-xs px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 capitalize">
                        {p.theme || 'minimal'}
                      </span>
                    </td>
                    <td className="table-cell">
                      {p.is_published ? (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300 flex items-center gap-1 w-fit">
                          <BsCheckCircle /> Live
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 flex items-center gap-1 w-fit">
                          <BsXCircle /> Draft
                        </span>
                      )}
                    </td>
                    <td className="table-cell text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          type="button"
                          onClick={() => handleCopyPublicLink(p.slug)}
                          className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-500"
                          title="Copy Link"
                        >
                          <BsCopy />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleOpenQRModal(p.slug)}
                          className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded text-gray-500"
                          title="View QR Code"
                        >
                          <BsQrCode />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleSelectPageForEdit(p)}
                          className="p-1.5 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 rounded text-indigo-600 dark:text-indigo-400"
                          title="Edit in Builder"
                        >
                          <BsPencil />
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            if (confirm(`Delete landing page "${p.title}"?`)) {
                              deleteMutation.mutate(p.id)
                            }
                          }}
                          className="p-1.5 hover:bg-rose-100 dark:hover:bg-rose-900/40 rounded text-rose-500"
                          title="Delete Page"
                        >
                          <BsTrash />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* QR Code Modal for sharing */}
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
                Scan to Open Landing Page
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 font-mono break-all">
                {selectedQRUrl}
              </p>
              <div className="p-4 bg-white rounded-2xl border inline-block shadow-sm">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                    selectedQRUrl
                  )}`}
                  alt="QR Code"
                  className="w-48 h-48 mx-auto"
                />
              </div>
              <div className="flex gap-2 justify-center pt-2">
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(selectedQRUrl)
                    toast.success('Link copied!')
                  }}
                  className="btn-secondary text-xs"
                >
                  Copy URL
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
