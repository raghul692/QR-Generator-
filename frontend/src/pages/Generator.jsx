import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  BsQrCode, BsDownload, BsEye, BsPalette, BsImage, BsCheck2,
} from 'react-icons/bs'
import { qrAPI, categoryAPI } from '../services/api'

export default function Generator() {
  const [selectedType, setSelectedType] = useState('url')
  const [formData, setFormData] = useState({})
  const [customization, setCustomization] = useState({
    size: 400,
    foreground_color: '#000000',
    background_color: '#FFFFFF',
    gradient_enabled: false,
    gradient_start: '#6366F1',
    gradient_end: '#8B5CF6',
    transparent_background: false,
    qr_style: 'square',
    margin: 4,
    border_thickness: 0,
    border_color: '#000000',
    error_correction: 'H',
    logo_size: 20,
    logo_position: 'center',
    logo_background: true,
  })
  const [previewBase64, setPreviewBase64] = useState(null)
  const [showCustomization, setShowCustomization] = useState(true)
  const [title, setTitle] = useState('')

  const { data: types } = useQuery({
    queryKey: ['qr-types'],
    queryFn: () => qrAPI.getTypes().then((r) => r.data),
  })

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryAPI.list().then((r) => r.data),
  })

  const currentType = types?.find((t) => t.key === selectedType)

  // Preview mutation
  const previewMutation = useMutation({
    mutationFn: (data) => qrAPI.preview(data),
    onSuccess: (res) => {
      setPreviewBase64(res.data.preview_base64)
    },
    onError: (err) => {
      toast.error(err.message)
    },
  })

  // Generate mutation
  const generateMutation = useMutation({
    mutationFn: (data) => qrAPI.generate(data),
    onSuccess: (res) => {
      setPreviewBase64(res.data.preview_base64)
      toast.success('QR code generated and saved to history!')
    },
    onError: (err) => {
      toast.error(err.message)
    },
  })

  // Auto-preview on form/type change
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentType) {
        previewMutation.mutate({
          qr_type: selectedType,
          data: formData,
          customization,
        })
      }
    }, 500)
    return () => clearTimeout(timer)
  }, [selectedType, formData, customization])

  const handleFieldChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleCustomChange = (name, value) => {
    setCustomization((prev) => ({ ...prev, [name]: value }))
  }

  const handleGenerate = () => {
    if (!title.trim()) {
      toast.error('Please enter a QR title')
      return
    }
    generateMutation.mutate({
      title,
      qr_type: selectedType,
      data: formData,
      customization,
      save_to_history: true,
    })
  }

  const handleDownload = (format) => {
    if (!generateMutation.data?.data?.id) {
      toast.error('Please generate the QR first')
      return
    }
    const id = generateMutation.data.data.id
    qrAPI.download(id, format).then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `qr_${selectedType}_${id}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success(`Downloaded as ${format.toUpperCase()}`)
    })
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">QR Code Generator</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">Generate customized QR codes for 30+ data types</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Type selector + form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Type selector */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Select QR Type</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-h-64 overflow-y-auto">
              {types?.map((t) => (
                <button
                  key={t.key}
                  onClick={() => {
                    setSelectedType(t.key)
                    setFormData({})
                  }}
                  className={`p-3 rounded-xl border-2 text-center transition-all ${
                    selectedType === t.key
                      ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/30'
                      : 'border-gray-200 dark:border-gray-700 hover:border-primary-300'
                  }`}
                >
                  <BsQrCode className="text-2xl mx-auto mb-1 text-primary-600" />
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300">{t.label}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Dynamic form */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {currentType?.label} Details
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  QR Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter a title for this QR code"
                  className="input-field"
                />
              </div>
              {currentType?.fields?.map((field) => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  {field.type === 'textarea' ? (
                    <textarea
                      value={formData[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      rows={3}
                      className="input-field"
                    />
                  ) : field.type === 'select' ? (
                    <select
                      value={formData[field.name] || field.default || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                      className="input-field"
                    >
                      {field.options?.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  ) : field.type === 'checkbox' ? (
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData[field.name] || false}
                        onChange={(e) => handleFieldChange(field.name, e.target.checked)}
                        className="w-5 h-5 rounded text-primary-600"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{field.label}</span>
                    </label>
                  ) : (
                    <input
                      type={field.type}
                      value={formData[field.name] || ''}
                      onChange={(e) => handleFieldChange(field.name, e.target.value)}
                      placeholder={field.placeholder}
                      className="input-field"
                    />
                  )}
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Category
                </label>
                <select
                  value={formData.category_id || ''}
                  onChange={(e) => handleFieldChange('category_id', e.target.value ? Number(e.target.value) : null)}
                  className="input-field"
                >
                  <option value="">No category</option>
                  {categories?.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Customization */}
          <div className="glass-card p-6">
            <button
              onClick={() => setShowCustomization(!showCustomization)}
              className="flex items-center justify-between w-full"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                <BsPalette /> Customization
              </h3>
              <span className="text-gray-400">{showCustomization ? '−' : '+'}</span>
            </button>
            {showCustomization && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4"
              >
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Size: {customization.size}px</label>
                  <input type="range" min="100" max="1000" step="50"
                    value={customization.size}
                    onChange={(e) => handleCustomChange('size', Number(e.target.value))}
                    className="w-full" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Error Correction</label>
                  <select value={customization.error_correction}
                    onChange={(e) => handleCustomChange('error_correction', e.target.value)}
                    className="input-field">
                    <option value="L">L (7%)</option>
                    <option value="M">M (15%)</option>
                    <option value="Q">Q (25%)</option>
                    <option value="H">H (30%)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Foreground Color</label>
                  <input type="color" value={customization.foreground_color}
                    onChange={(e) => handleCustomChange('foreground_color', e.target.value)}
                    className="w-full h-10 rounded-lg cursor-pointer" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Background Color</label>
                  <input type="color" value={customization.background_color}
                    onChange={(e) => handleCustomChange('background_color', e.target.value)}
                    className="w-full h-10 rounded-lg cursor-pointer" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">QR Style</label>
                  <select value={customization.qr_style}
                    onChange={(e) => handleCustomChange('qr_style', e.target.value)}
                    className="input-field">
                    <option value="square">Square</option>
                    <option value="rounded">Rounded</option>
                    <option value="circular">Circular</option>
                    <option value="dots">Dots</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Margin: {customization.margin}</label>
                  <input type="range" min="0" max="20"
                    value={customization.margin}
                    onChange={(e) => handleCustomChange('margin', Number(e.target.value))}
                    className="w-full" />
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={customization.gradient_enabled}
                    onChange={(e) => handleCustomChange('gradient_enabled', e.target.checked)}
                    className="w-5 h-5 rounded text-primary-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Gradient Foreground</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={customization.transparent_background}
                    onChange={(e) => handleCustomChange('transparent_background', e.target.checked)}
                    className="w-5 h-5 rounded text-primary-600" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Transparent Background</span>
                </label>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Decorative Frame</label>
                  <select value={customization.frame_style || 'none'}
                    onChange={(e) => handleCustomChange('frame_style', e.target.value)}
                    className="input-field">
                    <option value="none">None (Standard)</option>
                    <option value="badge">Badge Frame ("SCAN ME")</option>
                    <option value="banner">Banner Frame</option>
                    <option value="speech">Speech Bubble Frame</option>
                    <option value="rounded">Rounded Border Frame</option>
                  </select>
                </div>
                {customization.frame_style && customization.frame_style !== 'none' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Frame Text</label>
                      <input type="text" value={customization.frame_text || 'SCAN ME'}
                        onChange={(e) => handleCustomChange('frame_text', e.target.value)}
                        placeholder="SCAN ME" className="input-field" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Frame Color</label>
                      <input type="color" value={customization.frame_color || '#6366F1'}
                        onChange={(e) => handleCustomChange('frame_color', e.target.value)}
                        className="w-full h-10 rounded-lg cursor-pointer" />
                    </div>
                  </>
                )}

                {/* Logo Upload */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 flex items-center gap-1">
                    <BsImage /> Custom Center Logo
                  </label>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files[0]
                      if (file) {
                        const reader = new FileReader()
                        reader.onloadend = () => {
                          handleCustomChange('logo_url', reader.result)
                        }
                        reader.readAsDataURL(file)
                      }
                    }}
                    className="input-field text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
                  />
                  {customization.logo_url && (
                    <div className="mt-2 flex items-center gap-2">
                      <img src={customization.logo_url} alt="Logo preview" className="w-8 h-8 object-contain rounded border" />
                      <button
                        onClick={() => handleCustomChange('logo_url', null)}
                        className="text-xs text-red-500 hover:underline"
                      >
                        Remove Logo
                      </button>
                    </div>
                  )}
                </div>

                {/* Dynamic QR & Security */}
                <div className="md:col-span-2 border-t pt-4 mt-2">
                  <label className="flex items-center gap-2 cursor-pointer font-semibold text-gray-900 dark:text-white">
                    <input
                      type="checkbox"
                      checked={customization.is_dynamic || false}
                      onChange={(e) => handleCustomChange('is_dynamic', e.target.checked)}
                      className="w-5 h-5 rounded text-primary-600"
                    />
                    ⚡ Enable Dynamic QR (Redirectable & Scan Analytics)
                  </label>
                  <p className="text-xs text-gray-500 mt-1">Allows updating target destination after printing, plus real-time scan analytics.</p>
                </div>

                {customization.is_dynamic && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">🔒 Access Password (Optional)</label>
                      <input
                        type="password"
                        placeholder="Protect with PIN/Password"
                        value={customization.password || ''}
                        onChange={(e) => handleCustomChange('password', e.target.value)}
                        className="input-field"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">⏳ Expiration Date (Optional)</label>
                      <input
                        type="datetime-local"
                        value={customization.expires_at || ''}
                        onChange={(e) => handleCustomChange('expires_at', e.target.value)}
                        className="input-field"
                      />
                    </div>
                  </>
                )}
              </motion.div>
            )}
          </div>
        </div>

        {/* Right: Preview + actions */}
        <div className="space-y-6">
          <div className="glass-card p-6 sticky top-24">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <BsEye /> Live Preview
            </h3>
            <div className="flex justify-center bg-gray-50 dark:bg-gray-900 rounded-xl p-6 mb-4">
              {previewBase64 ? (
                <img src={previewBase64} alt="QR Preview" className="max-w-full h-auto rounded-lg" />
              ) : (
                <div className="w-48 h-48 flex items-center justify-center text-gray-400">
                  <BsQrCode className="text-6xl" />
                </div>
              )}
            </div>
            {previewMutation.isPending && (
              <p className="text-center text-sm text-gray-400 mb-4">Generating preview...</p>
            )}
            <button
              onClick={handleGenerate}
              disabled={generateMutation.isPending}
              className="btn-primary w-full mb-3"
            >
              {generateMutation.isPending ? 'Generating...' : 'Generate & Save QR'}
            </button>
            {generateMutation.data?.data?.id && (
              <div className="grid grid-cols-4 gap-2">
                <button onClick={() => handleDownload('png')} className="btn-secondary text-xs">PNG</button>
                <button onClick={() => handleDownload('jpg')} className="btn-secondary text-xs">JPG</button>
                <button onClick={() => handleDownload('svg')} className="btn-secondary text-xs">SVG</button>
                <button onClick={() => handleDownload('pdf')} className="btn-secondary text-xs">PDF</button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}