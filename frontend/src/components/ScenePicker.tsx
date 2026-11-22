import { Check, Info } from 'lucide-react'
import type { DemoScene } from '../types'

interface Props {
  scenes: DemoScene[]
  selectedId: string | null
  onSelect: (id: string) => void
  disabled: boolean
}

const TYPE_LABELS: Record<string, string> = {
  'water / coastal': 'Water',
  'vegetation / agriculture': 'Vegetation',
  'urban / built-up': 'Built-up',
  'mixed / disaster-response narrative': 'Mixed scene',
}

export function ScenePicker({ scenes, selectedId, onSelect, disabled }: Props) {
  return (
    <section className="panel" aria-labelledby="scenes-title">
      <div className="panel-head">
        <div>
          <span className="step-tag">01 / CHOOSE</span>
          <h2 id="scenes-title">Demo scenes</h2>
        </div>
        <span className="panel-count">{scenes.length} scenes</span>
      </div>
      <p className="panel-sub">Start with a prepared scene for a reliable first run.</p>
      <div className="scene-grid">
        {scenes.map((scene) => (
          <button
            key={scene.id}
            className={`scene-card ${selectedId === scene.id ? 'selected' : ''}`}
            onClick={() => onSelect(scene.id)}
            disabled={disabled}
            aria-pressed={selectedId === scene.id}
          >
            <span className="scene-thumb">
              <img src={scene.image_url} alt="" loading="lazy" />
              <span className="scene-type">{TYPE_LABELS[scene.scene_type] ?? scene.scene_type}</span>
              {selectedId === scene.id && <span className="scene-check"><Check size={14} strokeWidth={3} /></span>}
            </span>
            <span className="scene-body">
              <strong>{scene.name}</strong>
              <small>{scene.description}</small>
              <em><Info size={11} /> Synthetic illustration</em>
            </span>
          </button>
        ))}
      </div>
    </section>
  )
}
