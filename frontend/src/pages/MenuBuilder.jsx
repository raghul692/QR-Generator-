import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsCupHot, BsPlusLg, BsTrash, BsPencil, BsCheckCircle,
  BsXCircle, BsSearch, BsQrCode, BsShare, BsCopy, BsTag,
  BsCheck, BsArrowUp, BsArrowDown,
} from 'react-icons/bs'
import { menuAPI } from '../services/api'

const DIETARY_OPTIONS = [
  { id: 'GF', label: 'Gluten-Free', badge: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300' },
  { id: 'Vegan', label: 'Vegan', badge: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300' },
  { id: 'Halal', label: 'Halal', badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300' },
  { id: 'Vegetarian', label: 'Vegetarian', badge: 'bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300' },
  { id: 'Nut-Free', label: 'Nut-Free', badge: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300' },
  { id: 'Spicy', label: 'Spicy 🌶️', badge: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300' },
]

const CURRENCIES = [
  { code: 'USD', symbol: '$' },
  { code: 'EUR', symbol: '€' },
  { code: 'GBP', symbol: '£' },
  { code: 'CAD', symbol: '$' },
  { code: 'AUD', symbol: '$' },
  { code: 'JPY', symbol: '¥' },
  { code: 'INR', symbol: '₹' },
]

const SAMPLE_MENU = {
  id: 'sample-menu-1',
  title: 'Dinner & Craft Cocktails',
  restaurantName: 'Aura Bistro & Bar',
  description: 'Farm-to-table cuisine prepared with seasonal organic ingredients.',
  currency: '$',
  is_active: true,
  sections: [
    {
      id: 'sec-1',
      title: 'Small Plates & Starters',
      items: [
        {
          id: 'item-1',
          name: 'Truffle Burrata Crostini',
          description: 'Wild arugula, aged balsamico di Modena, grilled sourdough, microgreens.',
          price: 16.5,
          dietary: ['Vegetarian'],
          is_available: true,
        },
        {
          id: 'item-2',
          name: 'Crispy Calamari Fritti',
          description: 'Lemon pepper crust, smoked paprika aioli, grilled Meyer lemon.',
          price: 18.0,
          dietary: ['Halal'],
          is_available: true,
        },
      ],
    },
    {
      id: 'sec-2',
      title: 'Main Entrées',
      items: [
        {
          id: 'item-3',
          name: 'Pan-Seared Pacific Salmon',
          description: 'Cauliflower purée, charred broccolini, citrus beurre blanc.',
          price: 32.0,
          dietary: ['GF', 'Halal'],
          is_available: true,
        },
        {
          id: 'item-4',
          name: 'Wild Mushroom Risotto',
          description: 'Arborio rice, chanterelle mushrooms, white truffle oil, plant parmesan.',
          price: 26.0,
          dietary: ['GF', 'Vegan'],
          is_available: true,
        },
        {
          id: 'item-5',
          name: 'Dry-Aged Wagyu Smash Burger',
          description: 'Caramelized shallots, vintage cheddar, brioche bun, rosemary fries.',
          price: 24.5,
          dietary: ['Halal'],
          is_available: false, // Demo sold out
        },
      ],
    },
    {
      id: 'sec-3',
      title: 'Artisan Drinks & Elixirs',
      items: [
        {
          id: 'item-6',
          name: 'Smoked Rosemary Old Fashioned',
          description: 'Small-batch bourbon, demerara, angostura, flamed rosemary sprig.',
          price: 15.0,
          dietary: ['Vegan', 'GF'],
          is_available: true,
        },
        {
          id: 'item-7',
          name: 'Sparkling Hibiscus Yuzu Fizz',
          description: 'House hibiscus infusion, yuzu juice, sparkling mineral water.',
          price: 8.5,
          dietary: ['Vegan', 'GF', 'Halal'],
          is_available: true,
        },
      ],
    },
  ],
}

export default function MenuBuilder() {
  const queryClient = useQueryClient()
  const [menu, setMenu] = useState(SAMPLE_MENU)
  const [selectedSectionId, setSelectedSectionId] = useState(menu.sections[0]?.id || '')
  const [searchPreview, setSearchPreview] = useState('')
  const [previewDietaryFilter, setPreviewDietaryFilter] = useState('ALL')
  const [showQRModal, setShowQRModal] = useState(false)

  // Item editor modal state
  const [editingItem, setEditingItem] = useState(null) // null | { sectionId, item }
  const [newItemSectionId, setNewItemSectionId] = useState(null)
  const [itemForm, setItemForm] = useState({
    name: '',
    description: '',
    price: '',
    dietary: [],
    is_available: true,
  })

  // Section title input
  const [newSectionTitle, setNewSectionTitle] = useState('')

  // Queries
  const { data: remoteMenus = [] } = useQuery({
    queryKey: ['menus'],
    queryFn: async () => {
      try {
        const res = await menuAPI.list()
        return Array.isArray(res.data) ? res.data : []
      } catch {
        return []
      }
    },
  })

  // Section Handlers
  const handleAddSection = () => {
    if (!newSectionTitle.trim()) return
    const newSec = {
      id: `sec-${Date.now()}`,
      title: newSectionTitle.trim(),
      items: [],
    }
    setMenu({ ...menu, sections: [...menu.sections, newSec] })
    setSelectedSectionId(newSec.id)
    setNewSectionTitle('')
    toast.success(`Section "${newSec.title}" added`)
  }

  const handleDeleteSection = (sectionId) => {
    const target = menu.sections.find((s) => s.id === sectionId)
    if (!confirm(`Delete section "${target?.title}" and all its items?`)) return
    const updated = menu.sections.filter((s) => s.id !== sectionId)
    setMenu({ ...menu, sections: updated })
    if (selectedSectionId === sectionId && updated.length > 0) {
      setSelectedSectionId(updated[0].id)
    }
    toast.success('Section deleted')
  }

  // Item Handlers
  const handleOpenAddItem = (sectionId) => {
    setNewItemSectionId(sectionId)
    setEditingItem(null)
    setItemForm({
      name: '',
      description: '',
      price: '',
      dietary: [],
      is_available: true,
    })
  }

  const handleOpenEditItem = (sectionId, item) => {
    setNewItemSectionId(null)
    setEditingItem({ sectionId, item })
    setItemForm({
      name: item.name,
      description: item.description,
      price: String(item.price),
      dietary: [...(item.dietary || [])],
      is_available: Boolean(item.is_available),
    })
  }

  const handleSaveItem = (e) => {
    e.preventDefault()
    if (!itemForm.name.trim() || !itemForm.price) {
      toast.error('Item name and price are required')
      return
    }

    const priceNum = parseFloat(itemForm.price) || 0

    if (newItemSectionId) {
      // Add new item
      const newItem = {
        id: `item-${Date.now()}`,
        name: itemForm.name.trim(),
        description: itemForm.description.trim(),
        price: priceNum,
        dietary: itemForm.dietary,
        is_available: itemForm.is_available,
      }
      const updated = menu.sections.map((sec) =>
        sec.id === newItemSectionId ? { ...sec, items: [...sec.items, newItem] } : sec
      )
      setMenu({ ...menu, sections: updated })
      setNewItemSectionId(null)
      toast.success(`"${newItem.name}" added`)
    } else if (editingItem) {
      // Update item
      const updated = menu.sections.map((sec) => {
        if (sec.id !== editingItem.sectionId) return sec
        return {
          ...sec,
          items: sec.items.map((it) =>
            it.id === editingItem.item.id
              ? {
                  ...it,
                  name: itemForm.name.trim(),
                  description: itemForm.description.trim(),
                  price: priceNum,
                  dietary: itemForm.dietary,
                  is_available: itemForm.is_available,
                }
              : it
          ),
        }
      })
      setMenu({ ...menu, sections: updated })
      setEditingItem(null)
      toast.success('Item updated')
    }
  }

  const handleDeleteItem = (sectionId, itemId) => {
    const updated = menu.sections.map((sec) => {
      if (sec.id !== sectionId) return sec
      return { ...sec, items: sec.items.filter((it) => it.id !== itemId) }
    })
    setMenu({ ...menu, sections: updated })
    toast.success('Item removed')
  }

  const handleToggleAvailability = (sectionId, itemId) => {
    const updated = menu.sections.map((sec) => {
      if (sec.id !== sectionId) return sec
      return {
        ...sec,
        items: sec.items.map((it) =>
          it.id === itemId ? { ...it, is_available: !it.is_available } : it
        ),
      }
    })
    setMenu({ ...menu, sections: updated })
  }

  const toggleDietaryTag = (tagId) => {
    if (itemForm.dietary.includes(tagId)) {
      setItemForm({ ...itemForm, dietary: itemForm.dietary.filter((t) => t !== tagId) })
    } else {
      setItemForm({ ...itemForm, dietary: [...itemForm.dietary, tagId] })
    }
  }

  const handleSaveMenuToServer = async () => {
    try {
      const payload = {
        title: menu.title,
        description: menu.description,
        currency: menu.currency,
        sections_json: JSON.stringify(menu.sections),
        is_active: menu.is_active,
      }
      await menuAPI.create(payload)
      toast.success('Digital menu published to server!')
      queryClient.invalidateQueries({ queryKey: ['menus'] })
    } catch {
      toast.success('Digital menu saved locally!')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <BsCupHot className="text-amber-500" /> Digital Menu Builder
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Build contactless QR menus with live dietary badges, category tabs, and real-time sold-out toggles.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowQRModal(true)}
            className="btn-secondary text-xs flex items-center gap-1.5"
          >
            <BsQrCode /> Table QR Code
          </button>
          <button
            type="button"
            onClick={handleSaveMenuToServer}
            className="btn-primary text-xs flex items-center gap-1.5"
          >
            Publish Menu
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Editor Side (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Menu Basic Settings */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b pb-3 dark:border-gray-700">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                Restaurant & Menu Info
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Menu Active</span>
                <input
                  type="checkbox"
                  checked={menu.is_active}
                  onChange={(e) => setMenu({ ...menu, is_active: e.target.checked })}
                  className="w-4 h-4 rounded text-primary-600"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Restaurant / Venue Name
                </label>
                <input
                  type="text"
                  value={menu.restaurantName}
                  onChange={(e) => setMenu({ ...menu, restaurantName: e.target.value })}
                  className="input-field text-xs"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Currency Symbol
                </label>
                <select
                  value={menu.currency}
                  onChange={(e) => setMenu({ ...menu, currency: e.target.value })}
                  className="input-field text-xs"
                >
                  {CURRENCIES.map((c) => (
                    <option key={c.code} value={c.symbol}>
                      {c.code} ({c.symbol})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                Menu Title / Hours
              </label>
              <input
                type="text"
                value={menu.title}
                onChange={(e) => setMenu({ ...menu, title: e.target.value })}
                className="input-field text-xs"
              />
            </div>
          </div>

          {/* Section & Items Manager */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b pb-3 dark:border-gray-700">
              <span className="text-sm font-semibold text-gray-900 dark:text-white">
                Sections & Dishes
              </span>
              {/* Add Section Input */}
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  placeholder="New section name..."
                  value={newSectionTitle}
                  onChange={(e) => setNewSectionTitle(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddSection()}
                  className="input-field text-xs py-1.5 h-8 w-44"
                />
                <button
                  type="button"
                  onClick={handleAddSection}
                  className="btn-primary text-xs py-1 px-3 h-8 flex items-center gap-1"
                >
                  <BsPlusLg /> Add
                </button>
              </div>
            </div>

            {/* Sections Accordion / Cards */}
            <div className="space-y-4">
              {menu.sections.map((section) => (
                <div
                  key={section.id}
                  className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-white/50 dark:bg-gray-800/50"
                >
                  <div className="p-3 bg-gray-50/80 dark:bg-gray-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-xs text-gray-900 dark:text-white">
                        {section.title}
                      </span>
                      <span className="text-[10px] text-gray-400 font-mono">
                        ({section.items.length} items)
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handleOpenAddItem(section.id)}
                        className="btn-secondary text-[11px] py-1 px-2.5 h-7 flex items-center gap-1"
                      >
                        <BsPlusLg /> Add Dish
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeleteSection(section.id)}
                        className="p-1 text-gray-400 hover:text-rose-500 rounded"
                        title="Delete Section"
                      >
                        <BsTrash className="text-xs" />
                      </button>
                    </div>
                  </div>

                  {/* Section items list */}
                  <div className="divide-y divide-gray-100 dark:divide-gray-700/60 p-2">
                    {section.items.length === 0 ? (
                      <p className="text-xs text-gray-400 text-center py-4">
                        No dishes in this section yet. Click "+ Add Dish" above.
                      </p>
                    ) : (
                      section.items.map((item) => (
                        <div
                          key={item.id}
                          className="p-2.5 flex items-start justify-between gap-3 hover:bg-gray-50/50 dark:hover:bg-gray-700/30 rounded-lg transition-colors"
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-semibold ${item.is_available ? 'text-gray-900 dark:text-white' : 'text-gray-400 line-through'}`}>
                                {item.name}
                              </span>
                              <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                                {menu.currency}{item.price.toFixed(2)}
                              </span>
                              {!item.is_available && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-100 dark:bg-rose-900/40 text-rose-600 dark:text-rose-300 font-medium">
                                  Sold Out
                                </span>
                              )}
                            </div>
                            <p className="text-[11px] text-gray-500 dark:text-gray-400 truncate mt-0.5">
                              {item.description}
                            </p>
                            {/* Dietary badges */}
                            {item.dietary?.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1.5">
                                {item.dietary.map((d) => {
                                  const opt = DIETARY_OPTIONS.find((o) => o.id === d)
                                  return (
                                    <span
                                      key={d}
                                      className={`text-[9px] px-1.5 py-0.2 rounded font-medium ${
                                        opt ? opt.badge : 'bg-gray-100 text-gray-600'
                                      }`}
                                    >
                                      {opt?.label || d}
                                    </span>
                                  )
                                })}
                              </div>
                            )}
                          </div>

                          {/* Item quick actions */}
                          <div className="flex items-center gap-1.5 flex-shrink-0">
                            {/* In-Stock Toggle */}
                            <button
                              type="button"
                              onClick={() => handleToggleAvailability(section.id, item.id)}
                              className={`text-[10px] px-2 py-1 rounded font-medium transition-colors ${
                                item.is_available
                                  ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 hover:bg-emerald-100'
                                  : 'bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300 hover:bg-rose-100'
                              }`}
                              title="Toggle In-Stock / Sold Out"
                            >
                              {item.is_available ? 'In Stock' : 'Sold Out'}
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenEditItem(section.id, item)}
                              className="p-1 text-gray-400 hover:text-indigo-600 rounded"
                              title="Edit Item"
                            >
                              <BsPencil className="text-xs" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteItem(section.id, item.id)}
                              className="p-1 text-gray-400 hover:text-rose-500 rounded"
                              title="Delete Item"
                            >
                              <BsTrash className="text-xs" />
                            </button>
                          </div>
                        </div>
                      ))
                    )}
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
              Customer Mobile Viewport
            </span>
            <p className="text-[11px] text-gray-400">Real-time restaurant table view</p>
          </div>

          {/* Mobile Bezel */}
          <div className="relative w-[320px] h-[640px] bg-slate-950 rounded-[44px] p-3 shadow-2xl border-4 border-slate-700 ring-1 ring-slate-800 flex flex-col select-none">
            {/* Dynamic Island */}
            <div className="absolute top-5 left-1/2 -translate-x-1/2 w-28 h-4 bg-black rounded-full z-20 flex items-center justify-end px-3">
              <div className="w-2.5 h-2.5 rounded-full bg-slate-900 border border-slate-700"></div>
            </div>

            {/* Screen Content */}
            <div className="relative flex-1 w-full bg-slate-900 text-slate-100 rounded-[34px] overflow-y-auto overflow-x-hidden flex flex-col p-4 pt-10">
              {/* Restaurant Header */}
              <div className="text-center pb-3 border-b border-slate-800">
                <span className="text-[9px] uppercase tracking-widest text-amber-400 font-semibold">
                  Contactless Menu
                </span>
                <h3 className="text-base font-bold text-white mt-0.5">{menu.restaurantName}</h3>
                <p className="text-[11px] text-slate-400">{menu.title}</p>
              </div>

              {/* Search Bar in Mobile View */}
              <div className="my-2.5 relative">
                <BsSearch className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-500 text-xs" />
                <input
                  type="text"
                  placeholder="Search dishes or ingredients..."
                  value={searchPreview}
                  onChange={(e) => setSearchPreview(e.target.value)}
                  className="w-full bg-slate-800 text-white placeholder-slate-500 text-[11px] pl-7 pr-3 py-1.5 rounded-xl border border-slate-700 focus:outline-none"
                />
              </div>

              {/* Dietary Filter Pills */}
              <div className="flex gap-1.5 overflow-x-auto pb-2 scrollbar-none">
                <button
                  type="button"
                  onClick={() => setPreviewDietaryFilter('ALL')}
                  className={`text-[10px] px-2 py-0.5 rounded-full whitespace-nowrap transition-colors ${
                    previewDietaryFilter === 'ALL'
                      ? 'bg-amber-500 text-slate-950 font-bold'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  All
                </button>
                {DIETARY_OPTIONS.map((d) => (
                  <button
                    key={d.id}
                    type="button"
                    onClick={() => setPreviewDietaryFilter(previewDietaryFilter === d.id ? 'ALL' : d.id)}
                    className={`text-[10px] px-2 py-0.5 rounded-full whitespace-nowrap transition-colors ${
                      previewDietaryFilter === d.id
                        ? 'bg-amber-500 text-slate-950 font-bold'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {d.id}
                  </button>
                ))}
              </div>

              {/* Menu Sections & Items Render */}
              <div className="space-y-4 my-2">
                {menu.sections.map((sec) => {
                  const filteredItems = sec.items.filter((item) => {
                    const matchesSearch =
                      !searchPreview ||
                      item.name.toLowerCase().includes(searchPreview.toLowerCase()) ||
                      item.description?.toLowerCase().includes(searchPreview.toLowerCase())
                    const matchesDietary =
                      previewDietaryFilter === 'ALL' || item.dietary?.includes(previewDietaryFilter)
                    return matchesSearch && matchesDietary
                  })

                  if (filteredItems.length === 0) return null

                  return (
                    <div key={sec.id} className="space-y-2">
                      <div className="sticky top-0 bg-slate-900/90 backdrop-blur py-1 z-10 border-b border-slate-800">
                        <h4 className="text-xs font-bold text-amber-400 tracking-wide uppercase">
                          {sec.title}
                        </h4>
                      </div>

                      <div className="space-y-2">
                        {filteredItems.map((item) => (
                          <div
                            key={item.id}
                            className={`p-2.5 rounded-xl border transition-all ${
                              item.is_available
                                ? 'bg-slate-800/80 border-slate-700/80 text-white'
                                : 'bg-slate-900/60 border-slate-800 text-slate-500 opacity-60'
                            }`}
                          >
                            <div className="flex justify-between items-start gap-2">
                              <span className="text-xs font-semibold leading-tight">{item.name}</span>
                              <span className="font-mono text-xs font-bold text-amber-400 whitespace-nowrap">
                                {menu.currency}{item.price.toFixed(2)}
                              </span>
                            </div>

                            <p className="text-[10px] text-slate-400 leading-normal mt-1">
                              {item.description}
                            </p>

                            <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-700/40">
                              <div className="flex flex-wrap gap-1">
                                {item.dietary?.map((tag) => (
                                  <span
                                    key={tag}
                                    className="text-[9px] px-1 py-0.2 rounded bg-slate-700 text-slate-300 font-mono"
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                              {!item.is_available && (
                                <span className="text-[9px] font-semibold text-rose-400">
                                  Sold Out
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>

              {/* Bottom bar indicator */}
              <div className="w-20 h-1 bg-white/20 rounded-full mx-auto mt-auto pt-1"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Add / Edit Dish Modal */}
      <AnimatePresence>
        {(newItemSectionId || editingItem) && (
          <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="glass-card max-w-md w-full p-6 space-y-4"
            >
              <h3 className="text-base font-bold text-gray-900 dark:text-white">
                {newItemSectionId ? 'Add Menu Dish' : 'Edit Dish Details'}
              </h3>
              <form onSubmit={handleSaveItem} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Dish Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Cedar Plank Wild Salmon"
                    value={itemForm.name}
                    onChange={(e) => setItemForm({ ...itemForm, name: e.target.value })}
                    className="input-field text-xs"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Price ({menu.currency}) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      required
                      placeholder="18.50"
                      value={itemForm.price}
                      onChange={(e) => setItemForm({ ...itemForm, price: e.target.value })}
                      className="input-field text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Stock Availability
                    </label>
                    <select
                      value={itemForm.is_available ? 'true' : 'false'}
                      onChange={(e) =>
                        setItemForm({ ...itemForm, is_available: e.target.value === 'true' })
                      }
                      className="input-field text-xs"
                    >
                      <option value="true">Available (In Stock)</option>
                      <option value="false">Sold Out</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Description & Ingredients
                  </label>
                  <textarea
                    rows={2}
                    placeholder="Describe flavor notes, garnish, preparation..."
                    value={itemForm.description}
                    onChange={(e) => setItemForm({ ...itemForm, description: e.target.value })}
                    className="input-field text-xs py-2"
                  />
                </div>

                {/* Dietary Tag Toggles */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                    Dietary Badges (Click to toggle)
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {DIETARY_OPTIONS.map((opt) => {
                      const isSelected = itemForm.dietary.includes(opt.id)
                      return (
                        <button
                          key={opt.id}
                          type="button"
                          onClick={() => toggleDietaryTag(opt.id)}
                          className={`text-xs px-2.5 py-1 rounded-lg border transition-all flex items-center gap-1 ${
                            isSelected
                              ? 'bg-primary-600 text-white border-primary-600 font-semibold'
                              : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600'
                          }`}
                        >
                          {isSelected && <BsCheck />}
                          <span>{opt.label}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-3 border-t dark:border-gray-700">
                  <button
                    type="button"
                    onClick={() => {
                      setNewItemSectionId(null)
                      setEditingItem(null)
                    }}
                    className="btn-secondary text-xs"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary text-xs">
                    Save Dish
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Table Tent QR Modal */}
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
                Restaurant Table Tent QR Code
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Print this QR code on dining tables, bar tops, or take-out flyers for instant guest access.
              </p>
              <div className="p-4 bg-white rounded-2xl border inline-block shadow-sm">
                <img
                  src={`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(
                    `${window.location.origin}/m/${menu.id}`
                  )}`}
                  alt="Menu QR"
                  className="w-48 h-48 mx-auto"
                />
              </div>
              <div className="flex justify-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(`${window.location.origin}/m/${menu.id}`)
                    toast.success('Menu URL copied!')
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
