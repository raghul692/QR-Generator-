import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { BsPlus, BsTrash, BsFolder, BsPencil } from 'react-icons/bs'
import { categoryAPI } from '../services/api'

export default function Categories() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({ name: '', description: '', icon: '', color: '#6366F1' })

  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryAPI.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data) => categoryAPI.create(data),
    onSuccess: () => {
      toast.success('Category created')
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setShowForm(false)
      setForm({ name: '', description: '', icon: '', color: '#6366F1' })
    },
    onError: (err) => toast.error(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => categoryAPI.update(id, data),
    onSuccess: () => {
      toast.success('Category updated')
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setEditing(null)
      setShowForm(false)
    },
    onError: (err) => toast.error(err.message),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => categoryAPI.delete(id),
    onSuccess: () => {
      toast.success('Category deleted')
      queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
    onError: (err) => toast.error(err.message),
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.name.trim()) {
      toast.error('Name is required')
      return
    }
    if (editing) {
      updateMutation.mutate({ id: editing, data: form })
    } else {
      createMutation.mutate(form)
    }
  }

  const handleEdit = (cat) => {
    setEditing(cat.id)
    setForm({ name: cat.name, description: cat.description || '', icon: cat.icon || '', color: cat.color || '#6366F1' })
    setShowForm(true)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Categories</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Organize your QR codes into categories</p>
        </div>
        <button onClick={() => { setShowForm(!showForm); setEditing(null); setForm({ name: '', description: '', icon: '', color: '#6366F1' }) }}
          className="btn-primary flex items-center gap-2">
          <BsPlus /> New Category
        </button>
      </div>

      {showForm && (
        <motion.form initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          onSubmit={handleSubmit} className="glass-card p-6 space-y-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {editing ? 'Edit Category' : 'Create Category'}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name *</label>
              <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input-field" placeholder="Category name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Color</label>
              <input type="color" value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })}
                className="w-full h-10 rounded-lg cursor-pointer" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
              <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="input-field" rows={2} placeholder="Optional description" />
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="btn-primary">{editing ? 'Update' : 'Create'}</button>
            <button type="button" onClick={() => { setShowForm(false); setEditing(null) }} className="btn-secondary">Cancel</button>
          </div>
        </motion.form>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <p className="text-gray-400">Loading...</p>
        ) : categories?.map((cat, i) => (
          <motion.div key={cat.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }} className="glass-card p-6">
            <div className="flex items-start justify-between mb-3">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ backgroundColor: cat.color + '20' }}>
                <BsFolder className="text-2xl" style={{ color: cat.color }} />
              </div>
              <div className="flex gap-1">
                <button onClick={() => handleEdit(cat)} className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded">
                  <BsPencil className="text-gray-600 dark:text-gray-300" />
                </button>
                {!cat.is_default && (
                  <button onClick={() => { if (confirm('Delete?')) deleteMutation.mutate(cat.id) }}
                    className="p-1.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded">
                    <BsTrash className="text-red-500" />
                  </button>
                )}
              </div>
            </div>
            <h3 className="font-semibold text-gray-900 dark:text-white">{cat.name}</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{cat.description || 'No description'}</p>
            <p className="text-xs text-gray-400 mt-2">{cat.qr_count} QR code(s)</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}