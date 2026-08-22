import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsSearch, BsTrash, BsStar, BsStarFill, BsDownload, BsArrowRepeat,
  BsFunnel, BsClockHistory,
} from 'react-icons/bs'
import { historyAPI, categoryAPI, qrAPI, exportAPI } from '../services/api'

export default function History() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')

  const handleDownloadStickerSheet = async () => {
    try {
      toast.loading('Generating printable sticker sheet...', { id: 'sticker' })
      const res = await exportAPI.stickerSheet()
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = 'qr_sticker_sheet.pdf'
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('Downloaded Printable Sticker Sheet (A4 PDF)', { id: 'sticker' })
    } catch (err) {
      toast.error('Failed to export sticker sheet: ' + err.message, { id: 'sticker' })
    }
  }
  const [qrType, setQrType] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [isFavorite, setIsFavorite] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryAPI.list().then((r) => r.data),
  })

  const { data, isLoading } = useQuery({
    queryKey: ['history', { search, qrType, categoryId, isFavorite, sortBy, sortOrder, page, pageSize }],
    queryFn: () => historyAPI.list({
      search: search || undefined,
      qr_type: qrType || undefined,
      category_id: categoryId || undefined,
      is_favorite: isFavorite === '' ? undefined : isFavorite === 'true',
      sort_by: sortBy,
      sort_order: sortOrder,
      page,
      page_size: pageSize,
    }).then((r) => r.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => historyAPI.delete(id),
    onSuccess: () => {
      toast.success('QR deleted')
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const favoriteMutation = useMutation({
    mutationFn: (id) => historyAPI.toggleFavorite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const regenerateMutation = useMutation({
    mutationFn: (id) => qrAPI.regenerate(id),
    onSuccess: () => {
      toast.success('QR regenerated')
      queryClient.invalidateQueries({ queryKey: ['history'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleDownload = async (id, fmt) => {
    try {
      const res = await qrAPI.download(id, fmt)
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `qr_${id}.${fmt}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success(`Downloaded as ${fmt.toUpperCase()}`)
      queryClient.invalidateQueries({ queryKey: ['history'] })
    } catch (err) {
      toast.error(err.message)
    }
  }

  const items = data?.items || []
  const totalPages = data?.total_pages || 1

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">QR History</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Search, filter, and manage your generated QR codes</p>
        </div>
        <button
          onClick={handleDownloadStickerSheet}
          className="btn-primary text-sm flex items-center gap-2 self-start sm:self-auto"
        >
          <BsDownload /> Printable Sticker Sheet (PDF)
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
          <div className="md:col-span-2 lg:col-span-2 relative">
            <BsSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Search..." value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              className="input-field pl-10" />
          </div>
          <select value={qrType} onChange={(e) => { setQrType(e.target.value); setPage(1) }} className="input-field">
            <option value="">All Types</option>
            <option value="url">URL</option>
            <option value="text">Text</option>
            <option value="email">Email</option>
            <option value="wifi">Wi-Fi</option>
            <option value="vcard">vCard</option>
            <option value="upi">UPI</option>
          </select>
          <select value={categoryId} onChange={(e) => { setCategoryId(e.target.value); setPage(1) }} className="input-field">
            <option value="">All Categories</option>
            {categories?.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select value={isFavorite} onChange={(e) => { setIsFavorite(e.target.value); setPage(1) }} className="input-field">
            <option value="">All</option>
            <option value="true">Favorites</option>
            <option value="false">Non-Favorites</option>
          </select>
          <select value={`${sortBy}-${sortOrder}`} onChange={(e) => {
            const [by, order] = e.target.value.split('-')
            setSortBy(by); setSortOrder(order)
          }} className="input-field">
            <option value="created_at-desc">Newest</option>
            <option value="created_at-asc">Oldest</option>
            <option value="title-asc">Title A-Z</option>
            <option value="download_count-desc">Most Downloaded</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-gray-400">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2">Loading...</p>
          </div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center">
            <BsClockHistory className="text-5xl text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No QR codes found. Generate some from the Generator page!</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="table-header">Title</th>
                  <th className="table-header">Type</th>
                  <th className="table-header">Category</th>
                  <th className="table-header">Downloads</th>
                  <th className="table-header">Created</th>
                  <th className="table-header">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {items.map((item) => (
                  <motion.tr
                    key={item.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="hover:bg-gray-50 dark:hover:bg-gray-800/50"
                  >
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <button onClick={() => favoriteMutation.mutate(item.id)}>
                          {item.is_favorite ? <BsStarFill className="text-yellow-400" /> : <BsStar className="text-gray-400" />}
                        </button>
                        <span className="font-medium">{item.title}</span>
                      </div>
                    </td>
                    <td className="table-cell">
                      <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 rounded text-xs font-medium">
                        {item.qr_type}
                      </span>
                    </td>
                    <td className="table-cell">{item.category_name || '—'}</td>
                    <td className="table-cell">{item.download_count}</td>
                    <td className="table-cell text-xs">{item.created_at?.split('T')[0]}</td>
                    <td className="table-cell">
                      <div className="flex gap-1">
                        <button onClick={() => handleDownload(item.id, 'png')} className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded" title="Download PNG">
                          <BsDownload className="text-gray-600 dark:text-gray-300" />
                        </button>
                        <button onClick={() => regenerateMutation.mutate(item.id)} className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded" title="Regenerate">
                          <BsArrowRepeat className="text-gray-600 dark:text-gray-300" />
                        </button>
                        <button onClick={() => { if (confirm('Delete this QR?')) deleteMutation.mutate(item.id) }} className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded" title="Delete">
                          <BsTrash className="text-red-500" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500">Page {page} of {totalPages} ({data?.total || 0} total)</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="btn-secondary text-sm disabled:opacity-50">Previous</button>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                className="btn-secondary text-sm disabled:opacity-50">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}