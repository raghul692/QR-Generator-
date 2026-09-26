import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  BsPalette, BsImage, BsSliders, BsShieldLock, BsLightningCharge,
  BsApple, BsGooglePlay, BsChevronDown, BsChevronUp
} from 'react-icons/bs'
import PresetGallery from './PresetGallery'

const DOTS_STYLES = [
  { id: 'square', label: 'Classic Square' },
  { id: 'dots', label: 'Modern Dots' },
  { id: 'rounded', label: 'Soft Rounded' },
  { id: 'extra-rounded', label: 'Extra Rounded' },
  { id: 'classy', label: 'Classy Diamond' },
  { id: 'classy-rounded', label: 'Classy Smooth' },
]

const CORNER_SQUARE_STYLES = [
  { id: 'square', label: 'Square' },
  { id: 'dot', label: 'Circle' },
  { id: 'extra-rounded', label: 'Squircle' },
]

const CORNER_DOT_STYLES = [
  { id: 'square', label: 'Square' },
  { id: 'dot', label: 'Dot' },
]

export default function StyleCustomizer({
  customization,
  onChange,
  onApplyPreset,
  activePresetId,
}) {
  const [activeTab, setActiveTab] = useState('style') // 'presets', 'style', 'colors', 'logo', 'dynamic'

  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-accent-violet animate-pulse" />
          2. Design & Customization Studio
        </h3>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex items-center gap-1 p-1 rounded-xl bg-slate-100 dark:bg-white/[0.04] border border-slate-200 dark:border-white/[0.06] overflow-x-auto scrollbar-none">
        {[
          { id: 'presets', label: 'Presets' },
          { id: 'style', label: 'Patterns & Eyes' },
          { id: 'colors', label: 'Colors & Glow' },
          { id: 'logo', label: 'Brand Logo' },
          { id: 'dynamic', label: '⚡ Smart Dynamic' },
        ].map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all duration-150 ${
              activeTab === tab.id
                ? 'bg-white dark:bg-obsidian-800 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 1. Presets Tab */}
      {activeTab === 'presets' && (
        <PresetGallery
          activePresetId={activePresetId}
          onApplyPreset={onApplyPreset}
        />
      )}

      {/* 2. Patterns & Eyes Tab */}
      {activeTab === 'style' && (
        <div className="space-y-4">
          {/* Matrix Pattern Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wider">
              Matrix Dot Style
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {DOTS_STYLES.map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => onChange('dotsType', d.id)}
                  className={`p-2.5 rounded-xl border text-xs font-medium text-left transition-all ${
                    customization.dotsType === d.id
                      ? 'border-primary-500 bg-primary-500/10 text-primary-600 dark:text-primary-300 ring-1 ring-primary-500'
                      : 'border-slate-200 dark:border-white/[0.08] hover:border-slate-300 dark:hover:border-white/[0.2] text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Eye Outer Frame */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wider">
              Outer Eye Corner Shape
            </label>
            <div className="grid grid-cols-3 gap-2">
              {CORNER_SQUARE_STYLES.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => onChange('cornerSquareType', c.id)}
                  className={`p-2 rounded-xl border text-xs font-medium text-center transition-all ${
                    customization.cornerSquareType === c.id
                      ? 'border-primary-500 bg-primary-500/10 text-primary-600 dark:text-primary-300 ring-1 ring-primary-500'
                      : 'border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Eye Inner Pupil */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2 uppercase tracking-wider">
              Inner Pupil Style
            </label>
            <div className="grid grid-cols-2 gap-2">
              {CORNER_DOT_STYLES.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => onChange('cornerDotType', c.id)}
                  className={`p-2 rounded-xl border text-xs font-medium text-center transition-all ${
                    customization.cornerDotType === c.id
                      ? 'border-primary-500 bg-primary-500/10 text-primary-600 dark:text-primary-300 ring-1 ring-primary-500'
                      : 'border-slate-200 dark:border-white/[0.08] text-slate-700 dark:text-slate-300'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Margin & Error Correction */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-200 dark:border-white/[0.06]">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-slate-700 dark:text-slate-300">Quiet Zone (Margin):</span>
                <span className="text-slate-500 font-mono">{customization.margin || 4}px</span>
              </div>
              <input
                type="range"
                min="0"
                max="20"
                value={customization.margin || 4}
                onChange={(e) => onChange('margin', Number(e.target.value))}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Error Correction Level
              </label>
              <select
                value={customization.error_correction || 'H'}
                onChange={(e) => onChange('error_correction', e.target.value)}
                className="input-field py-1.5"
              >
                <option value="L">L - Low (7% recovery)</option>
                <option value="M">M - Medium (15% recovery)</option>
                <option value="Q">Q - Quality (25% recovery)</option>
                <option value="H">H - High (30% - Best with Logo)</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* 3. Colors & Glow Tab */}
      {activeTab === 'colors' && (
        <div className="space-y-4">
          {/* Gradient Toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.06]">
            <div>
              <p className="text-xs font-bold text-slate-900 dark:text-white">Enable Matrix Gradient</p>
              <p className="text-[11px] text-slate-400">Blend two colors smoothly across the QR code</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={customization.gradient_enabled || false}
                onChange={(e) => onChange('gradient_enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none rounded-full peer dark:bg-slate-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
            </label>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {customization.gradient_enabled ? (
              <>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Gradient Start Color
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={customization.gradient_start || '#6366F1'}
                      onChange={(e) => onChange('gradient_start', e.target.value)}
                      className="w-10 h-10 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                    />
                    <input
                      type="text"
                      value={customization.gradient_start || '#6366F1'}
                      onChange={(e) => onChange('gradient_start', e.target.value)}
                      className="input-field py-1.5 uppercase font-mono text-xs"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Gradient End Color
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={customization.gradient_end || '#8B5CF6'}
                      onChange={(e) => onChange('gradient_end', e.target.value)}
                      className="w-10 h-10 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                    />
                    <input
                      type="text"
                      value={customization.gradient_end || '#8B5CF6'}
                      onChange={(e) => onChange('gradient_end', e.target.value)}
                      className="input-field py-1.5 uppercase font-mono text-xs"
                    />
                  </div>
                </div>
              </>
            ) : (
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                  Foreground Matrix Color
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={customization.foreground_color || '#000000'}
                    onChange={(e) => onChange('foreground_color', e.target.value)}
                    className="w-10 h-10 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                  />
                  <input
                    type="text"
                    value={customization.foreground_color || '#000000'}
                    onChange={(e) => onChange('foreground_color', e.target.value)}
                    className="input-field py-1.5 uppercase font-mono text-xs"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Background Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={customization.background_color || '#FFFFFF'}
                  onChange={(e) => onChange('background_color', e.target.value)}
                  className="w-10 h-10 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                />
                <input
                  type="text"
                  value={customization.background_color || '#FFFFFF'}
                  onChange={(e) => onChange('background_color', e.target.value)}
                  className="input-field py-1.5 uppercase font-mono text-xs"
                />
              </div>
            </div>
          </div>

          {/* Individual Eye Colors */}
          <div className="pt-3 border-t border-slate-200 dark:border-white/[0.06] grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Outer Eye Corner Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={customization.cornerSquareColor || customization.foreground_color || '#000000'}
                  onChange={(e) => onChange('cornerSquareColor', e.target.value)}
                  className="w-9 h-9 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                />
                <input
                  type="text"
                  value={customization.cornerSquareColor || customization.foreground_color || '#000000'}
                  onChange={(e) => onChange('cornerSquareColor', e.target.value)}
                  className="input-field py-1 text-xs uppercase font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Inner Eye Ball (Pupil) Color
              </label>
              <div className="flex items-center gap-2">
                <input
                  type="color"
                  value={customization.cornerDotColor || customization.foreground_color || '#000000'}
                  onChange={(e) => onChange('cornerDotColor', e.target.value)}
                  className="w-9 h-9 rounded-lg cursor-pointer border border-white/20 p-0.5 bg-transparent"
                />
                <input
                  type="text"
                  value={customization.cornerDotColor || customization.foreground_color || '#000000'}
                  onChange={(e) => onChange('cornerDotColor', e.target.value)}
                  className="input-field py-1 text-xs uppercase font-mono"
                />
              </div>
            </div>
          </div>

          {/* Transparent Background Toggle */}
          <label className="flex items-center gap-2 cursor-pointer pt-2">
            <input
              type="checkbox"
              checked={customization.transparent_background || false}
              onChange={(e) => onChange('transparent_background', e.target.checked)}
              className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500"
            />
            <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
              Transparent Background (PNG / SVG Only)
            </span>
          </label>
        </div>
      )}

      {/* 4. Brand Logo Tab */}
      {activeTab === 'logo' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl border border-dashed border-slate-300 dark:border-white/[0.15] bg-slate-50/50 dark:bg-white/[0.02] text-center">
            <BsImage className="text-3xl mx-auto mb-2 text-slate-400" />
            <p className="text-xs font-bold text-slate-800 dark:text-slate-200">
              Upload Company / Brand Logo
            </p>
            <p className="text-[11px] text-slate-400 mb-3">
              PNG, SVG, or JPG with transparent background recommended
            </p>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  const reader = new FileReader()
                  reader.onloadend = () => {
                    onChange('logo_url', reader.result)
                  }
                  reader.readAsDataURL(file)
                }
              }}
              className="text-xs file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-primary-600 file:text-white hover:file:bg-primary-700 cursor-pointer"
            />
          </div>

          {customization.logo_url && (
            <div className="p-3 rounded-xl bg-slate-100 dark:bg-white/[0.04] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <img
                  src={customization.logo_url}
                  alt="Logo preview"
                  className="w-10 h-10 object-contain rounded-lg border bg-white p-1"
                />
                <div>
                  <p className="text-xs font-bold text-slate-800 dark:text-slate-200">Custom Center Logo</p>
                  <p className="text-[10px] text-emerald-500">Embedded in QR center</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => onChange('logo_url', null)}
                className="text-xs text-rose-500 hover:underline font-medium"
              >
                Remove
              </button>
            </div>
          )}

          {/* Logo Size */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold text-slate-700 dark:text-slate-300">Logo Scale:</span>
              <span className="text-slate-500 font-mono">{customization.logo_size || 25}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="35"
              value={customization.logo_size || 25}
              onChange={(e) => onChange('logo_size', Number(e.target.value))}
            />
          </div>
        </div>
      )}

      {/* 5. Smart Dynamic & OS Redirection Tab */}
      {activeTab === 'dynamic' && (
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-gradient-to-r from-primary-950/40 to-indigo-950/40 border border-primary-500/20">
            <label className="flex items-center justify-between cursor-pointer">
              <div className="flex items-center gap-2">
                <BsLightningCharge className="text-primary-400 text-lg" />
                <div>
                  <span className="text-xs font-bold text-white block">
                    Enable Dynamic Shortlink & Tracking
                  </span>
                  <span className="text-[11px] text-slate-400">
                    Destination can be updated anytime after printing + real-time scan analytics.
                  </span>
                </div>
              </div>
              <input
                type="checkbox"
                checked={customization.is_dynamic || false}
                onChange={(e) => onChange('is_dynamic', e.target.checked)}
                className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500"
              />
            </label>
          </div>

          {customization.is_dynamic && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className="space-y-4 pt-2"
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1 flex items-center gap-1.5">
                    <BsShieldLock /> Passcode Protection (Optional)
                  </label>
                  <input
                    type="password"
                    placeholder="Require PIN to access"
                    value={customization.password || ''}
                    onChange={(e) => onChange('password', e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                    Expiration Date (Optional)
                  </label>
                  <input
                    type="datetime-local"
                    value={customization.expires_at || ''}
                    onChange={(e) => onChange('expires_at', e.target.value)}
                    className="input-field"
                  />
                </div>
              </div>

              {/* Smart OS Redirection Rules */}
              <div className="p-4 rounded-xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200 dark:border-white/[0.08] space-y-3">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
                    Smart OS Device Routing
                  </span>
                  <span className="text-[10px] bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded-full font-bold">
                    2026 Feature
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">
                  Route scanners directly to platform-specific apps based on their operating system:
                </p>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <BsApple className="text-lg text-slate-400 flex-shrink-0" />
                    <input
                      type="url"
                      placeholder="iOS Fallback (App Store URL)"
                      value={customization.ios_target_url || ''}
                      onChange={(e) => onChange('ios_target_url', e.target.value)}
                      className="input-field text-xs py-2"
                    />
                  </div>
                  <div className="flex items-center gap-2">
                    <BsGooglePlay className="text-lg text-slate-400 flex-shrink-0" />
                    <input
                      type="url"
                      placeholder="Android Fallback (Google Play Store URL)"
                      value={customization.android_target_url || ''}
                      onChange={(e) => onChange('android_target_url', e.target.value)}
                      className="input-field text-xs py-2"
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}
