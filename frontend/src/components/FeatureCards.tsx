import { Building2, Leaf, Mountain, Waves } from 'lucide-react'

const FEATURES = [
  { key: 'water', label: 'Water', detail: 'Open water, channels, ponds', icon: Waves, color: '#4aa8d8' },
  { key: 'vegetation', label: 'Vegetation', detail: 'Fields, crops, wooded areas', icon: Leaf, color: '#61c47a' },
  { key: 'built_up', label: 'Built-up', detail: 'Structures, roads, hard surfaces', icon: Building2, color: '#eb9a71' },
  { key: 'bare_other', label: 'Bare / other', detail: 'Exposed ground and mixed pixels', icon: Mountain, color: '#dfc48f' },
]

export function FeatureCards({ estimates, method }: { estimates: Record<string, number>; method: string }) {
  return (
    <div className="feature-section">
      <div className="subsection-head">
        <div>
          <h3>Palette-derived scene shares</h3>
          <p>Fixed palette buckets from the output image—not learned class probabilities or validated land-cover mapping.</p>
        </div>
      </div>
      <div className="feature-grid">
        {FEATURES.map(({ key, label, detail, icon: Icon, color }) => {
          const value = estimates[key] ?? 0
          return (
            <article className="feature-card" key={key} style={{ '--feature-color': color } as React.CSSProperties}>
              <div className="feature-top">
                <span className="feature-icon"><Icon size={18} strokeWidth={2} /></span>
                <strong>{(value * 100).toFixed(0)}%</strong>
              </div>
              <h4>{label}</h4>
              <small>{detail}</small>
              <div className="feature-track"><span style={{ width: `${Math.max(2, Math.min(100, value * 100))}%` }} /></div>
            </article>
          )
        })}
      </div>
      <p className="method-footnote">{method}</p>
    </div>
  )
}
