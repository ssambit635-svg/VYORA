import { Eye, EyeOff, Info, Layers3 } from 'lucide-react'
import { useState } from 'react'
import type { InferenceResult } from '../types'

type LayerId = 'source' | 'estimate' | 'consistency' | 'feature-summary'

interface Props {
  result: InferenceResult
}

const featureLabels: Record<string, string> = {
  water: 'Water palette',
  vegetation: 'Vegetation palette',
  built_up: 'Built-up palette',
  bare_other: 'Bare / other palette',
}

export function ResultLayerStudio({ result }: Props) {
  const [activeLayer, setActiveLayer] = useState<LayerId>('source')
  const active = layerDetails(activeLayer, result)
  const shares = Object.entries(result.feature_estimates ?? {}).filter(([key]) => key in featureLabels)
  const hasShares = shares.length > 0
  const normalizedTotal = shares.reduce((sum, [, value]) => sum + Math.max(0, value), 0)

  return (
    <section className="panel layer-studio" aria-labelledby="layer-studio-title">
      <div className="layer-studio-head">
        <div><span className="step-tag">LAYER INSPECTOR</span><h3 id="layer-studio-title"><Layers3 size={16} /> One scene, several honest views</h3></div>
        <span className="layer-source-note">Same image grid · no map alignment claim</span>
      </div>
      <div className="layer-tabs" role="group" aria-label="Choose an available result layer">
        <button className={activeLayer === 'source' ? 'active' : ''} aria-pressed={activeLayer === 'source'} onClick={() => setActiveLayer('source')}><Eye size={14} /> Original input</button>
        <button className={activeLayer === 'estimate' ? 'active' : ''} aria-pressed={activeLayer === 'estimate'} onClick={() => setActiveLayer('estimate')}><Eye size={14} /> Estimated colour</button>
        <button className={activeLayer === 'consistency' ? 'active' : ''} aria-pressed={activeLayer === 'consistency'} onClick={() => setActiveLayer('consistency')}><Eye size={14} /> Consistency</button>
        <button className={activeLayer === 'feature-summary' ? 'active' : ''} aria-pressed={activeLayer === 'feature-summary'} onClick={() => setActiveLayer('feature-summary')}><Layers3 size={14} /> Feature summary</button>
        <button className="unavailable-layer" disabled title="This model does not return a spatial segmentation mask."><EyeOff size={14} /> Feature mask · unavailable</button>
        <button className="unavailable-layer" disabled title="This model does not return an attention map."><EyeOff size={14} /> Attention map · unavailable</button>
      </div>
      <div className="layer-stage">
        {activeLayer === 'feature-summary' ? (
          <div className="layer-summary-view">
            <span className="summary-view-icon"><Layers3 size={22} /></span>
            <h4>{hasShares ? 'Palette-derived proportions' : 'No class proportions from this run'}</h4>
            <p>{hasShares
              ? 'These are aggregate palette or fixed-rule shares, not a pixel segmentation map or validated land-cover detections.'
              : 'The active image-to-image checkpoint does not output spatial feature classes. No mask is being substituted here.'}</p>
            {hasShares && <div className="layer-share-list">{shares.map(([key, value]) => <div className="layer-share-row" key={key}>
              <span>{featureLabels[key]}</span><strong>{normalizedTotal ? `${(value / normalizedTotal * 100).toFixed(1)}%` : '—'}</strong>
              <i><b style={{ width: normalizedTotal ? `${Math.max(0, value / normalizedTotal * 100)}%` : '0%' }} /></i>
            </div>)}</div>}
          </div>
        ) : (
          <div className="layer-image-view">
            <img src={active.url} alt={active.alt} />
            <div className="layer-image-caption"><strong>{active.title}</strong><span>{active.description}</span></div>
          </div>
        )}
      </div>
      <div className="layer-limits"><Info size={14} /><p><strong>Not available in this model:</strong> learned feature-segmentation masks and attention/saliency maps. We show only API-returned images and clearly labelled derived summaries.</p></div>
    </section>
  )
}

function layerDetails(id: LayerId, result: InferenceResult) {
  if (id === 'estimate') return {
    url: result.urls.colour,
    alt: 'Model or development-run RGB-style estimated output; not true-colour recovery.',
    title: 'Estimated colour view',
    description: 'Pixel estimate from the active API runner; see the status banner for model or development mode.',
  }
  if (id === 'consistency') return {
    url: result.urls.confidence,
    alt: 'Flip-view agreement or development-rule consistency map; not calibrated confidence.',
    title: 'Consistency view',
    description: 'Agreement/stability cue only. It is not a probability of correctness or hazard.',
  }
  return {
    url: result.urls.input,
    alt: result.input.distinct_channels
      ? 'SAR diagnostic composite based on distinct VV and VH input bands.'
      : 'Input preview without verified distinct VV and VH bands.',
    title: result.input.distinct_channels ? 'Original SAR · VV/VH diagnostic composite' : 'Original input preview',
    description: result.input.distinct_channels
      ? 'Diagnostic band composite, not optical RGB.'
      : 'No verified separate VV/VH channels for this input.',
  }
}
