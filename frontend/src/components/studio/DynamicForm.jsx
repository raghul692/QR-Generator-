import { BsFolder, BsTag, BsWifi, BsGlobe, BsPerson, BsChatDots } from 'react-icons/bs'

export default function DynamicForm({
  currentType,
  formData = {},
  onChange,
  title,
  onTitleChange,
  categories = [],
}) {
  const selectedCategory = formData.category_id || ''

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent-cyan animate-pulse" />
          Content Details & Meta
        </h3>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-600 dark:text-primary-300">
          {currentType?.label || 'Custom'}
        </span>
      </div>

      <div className="space-y-4">
        {/* Title */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1.5">
            <BsTag className="text-primary-500" /> Campaign / QR Code Title <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => onTitleChange(e.target.value)}
            placeholder="e.g. Summer Promo, Store Wi-Fi, My Portfolio"
            className="input-field"
          />
        </div>

        {/* Dynamic Fields rendered from Backend Type Definition */}
        {currentType?.fields?.map((field) => (
          <div key={field.name} className="space-y-1">
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300">
              {field.label}
              {field.required && <span className="text-rose-500 ml-1">*</span>}
            </label>

            {field.type === 'textarea' ? (
              <textarea
                value={formData[field.name] || ''}
                onChange={(e) => onChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                rows={3}
                className="input-field"
              />
            ) : field.type === 'select' ? (
              <select
                value={formData[field.name] || field.default || ''}
                onChange={(e) => onChange(field.name, e.target.value)}
                className="input-field"
              >
                {field.options?.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            ) : field.type === 'checkbox' ? (
              <label className="flex items-center gap-2.5 cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={formData[field.name] || false}
                  onChange={(e) => onChange(field.name, e.target.checked)}
                  className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500"
                />
                <span className="text-xs text-slate-700 dark:text-slate-300">
                  {field.label}
                </span>
              </label>
            ) : (
              <input
                type={field.type || 'text'}
                value={formData[field.name] || ''}
                onChange={(e) => onChange(field.name, e.target.value)}
                placeholder={field.placeholder}
                className="input-field"
              />
            )}
          </div>
        ))}

        {/* If no backend fields provided, fallback to standard URL / Content input */}
        {(!currentType?.fields || currentType.fields.length === 0) && (
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1.5">
              <BsGlobe className="text-primary-500" /> Target Destination / Text Content <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={formData.url || formData.text || formData.content || ''}
              onChange={(e) => onChange('url', e.target.value)}
              placeholder="https://example.com or any text"
              className="input-field"
            />
          </div>
        )}

        {/* Category Selector */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1.5">
            <BsFolder className="text-primary-500" /> Category Organization
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => onChange('category_id', e.target.value ? Number(e.target.value) : null)}
            className="input-field"
          >
            <option value="">None (Uncategorized)</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}
