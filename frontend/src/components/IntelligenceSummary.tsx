import { Activity, Clock3, Database, MapPin, Ruler, ShieldAlert } from 'lucide-react'
import type { InferenceResult } from '../types'

const LABELS: Record<string, string> = {
  water: 'Water palette',
  vegetation: 'Vegetation palette',
  built_up: 'Built-up palette',
  bare_other: 'Bare / other palette',
}

interface Props { result: InferenceResult }

export function IntelligenceSummary({ result }: Props) {
  const shares = Object.entries(result.feature_estimates ?? {}).filter(([key]) => key in LABELS)
  const total = shares.reduce((sum, [, share]) => sum + Math.max(0, share), 0)
  return (
    <section className="panel intelligence-summary" aria-labelledby="intelligence-summary-title">
      <div className="summary-title-row"><div><span className="step-tag">RUN REPORT</span><h3 id="intelligence-summary-title">Intelligence Summary</h3></div><span className="summary-status"><Activity size={13} /> {result.is_ai_inference ? 'Checkpoint' : 'Development'}</span></div>
      <div className="summary-measurements">
        <div><span><Ruler size={13} /> Source dimensions</span><strong>{result.input.width} × {result.input.height}px</strong></div>
        <div><span><Clock3 size={13} /> API processing</span><strong>{result.metrics.runtime_ms} ms</strong></div>
        <div><span><Database size={13} /> Input type</span><strong>{formatInput(result)}</strong></div>
        <div><span><MapPin size={13} /> Map CRS</span><strong>{result.input.crs ?? 'Not present'}</strong></div>
      </div>
      <div className="summary-classes">
        <div className="summary-subhead"><strong>Palette / rule-derived shares</strong><span>not validated class detections</span></div>
        {shares.length > 0 ? <div className="summary-class-list">{shares.map(([key, value]) => <div className="summary-class-row" key={key}>
          <span>{LABELS[key]}</span><strong>{total ? `${(value / total * 100).toFixed(1)}%` : '—'}</strong>
          <i><b className={`share-${key}`} style={{ width: total ? `${Math.max(0, value / total * 100)}%` : '0%' }} /></i>
        </div>)}</div> : <p className="summary-unavailable"><ShieldAlert size={14} /> This run did not return feature shares; no classes are inferred here.</p>}
        <p className="summary-method">{result.feature_method}</p>
      </div>
      <p className="summary-footnote">Image estimate only. These percentages, when present, are not ground-truth land cover or disaster detection.</p>
    </section>
  )
}

function formatInput(result: InferenceResult): string {
  if (result.input.input_kind === 'geotiff-vv-vh') {
    return result.input.distinct_channels ? 'GeoTIFF · distinct VV/VH bands' : 'GeoTIFF · bands identical'
  }
  if (result.input.input_kind?.startsWith('single-channel')) return 'PNG/JPEG · grayscale duplicated'
  if (result.input.input_kind) return result.input.input_kind
  return result.input.distinct_channels ? 'Distinct two-band input' : 'Preview image'
}
