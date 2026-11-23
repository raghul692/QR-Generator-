import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsLink, BsPlusLg, BsTrash, BsPencil, BsArrowUp, BsArrowDown,
  BsQrCode, BsShare, BsCopy, BsInstagram, BsTwitter, BsLinkedin,
  BsGithub, BsEnvelope, BsGlobe, BsStar, BsStarFill, BsBoxArrowUpRight,
  BsCheckCircle,
} from 'react-icons/bs'

const BIO_THEMES = [
  {
    id: 'obsidian-dark',
    name: 'Obsidian Minimal',
    bg: 'bg-slate-950 text-white',
    card: 'bg-slate-900/90 hover:bg-slate-800 text-white border border-slate-800 shadow-sm',
    featuredCard: 'bg-slate-800 text-white border-2 border-indigo-500 shadow-md',
    avatarBg: 'bg-indigo-600 text-white',
    subtext: 'text-slate-400',
    socialColor: 'text-slate-400 hover:text-white',
  },
  {
    id: 'clean-editorial',
    name: 'Clean Editorial',
    bg: 'bg-[#faf9f5] text-slate-900',
    card: 'bg-white hover:bg-slate-50 text-slate-900 border border-slate-200 shadow-sm',
    featuredCard: 'bg-white text-slate-900 border-2 border-slate-900 shadow-md',
    avatarBg: 'bg-slate-900 text-white',
    subtext: 'text-slate-600',
    socialColor: 'text-slate-600 hover:text-slate-900',
  },
  {
    id: 'neo-brutalist',
    name: 'Neo-Brutalist',
    bg: 'bg-amber-50 text-slate-950',
    card: 'bg-white hover:bg-amber-100/60 text-slate-950 border-2 border-slate-900 shadow-[3px_3px_0px_0px_rgba(15,23,42,1)]',
    featuredCard: 'bg-yellow-300 text-slate-950 border-2 border-slate-900 shadow-[4px_4px_0px_0px_rgba(15,23,42,1)]',
    avatarBg: 'bg-slate-950 text-white border-2 border-slate-900',
    subtext: 'text-slate-700 font-medium',
    socialColor: 'text-slate-900 hover:scale-110',
  },
  {
    id: 'emerald-slate',
    name: 'Emerald Forest',
    bg: 'bg-emerald-950 text-emerald-50',
    card: 'bg-emerald-900/80 hover:bg-emerald-900 text-emerald-50 border border-emerald-800/80 shadow-sm',
    featuredCard: 'bg-emerald-800 text-emerald-50 border-2 border-emerald-400 shadow-md',
    avatarBg: 'bg-emerald-500 text-emerald-950 font-bold',
    subtext: 'text-emerald-300/80',
    socialColor: 'text-emerald-300 hover:text-emerald-100',
  },
  {
    id: 'warm-espresso',
    name: 'Espresso Sunset',
    bg: 'bg-stone-900 text-stone-100',
    card: 'bg-stone-800/80 hover:bg-stone-800 text-stone-100 border border-stone-700 shadow-sm',
    featuredCard: 'bg-stone-800 text-amber-300 border-2 border-amber-500 shadow-md',
    avatarBg: 'bg-amber-600 text-stone-950 font-bold',
    subtext: 'text-stone-400',
    socialColor: 'text-stone-400 hover:text-amber-300',
  },
]

const DEFAULT_LINKS = [
  {
    id: 'link-1',
    title: 'Listen to the Latest Podcast Episode',
    url: 'https://spotify.com',
    badge: '🎙️ Episode 42 Live',
    is_featured: true,
  },
  {
    id: 'link-2',
    title: 'Pre-Order My Architecture Guidebook',
    url: 'https://example.com/book',
    badge: '📚 Hardcover & PDF',
    is_featured: false,
  },
  {
    id: 'link-3',
    title: 'Schedule a 1-on-1 Consultation',
    url: 'https://cal.com',
    badge: '30-min strategy call',
    is_featured: false,
  },
  {
    id: 'link-4',
    title: 'GitHub Open Source Projects',
    url: 'https://github.com',
    badge: 'Code repositories & docs',
    is_featured: false,
  },
]

export default function LinkInBio() {
  const [showQRModal, setShowQRModal] = useState(false)
  const [profile, setProfile] = useState({
    name: 'Morgan Blake',
    handle: '@morganblake',
    bio: 'Software Architect, Open-Source Creator & Speaker. Building next-generation developer tooling.',
    avatarInitials: 'MB',
    theme: 'obsidian-dark',
    socials: {
      instagram: 'https://instagram.com',
      twitter: 'https://x.com',
      github: 'https://github.com',
      linkedin: 'https://linkedin.com',
      email: 'morgan@example.com',
      website: 'https://example.com',
    },
  })

  const [links, setLinks] = useState(DEFAULT_LINKS)

  // Link editor state
  const [editingLink, setEditingLink] = useState(null) // null | link object
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [linkForm, setLinkForm] = useState({
    title: '',
    url: '',
    badge: '',
    is_featured: false,
  })

  const currentTheme = BIO_THEMES.find((t) => t.id === profile.theme) || BIO_THEMES[0]

  // Reorder functions
  const handleMoveUp = (index) => {
    if (index === 0) return
    const updated = [...links]
    const temp = updated[index - 1]
    updated[index - 1] = updated[index]
    updated[index] = temp
    setLinks(updated)
  }

  const handleMoveDown = (index) => {
    if (index === links.length - 1) return
    const updated = [...links]
    const temp = updated[index + 1]
    updated[index + 1] = updated[index]
    updated[index] = temp
    setLinks(updated)
  }

  const handleDeleteLink = (id) => {
    setLinks(links.filter((l) => l.id !== id))
    toast.success('Link removed')
  }

  const handleToggleFeatured = (id) => {
    setLinks(
      links.map((l) => (l.id === id ? { ...l, is_featured: !l.is_featured } : l))
    )
  }

  const handleOpenAdd = () => {
    setIsAddingNew(true)
    setEditingLink(null)
    setLinkForm({ title: '', url: '', badge: '', is_featured: false })
  }

  const handleOpenEdit = (link) => {
    setEditingLink(link)
    setIsAddingNew(false)
    setLinkForm({
      title: link.title,
      url: link.url,
      badge: link.badge || '',
      is_featured: Boolean(link.is_featured),
    })
  }

  const handleSaveLinkForm = (e) => {
    e.preventDefault()
    if (!linkForm.title.trim() || !linkForm.url.trim()) {
      toast.error('Link title and URL are required')
      return
    }

    if (isAddingNew) {
      const newL = {
        id: `link-${Date.now()}`,
        title: linkForm.title.trim(),
        url: linkForm.url.trim(),
        badge: linkForm.badge.trim(),
        is_featured: linkForm.is_featured,
      }
      setLinks([...links, newL])
      setIsAddingNew(false)
      toast.success('Link added')
    } else if (editingLink) {
      setLinks(
        links.map((l) =>
          l.id === editingLink.id
            ? {
                ...l,
                title: linkForm.title.trim(),
                url: linkForm.url.trim(),
                badge: linkForm.badge.trim(),
                is_featured: linkForm.is_featured,
              }
            : l
        )
      )
      setEditingLink(null)
      toast.success('Link updated')
    }
  }

  const handleCopyBioURL = () => {
    const url = `${window.location.origin}/bio/${profile.handle.replace('@', '')}`
    navigator.clipboard.writeText(url)
    toast.success('Link-in-bio URL copied to clipboard!')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsLink className="text-indigo-600 dark:text-indigo-400" />
            Link-in-Bio Curator
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Curate and reorder all your essential links, media, and socials with live mobile viewport simulation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleCopyBioURL}
            className="btn-secondary text-xs flex items-center gap-1.5"
          >
            <BsCopy /> Copy Bio Link
          </button>
          <button
            type="button"
            onClick={() => setShowQRModal(true)}
            className="btn-primary text-xs flex items-center gap-1.5"
          >
            <BsQrCode /> Bio QR Code
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Editor Side (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Profile Details Card */}
          <div className="glass-card p-5 space-y-4">
            <div className="border-b pb-3 dark:border-gray-700">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                Bio Identity & Handle
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Display Name
                </label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  className="input-field text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Social Handle
                </label>
                <input
                  type="text"
                  value={profile.handle}
                  onChange={(e) => setProfile({ ...profile, handle: e.target.value })}
                  className="input-field text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Initials Badge
                </label>
                <input
                  type="text"
                  maxLength={3}
                  value={profile.avatarInitials}
                  onChange={(e) =>
                    setProfile({ ...profile, avatarInitials: e.target.value.toUpperCase() })
                  }
                  className="input-field text-xs"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Bio Description / Tagline
              </label>
              <textarea
                rows={2}
                value={profile.bio}
                onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                className="input-field text-xs py-2"
              />
            </div>

            {/* Theme Preset Selector */}
            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                Visual Theme Preset
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                {BIO_THEMES.map((theme) => (
                  <button
                    key={theme.id}
                    type="button"
                    onClick={() => setProfile({ ...profile, theme: theme.id })}
                    className={`p-2 rounded-xl border text-left transition-all ${
                      profile.theme === theme.id
                        ? 'border-indigo-600 ring-2 ring-indigo-500/20 bg-indigo-50/40 dark:bg-indigo-950/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <span className="block text-[11px] font-semibold text-gray-800 dark:text-gray-200 truncate">
                      {theme.name}
                    </span>
                    <div className={`h-4 mt-1 rounded ${theme.bg}`} />
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Reorderable Links Manager */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b pb-3 dark:border-gray-700">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                Links Hierarchy ({links.length})
              </span>
              <button
                type="button"
                onClick={handleOpenAdd}
                className="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
              >
                <BsPlusLg /> Add Link
              </button>
            </div>

            {/* Links list */}
            <div className="space-y-2">
              {links.map((link, index) => (
                <div
                  key={link.id}
                  className="p-3 bg-white/70 dark:bg-gray-800/70 border border-gray-200 dark:border-gray-700 rounded-xl flex items-center justify-between gap-3 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors"
                >
                  {/* Reorder buttons */}
                  <div className="flex flex-col gap-1 text-gray-400">
                    <button
                      type="button"
                      disabled={index === 0}
                      onClick={() => handleMoveUp(index)}
                      className="p-0.5 hover:text-indigo-600 disabled:opacity-20"
                      title="Move Up"
                    >
                      <BsArrowUp className="text-xs" />
                    </button>
                    <button
                      type="button"
                      disabled={index === links.length - 1}
                      onClick={() => handleMoveDown(index)}
                      className="p-0.5 hover:text-indigo-600 disabled:opacity-20"
                      title="Move Down"
                    >
                      <BsArrowDown className="text-xs" />
                    </button>
                  </div>

                  {/* Link Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-gray-900 dark:text-white truncate">
                        {link.title}
                      </span>
                      {link.is_featured && (
                        <span className="text-[10px] px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 font-semibold flex items-center gap-0.5">
                          <BsStarFill className="text-[9px]" /> Featured
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-primary-600 dark:text-primary-400 truncate mt-0.5">
                      {link.url}
                    </p>
                    {link.badge && (
                      <span className="text-[10px] text-gray-500 dark:text-gray-400 italic">
                        {link.badge}
                      </span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <button
                      type="button"
                      onClick={() => handleToggleFeatured(link.id)}
                      className={`p-1.5 rounded text-xs ${
                        link.is_featured
                          ? 'text-amber-500 hover:text-amber-600'
                          : 'text-gray-400 hover:text-gray-600'
                      }`}
                      title="Toggle Featured Highlight"
                    >
                      {link.is_featured ? <BsStarFill /> : <BsStar />}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleOpenEdit(link)}
                      className="p-1.5 text-gray-400 hover:text-indigo-600 rounded"
                      title="Edit Link"
                    >
                      <BsPencil className="text-xs" />
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteLink(link.id)}
                      className="p-1.5 text-gray-400 hover:text-rose-500 rounded"
                      title="Delete Link"
                    >
                      <BsTrash className="text-xs" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Live Mobile Device Preview Frame (5 cols) */}
        <div className="lg:col-span-5 flex flex-col items-center">
          <div className="text-center mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
              Visitor Mobile Viewport
            </span>
            <p className="text-[11px] text-gray-400">Interactive link-in-bio simulation</p>
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
              {/* Profile Header */}
              <div className="text-center pb-3">
                <div
                  className={`w-14 h-14 mx-auto rounded-2xl flex items-center justify-center font-bold text-lg shadow-md mb-2 ${currentTheme.avatarBg}`}
                >
                  {profile.avatarInitials}
                </div>
                <h3 className="text-sm font-bold tracking-tight">{profile.name}</h3>
                <p className={`text-[11px] font-mono mt-0.5 ${currentTheme.subtext}`}>
                  {profile.handle}
                </p>
                <p className={`text-[11px] leading-relaxed mt-2 px-2 ${currentTheme.subtext}`}>
                  {profile.bio}
                </p>
              </div>

              {/* Social Icons Bar */}
              <div className="flex justify-center items-center gap-3.5 my-2 text-base">
                {profile.socials.instagram && (
                  <a
                    href={profile.socials.instagram}
                    target="_blank"
                    rel="noreferrer"
                    className={`transition-colors ${currentTheme.socialColor}`}
                  >
                    <BsInstagram />
                  </a>
                )}
                {profile.socials.twitter && (
                  <a
                    href={profile.socials.twitter}
                    target="_blank"
                    rel="noreferrer"
                    className={`transition-colors ${currentTheme.socialColor}`}
                  >
                    <BsTwitter />
                  </a>
                )}
                {profile.socials.github && (
                  <a
                    href={profile.socials.github}
                    target="_blank"
                    rel="noreferrer"
                    className={`transition-colors ${currentTheme.socialColor}`}
                  >
                    <BsGithub />
                  </a>
                )}
                {profile.socials.linkedin && (
                  <a
                    href={profile.socials.linkedin}
                    target="_blank"
                    rel="noreferrer"
                    className={`transition-colors ${currentTheme.socialColor}`}
                  >
                    <BsLinkedin />
                  </a>
                )}
                {profile.socials.email && (
                  <a
                    href={`mailto:${profile.socials.email}`}
                    className={`transition-colors ${currentTheme.socialColor}`}
                  >
                    <BsEnvelope />
                  </a>
                )}
              </div>

              {/* Links Render Stack */}
              <div className="space-y-2.5 my-3">
                {links.map((link) => (
                  <a
                    key={link.id}
                    href={link.url}
                    target="_blank"
                    rel="noreferrer"
                    className={`block w-full min-h-[46px] p-3 rounded-xl transition-all text-center group active:scale-95 ${
                      link.is_featured ? currentTheme.featuredCard : currentTheme.card
                    }`}
                  >
                    <div className="flex items-center justify-between gap-1">
                      <span className="w-3" />
                      <span className="text-xs font-semibold truncate leading-tight">
                        {link.title}
                      </span>
                      <BsBoxArrowUpRight className="text-[10px] opacity-60 flex-shrink-0" />
                    </div>
                    {link.badge && (
                      <p className="text-[10px] opacity-75 mt-0.5 truncate">{link.badge}</p>
                    )}
                  </a>
                ))}
              </div>

              {/* Bottom Footer */}
              <div className="mt-auto pt-2 text-center">
                <span className="text-[9px] opacity-40 font-mono">
                  Curated with QRMaster
                </span>
                <div className="w-20 h-1 bg-current opacity-20 rounded-full mx-auto mt-2"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Add / Edit Link Modal */}
      <AnimatePresence>
        {(isAddingNew || editingLink) && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-md w-full p-6 space-y-4"
            >
              <h3 className="text-base font-bold text-gray-900 dark:text-white">
                {isAddingNew ? 'Add Curated Link' : 'Edit Link Details'}
              </h3>
              <form onSubmit={handleSaveLinkForm} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Link Title *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Read My Latest Essay"
                    value={linkForm.title}
                    onChange={(e) => setLinkForm({ ...linkForm, title: e.target.value })}
                    className="input-field text-xs"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Destination URL *
                  </label>
                  <input
                    type="url"
                    required
                    placeholder="https://example.com/essay"
                    value={linkForm.url}
                    onChange={(e) => setLinkForm({ ...linkForm, url: e.target.value })}
                    className="input-field text-xs"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Subtext / Badge (Optional)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. 5-min read on Substack"
                    value={linkForm.badge}
                    onChange={(e) => setLinkForm({ ...linkForm, badge: e.target.value })}
                    className="input-field text-xs"
                  />
                </div>

                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="isFeatured"
                    checked={linkForm.is_featured}
                    onChange={(e) => setLinkForm({ ...linkForm, is_featured: e.target.checked })}
                    className="w-4 h-4 rounded text-indigo-600"
                  />
                  <label htmlFor="isFeatured" className="text-xs font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
                    Highlight as Featured Link (Special styling & visual emphasis)
                  </label>
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t dark:border-gray-700">
                  <button
                    type="button"
                    onClick={() => {
                      setIsAddingNew(false)
                      setEditingLink(null)
                    }}
                    className="btn-secondary text-xs"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary text-xs">
                    Save Link
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

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
                Scan for Link-in-Bio
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Share this QR code on physical business cards, social headers, or presentation slides.
              </p>
              <div className="p-4 bg-white rounded-2xl border inline-block shadow-sm">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                    `${window.location.origin}/bio/${profile.handle.replace('@', '')}`
                  )}`}
                  alt="Bio QR"
                  className="w-48 h-48 mx-auto"
                />
              </div>
              <div className="flex justify-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={handleCopyBioURL}
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
