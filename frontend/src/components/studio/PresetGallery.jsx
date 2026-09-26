import { BsCheckCircleFill, BsStars } from 'react-icons/bs'

export const PRESET_THEMES = [
  {
    id: 'obsidian-glow',
    name: 'Obsidian Glow',
    tag: 'Cyberpunk',
    background: '#090D16',
    dotsColor: '#6366F1',
    dotsType: 'dots',
    gradient: {
      type: 'linear',
      start: '#6366F1',
      end: '#8B5CF6',
    },
    cornerSquareType: 'extra-rounded',
    cornerSquareColor: '#8B5CF6',
    cornerDotType: 'dot',
    cornerDotColor: '#06B6D4',
  },
  {
    id: 'emerald-luxury',
    name: 'Emerald Luxe',
    tag: 'Premium',
    background: '#051A14',
    dotsColor: '#10B981',
    dotsType: 'classy-rounded',
    gradient: {
      type: 'linear',
      start: '#10B981',
      end: '#34D399',
    },
    cornerSquareType: 'dot',
    cornerSquareColor: '#10B981',
    cornerDotType: 'dot',
    cornerDotColor: '#F59E0B',
  },
  {
    id: 'sunset-neon',
    name: 'Sunset Neon',
    tag: 'Vibrant',
    background: '#FFFFFF',
    dotsColor: '#F43F5E',
    dotsType: 'rounded',
    gradient: {
      type: 'linear',
      start: '#F43F5E',
      end: '#FB923C',
    },
    cornerSquareType: 'extra-rounded',
    cornerSquareColor: '#F43F5E',
    cornerDotType: 'dot',
    cornerDotColor: '#FB923C',
  },
  {
    id: 'cyber-cyan',
    name: 'Cyber Cyan',
    tag: 'High-Tech',
    background: '#040711',
    dotsColor: '#06B6D4',
    dotsType: 'square',
    gradient: {
      type: 'linear',
      start: '#06B6D4',
      end: '#3B82F6',
    },
    cornerSquareType: 'square',
    cornerSquareColor: '#06B6D4',
    cornerDotType: 'square',
    cornerDotColor: '#3B82F6',
  },
  {
    id: 'swiss-clean',
    name: 'Swiss Clean',
    tag: 'Minimal',
    background: '#FFFFFF',
    dotsColor: '#0F172A',
    dotsType: 'extra-rounded',
    gradient: null,
    cornerSquareType: 'extra-rounded',
    cornerSquareColor: '#0F172A',
    cornerDotType: 'dot',
    cornerDotColor: '#0F172A',
  },
  {
    id: 'corporate-navy',
    name: 'Royal Trust',
    tag: 'Enterprise',
    background: '#F8FAFC',
    dotsColor: '#1E3A8A',
    dotsType: 'rounded',
    gradient: {
      type: 'linear',
      start: '#1E3A8A',
      end: '#2563EB',
    },
    cornerSquareType: 'extra-rounded',
    cornerSquareColor: '#1E3A8A',
    cornerDotType: 'dot',
    cornerDotColor: '#2563EB',
  },
]

export default function PresetGallery({ activePresetId, onApplyPreset }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
          <BsStars className="text-accent-amber" /> 1-Click Curated Presets
        </label>
        <span className="text-[11px] text-slate-400">Click to apply full theme</span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
        {PRESET_THEMES.map((theme) => {
          const isActive = activePresetId === theme.id
          return (
            <button
              key={theme.id}
              type="button"
              onClick={() => onApplyPreset(theme)}
              className={`p-2.5 rounded-xl border text-left flex items-center gap-2.5 transition-all duration-200 group relative ${
                isActive
                  ? 'border-primary-500 bg-primary-500/10 shadow-sm ring-1 ring-primary-500'
                  : 'border-slate-200 dark:border-white/[0.08] hover:border-slate-300 dark:hover:border-white/[0.2] bg-white/40 dark:bg-white/[0.02]'
              }`}
            >
              {/* Color Swatch Preview */}
              <div
                className="w-8 h-8 rounded-lg flex-shrink-0 border border-white/20 shadow-inner flex items-center justify-center relative overflow-hidden"
                style={{ backgroundColor: theme.background }}
              >
                <div
                  className="w-4 h-4 rounded-sm"
                  style={{
                    background: theme.gradient
                      ? `linear-gradient(135deg, ${theme.gradient.start}, ${theme.gradient.end})`
                      : theme.dotsColor,
                  }}
                />
              </div>

              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate">
                  {theme.name}
                </p>
                <span className="text-[10px] text-slate-400 dark:text-slate-500 block truncate">
                  {theme.tag}
                </span>
              </div>

              {isActive && (
                <BsCheckCircleFill className="text-primary-500 text-sm flex-shrink-0" />
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
