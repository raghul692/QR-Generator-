import { useState, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { qrAPI, categoryAPI } from '../services/api'
import TypeTabs from '../components/studio/TypeTabs'
import DynamicForm from '../components/studio/DynamicForm'
import StyleCustomizer from '../components/studio/StyleCustomizer'
import LiveMockupViewer from '../components/studio/LiveMockupViewer'
import ScannabilityMeter from '../components/studio/ScannabilityMeter'

export default function Generator() {
  const [selectedType, setSelectedType] = useState('url')
  const [formData, setFormData] = useState({})
  const [title, setTitle] = useState('')
  const [activePresetId, setActivePresetId] = useState('obsidian-glow')

  const [customization, setCustomization] = useState({
    size: 400,
    foreground_color: '#6366F1',
    background_color: '#090D16',
    gradient_enabled: true,
    gradient_start: '#6366F1',
    gradient_end: '#8B5CF6',
    transparent_background: false,
    dotsType: 'dots',
    cornerSquareType: 'extra-rounded',
    cornerSquareColor: '#8B5CF6',
    cornerDotType: 'dot',
    cornerDotColor: '#06B6D4',
    margin: 4,
    error_correction: 'H',
    logo_size: 25,
    logo_url: null,
    is_dynamic: false,
    password: '',
    expires_at: '',
    ios_target_url: '',
    android_target_url: '',
  })

  // Fetch QR types
  const { data: types = [] } = useQuery({
    queryKey: ['qr-types'],
    queryFn: () => qrAPI.getTypes().then((r) => r.data),
  })

  // Fetch Categories
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoryAPI.list().then((r) => r.data),
  })

  const currentType = types.find((t) => t.key === selectedType) || {
    key: 'url',
    label: 'Website URL',
    fields: [{ name: 'url', label: 'Website URL', type: 'url', placeholder: 'https://example.com', required: true }]
  }

  // Compute live client-side QR string
  const rawQrValue = useMemo(() => {
    switch (selectedType) {
      case 'url':
        return formData.url || 'https://qrmaster.pro'
      case 'text':
        return formData.text || 'QRMaster Pro Modern Studio'
      case 'wifi':
        return `WIFI:T:${formData.encryption || 'WPA'};S:${formData.ssid || ''};P:${formData.password || ''};;`
      case 'vcard':
        return `BEGIN:VCARD\nVERSION:3.0\nN:${formData.last_name || ''};${formData.first_name || ''}\nFN:${formData.first_name || ''} ${formData.last_name || ''}\nTEL:${formData.phone || ''}\nEMAIL:${formData.email || ''}\nORG:${formData.company || ''}\nEND:VCARD`
      case 'whatsapp':
        return `https://wa.me/${formData.phone || ''}?text=${encodeURIComponent(formData.message || '')}`
      case 'upi':
        return `upi://pay?pa=${formData.vpa || ''}&pn=${encodeURIComponent(formData.name || '')}&am=${formData.amount || ''}&cu=INR`
      case 'email':
        return `mailto:${formData.email || ''}?subject=${encodeURIComponent(formData.subject || '')}&body=${encodeURIComponent(formData.body || '')}`
      case 'phone':
        return `tel:${formData.phone || ''}`
      case 'sms':
        return `smsto:${formData.phone || ''}:${formData.message || ''}`
      default:
        return formData.url || formData.text || formData.content || 'https://qrmaster.pro'
    }
  }, [selectedType, formData])

  // Handlers
  const handleFieldChange = (name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleCustomChange = (name, value) => {
    setActivePresetId(null) // Clear active preset if user manual tweaks
    setCustomization((prev) => ({ ...prev, [name]: value }))
  }

  const handleApplyPreset = (preset) => {
    setActivePresetId(preset.id)
    setCustomization((prev) => ({
      ...prev,
      background_color: preset.background,
      foreground_color: preset.dotsColor,
      dotsType: preset.dotsType,
      gradient_enabled: !!preset.gradient,
      gradient_start: preset.gradient?.start || preset.dotsColor,
      gradient_end: preset.gradient?.end || preset.dotsColor,
      cornerSquareType: preset.cornerSquareType,
      cornerSquareColor: preset.cornerSquareColor,
      cornerDotType: preset.cornerDotType,
      cornerDotColor: preset.cornerDotColor,
    }))
    toast.success(`Theme "${preset.name}" applied!`)
  }

  // Backend Generate & Save Mutation
  const generateMutation = useMutation({
    mutationFn: (payload) => qrAPI.generate(payload),
    onSuccess: () => {
      toast.success('QR Code saved to database history!')
    },
    onError: (err) => {
      toast.error(err.response?.data?.detail || err.message || 'Generation failed')
    },
  })

  const handleSaveToDatabase = () => {
    if (!title.trim()) {
      toast.error('Please enter a Campaign / QR Title first')
      return
    }

    generateMutation.mutate({
      title,
      qr_type: selectedType,
      data: formData,
      customization: {
        ...customization,
        qr_style: customization.dotsType === 'dots' ? 'dots' : customization.dotsType === 'rounded' ? 'rounded' : 'square',
      },
      save_to_history: true,
      category_id: formData.category_id || null,
      is_dynamic: customization.is_dynamic,
      password: customization.password || null,
      expires_at: customization.expires_at || null,
      ios_target_url: customization.ios_target_url || null,
      android_target_url: customization.android_target_url || null,
    })
  }

  const handleDownloadBackend = (format) => {
    const id = generateMutation.data?.data?.id
    if (!id) return
    qrAPI.download(id, format).then((res) => {
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `qr_${selectedType}_${id}.${format}`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success(`Downloaded ${format.toUpperCase()}`)
    })
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Page Title & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200 dark:border-white/[0.06]">
        <div>
          <h1 className="text-2xl lg:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            QR Studio <span className="text-primary-500 font-normal">2.0</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time vector generator with real-world 3D mockups, contrast guard, and smart dynamic routing.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-300 border border-primary-500/20">
            ⚡ Ultra-HD Vector Studio
          </span>
        </div>
      </div>

      {/* Main 2-Column Responsive Studio Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Form & Design Controls (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Step 1: Type Selection */}
          <TypeTabs
            types={types}
            selectedType={selectedType}
            onSelect={(type) => {
              setSelectedType(type)
              setFormData({})
            }}
          />

          {/* Step 2: Content Details Form */}
          <DynamicForm
            currentType={currentType}
            formData={formData}
            onChange={handleFieldChange}
            title={title}
            onTitleChange={setTitle}
            categories={categories}
          />

          {/* Step 3: Design & Styling Customizer */}
          <StyleCustomizer
            customization={customization}
            onChange={handleCustomChange}
            onApplyPreset={handleApplyPreset}
            activePresetId={activePresetId}
          />
        </div>

        {/* Right Column: Live Mockup Preview & Health Meter (5 cols, Sticky) */}
        <div className="lg:col-span-5 space-y-5 sticky top-20">
          {/* Live 60fps Real-World Mockup Engine */}
          <LiveMockupViewer
            value={rawQrValue}
            title={title}
            customization={customization}
            onSave={handleSaveToDatabase}
            isSaving={generateMutation.isPending}
            savedId={generateMutation.data?.data?.id}
            onDownloadBackend={handleDownloadBackend}
          />

          {/* Scannability Contrast Health Guard */}
          <ScannabilityMeter
            foregroundColor={customization.gradient_enabled ? customization.gradient_start : customization.foreground_color}
            backgroundColor={customization.background_color}
            errorCorrection={customization.error_correction}
            hasLogo={!!customization.logo_url}
          />
        </div>
      </div>
    </div>
  )
}