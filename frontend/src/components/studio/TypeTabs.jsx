import { useState, useMemo } from 'react'
import {
  BsLink45Deg, BsCardText, BsWifi, BsPersonVcard, BsWhatsapp,
  BsChatText, BsEnvelope, BsTelephone, BsGeoAlt, BsCalendarEvent,
  BsCurrencyBitcoin, BsCreditCard, BsApple, BsSearch, BsQrCode
} from 'react-icons/bs'

const TYPE_ICONS = {
  url: BsLink45Deg,
  text: BsCardText,
  wifi: BsWifi,
  vcard: BsPersonVcard,
  whatsapp: BsWhatsapp,
  sms: BsChatText,
  email: BsEnvelope,
  phone: BsTelephone,
  location: BsGeoAlt,
  event: BsCalendarEvent,
  upi: BsCreditCard,
  bitcoin: BsCurrencyBitcoin,
  ethereum: BsCurrencyBitcoin,
  appstore: BsApple,
}

const CATEGORIES = [
  { id: 'all', label: 'All Types' },
  { id: 'essentials', label: 'Essentials' },
  { id: 'social', label: 'Social & Contact' },
  { id: 'finance', label: 'Finance & Crypto' },
  { id: 'business', label: 'Business & Event' },
]

export default function TypeTabs({ types = [], selectedType, onSelect }) {
  const [activeCategory, setActiveCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const getCategoryForType = (key) => {
    if (['url', 'text', 'wifi'].includes(key)) return 'essentials'
    if (['vcard', 'whatsapp', 'sms', 'email', 'phone', 'location'].includes(key)) return 'social'
    if (['upi', 'bitcoin', 'ethereum', 'crypto'].includes(key)) return 'finance'
    return 'business'
  }

  const filteredTypes = useMemo(() => {
    return types.filter((t) => {
      const matchesCategory = activeCategory === 'all' || getCategoryForType(t.key) === activeCategory
      const matchesSearch = !searchQuery || t.label.toLowerCase().includes(searchQuery.toLowerCase()) || t.key.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesCategory && matchesSearch
    })
  }, [types, activeCategory, searchQuery])

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary-500 animate-pulse" />
            1. Select QR Data Type
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Choose what content will be encoded into your QR code
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-56">
          <BsSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-xs" />
          <input
            type="text"
            placeholder="Search types..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field pl-8 py-1.5 text-xs"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all duration-150 ${
              activeCategory === cat.id
                ? 'bg-primary-600 text-white shadow-sm shadow-primary-500/30'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white bg-slate-100 dark:bg-white/[0.04]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Type Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2.5 max-h-56 overflow-y-auto pr-1">
        {filteredTypes.map((t) => {
          const Icon = TYPE_ICONS[t.key] || BsQrCode
          const isSelected = selectedType === t.key
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => onSelect(t.key)}
              className={`p-3 rounded-xl border text-left flex flex-col items-start gap-1.5 transition-all duration-200 group relative overflow-hidden ${
                isSelected
                  ? 'border-primary-500 bg-primary-500/10 dark:bg-primary-500/15 shadow-sm shadow-primary-500/20 ring-1 ring-primary-500'
                  : 'border-slate-200/80 dark:border-white/[0.07] bg-white/50 dark:bg-white/[0.02] hover:border-primary-400/50 hover:bg-slate-50 dark:hover:bg-white/[0.04]'
              }`}
            >
              <div className={`p-2 rounded-lg transition-colors ${
                isSelected
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 dark:bg-white/[0.06] text-slate-700 dark:text-slate-300 group-hover:text-primary-500'
              }`}>
                <Icon className="text-base" />
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 leading-tight">
                  {t.label}
                </p>
                <p className="text-[10px] text-slate-400 dark:text-slate-500 truncate max-w-[100px]">
                  {t.key.toUpperCase()}
                </p>
              </div>
              {isSelected && (
                <div className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-primary-500" />
              )}
            </button>
          )
        })}
        {filteredTypes.length === 0 && (
          <div className="col-span-full py-6 text-center text-xs text-slate-400">
            No QR types found matching "{searchQuery}"
          </div>
        )}
      </div>
    </div>
  )
}
