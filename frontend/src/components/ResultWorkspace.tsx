import { AlertTriangle, CheckCircle2, Download, FileJson, ImageDown, Layers3, Map, RotateCcw, ShieldCheck } from 'lucide-react'
import { useState } from 'react'
import type { InferenceResult } from '../types'
import { ComparisonSlider } from './ComparisonSlider'
import { FeatureCards } from './FeatureCards'

interface Props {
  result: InferenceResult
  onReset: () => void
}

export function ResultWorkspace({ result, onReset }: Props) {
  const [showConfidence, setShowConfidence] = useState(false)
  const [position, setPosition] = useState(50)
  const conf = result.confidence_summary
  const isDev = result.mode === 'development'
  const isPngPrototype = result.model_version.includes('paired-png-prototype')

  return (
    <section className="results-section" aria-labelledby="results-title">
      <div className="results-head">
        <div>
          <span className="step-tag">03 / RESULT</span>
          <h2 id="results-title">Interpretation workspace</h2>
          <p className="muted">{result.source.name} · {result.input.width}×{result.input.height} tile · {result.model_version}</p>
        </div>
        <button className="ghost-btn" onClick={onReset}><RotateCcw size={15} /> New scene</button>
      </div>

      <div className={`mode-banner ${isDev ? 'dev' : 'model'}`} role="note">
        {isDev ? <AlertTriangle size={18} /> : <ShieldCheck size={18} />}
        <div>
          <strong>{isDev ? 'DEVELOPMENT MODE — not AI inference' : 'MODEL CHECKPOINT — AI inference'}</strong>
          <span>{isDev
            ? 'Output comes from fixed, hand-authored backscatter rules used to demonstrate the product flow. No trained model is running and no accuracy claim is made.'
            : isPngPrototype
              ? `Output comes from the local ${result.model_version} checkpoint trained on paired PNG tiles with grayscale input duplicated into two model channels. This is not separate VV/VH input.`
              : `Output was produced by the local ${result.model_version} checkpoint. The consistency cue comes from flipped-view agreement; it is not calibrated uncertainty.`}
          </span>
        </div>
      </div>

      <div className="result-grid">
        <div className="result-main">
          <div className="compare-shell panel">
            <div className="compare-toolbar">
              <div><Layers3 size={16} /><strong>Before / after</strong><span>Drag the handle to compare</span></div>
              <label className="switch">
                <input type="checkbox" checked={showConfidence} onChange={(e) => setShowConfidence(e.target.checked)} />
                <span className="switch-track" aria-hidden="true"><span /></span>
                <span className="switch-label">Consistency layer</span>
              </label>
            </div>
            <ComparisonSlider
              inputUrl={result.urls.input}
              colourUrl={result.urls.colour}
              confidenceUrl={result.urls.confidence}
              showConfidence={showConfidence}
              position={position}
              onPosition={setPosition}
              inputLabel={isPngPrototype ? 'GRAYSCALE PNG' : 'VV/VH INPUT'}
              outputLabel={isPngPrototype ? 'MODEL ESTIMATE' : 'INTERPRETATION'}
            />
            <div className="compare-foot">
              <div className={`legend ${showConfidence ? 'visible' : ''}`}>
                <span><i className="swatch low" /> Lower agreement &lt;45% · {conf.low_pct}%</span>
                <span><i className="swatch mid" /> Moderate · {conf.medium_pct}%</span>
                <span><i className="swatch high" /> Higher agreement ≥70% · {conf.high_pct}%</span>
              </div>
              <span className="muted small">Slider works with touch, mouse and arrow keys.</span>
            </div>
          </div>

          {isPngPrototype ? (
            <div className="panel prototype-note">
              <h3>What this prototype predicts</h3>
              <p>It predicts image pixels only. It does not predict water, vegetation, buildings, land-cover percentages, or calibrated uncertainty.</p>
            </div>
          ) : (
            <FeatureCards estimates={result.feature_estimates} method={result.feature_method} />
          )}
        </div>

        <aside className="result-side">
          <div className="panel side-panel">
            <h3>Session evidence</h3>
            <div className="stat-list">
              <div><span>Observed runtime</span><strong>{result.metrics.runtime_ms} ms</strong></div>
              <div><span>Structure proxy</span><strong>{(result.metrics.input_output_edge_agreement_proxy * 100).toFixed(0)}%</strong></div>
              <div><span>Mean consistency</span><strong>{(conf.mean * 100).toFixed(0)}%</strong></div>
              <div><span>Model version</span><strong>{result.model_version}</strong></div>
              <div>
                <span>Held-out evaluation</span>
                <strong className={result.metrics.held_out_evaluation === 'not_run' ? 'warn-text' : ''}>
                  {result.metrics.held_out_evaluation === 'not_run' ? 'Not run' : 'See report'}
                </strong>
              </div>
            </div>
            <p className="micro-note">{result.metrics.edge_method}. These are computed values from this run — not accuracy or ground truth.</p>
            <p className="micro-note">{confidenceText(result)}</p>
          </div>

          <div className="panel side-panel">
            <h3>Export result</h3>
            <p className="micro-note">{isPngPrototype
              ? 'Download the 256×256 model preview and JSON summary. The PNG source has no map CRS/transform, so no georeferenced export is available.'
              : 'Download the 256×256 model preview and a machine-readable summary. GeoTIFF inputs also get an extent/CRS-preserving RGB preview export; it is not a calibrated analytical product.'}</p>
            <div className="download-row">
              <a className="download-btn" href={result.urls.colour} download={`vyora-${result.result_id.slice(0, 8)}.png`}>
                <ImageDown size={17} /> Output PNG <Download size={14} />
              </a>
              <a className="download-btn secondary" href={result.urls.json} download={`vyora-${result.result_id.slice(0, 8)}.json`}>
                <FileJson size={17} /> Result JSON <Download size={14} />
              </a>
              {result.urls.geotiff && <a className="download-btn secondary" href={result.urls.geotiff} download={`vyora-${result.result_id.slice(0, 8)}.tif`}>
                <Map size={17} /> GeoTIFF preview <Download size={14} />
              </a>}
            </div>
          </div>

          <div className="disclaimer-box">
            <CheckCircle2 size={17} />
            <p>{result.disclaimer}</p>
          </div>
        </aside>
      </div>
    </section>
  )
}

function confidenceText(result: InferenceResult): string {
  const method = result.confidence_method.toLowerCase()
  if (method.includes('hand-authored')) {
    return 'Confidence here means agreement of fixed geographic rules under a mirror check. It is not model uncertainty.'
  }
  return 'Consistency is agreement between original and flipped-view model predictions. It is not calibrated uncertainty and does not measure real-world certainty.'
}
