import { ArrowRight, Activity, Clock3, Database, Gauge, Info, Orbit, Radar, ShieldAlert, Signal, Sparkles } from 'lucide-react'
import { lazy, Suspense, useRef } from 'react'
import type { DemoScene, Health, InferenceResult } from '../types'

const InteractiveEarth = lazy(() => import('./InteractiveEarth').then((module) => ({ default: module.InteractiveEarth })))
type Page = 'overview' | 'analyse' | 'scenes' | 'method'
interface Props {
  health: Health | null
  scenes: DemoScene[]
  result: InferenceResult | null
  onNavigate: (page: Page) => void
  onChooseScene: (sceneId: string) => void
}

export function OverviewPage({ health, scenes, result, onNavigate, onChooseScene }: Props) {
  const earthStageRef = useRef<HTMLElement>(null)
  const modelState = health?.is_ai_inference ? 'Checkpoint inference' : health ? 'Development rules' : 'API unavailable'
  const modelVersion = health?.model_version ?? 'Not reported'
  return (
    <main className="workspace-page overview-page" id="overview" ref={earthStageRef}>
      <div className="ops-heading">
        <div><span className="section-kicker">VYORA / OPERATIONS OVERVIEW</span><h1>Earth observation, <em>in context.</em></h1><p>Explore the 3D scene, inspect session status and open an image for review.</p></div>
        <div className="ops-heading-actions"><span className="local-session"><i /> LOCAL DEMO SESSION</span><button className="button-primary compact-button" onClick={() => onNavigate('analyse')}><Radar size={15} /> Start an analysis <ArrowRight size={14} /></button></div>
      </div>

      <section className="ops-console-grid" aria-label="Interactive Earth and session controls">
        <article className="ops-earth-panel">
          <div className="ops-panel-top"><div><span className="card-eyebrow">GLOBAL SPATIAL CONTEXT</span><h2>Earth & orbital models</h2></div><span className="illustration-tag"><i /> SIMULATED VIEW · NOT LIVE</span></div>
          <div className="ops-earth-stage">
            <div className="ops-earth-grid" aria-hidden="true" />
            <Suspense fallback={<div className="interactive-earth-loading">Loading 3D Earth and spacecraft…</div>}>
              <InteractiveEarth scrollStageRef={earthStageRef} enableScrollZoom />
            </Suspense>
            <span className="ops-coordinate ops-coordinate-a">EARTH · 3D SCENE</span>
            <span className="ops-coordinate ops-coordinate-b">ORBIT LINES · ILLUSTRATIVE / NOT TO SCALE</span>
            <div className="ops-earth-legend"><span><i className="legend-violet" /> GOES spacecraft model</span><span><i className="legend-blue" /> Landsat 8 model</span></div>
          </div>
          <div className="ops-earth-footer"><span><Orbit size={13} /> Drag to rotate · Scroll over Earth to zoom</span><span>NASA Earth textures · NASA spacecraft 3D assets</span></div>
        </article>

        <aside className="ops-side-stack" aria-label="Session and model details">
          <article className="ops-status-panel">
            <div className="ops-panel-top compact"><div><span className="card-eyebrow">SESSION STATUS</span><h2>Review console</h2></div><span className="ops-status-icon"><Signal size={15} /></span></div>
            <div className="ops-status-feature"><span className="ops-status-pulse" /><div><strong>Local workspace</strong><small>No satellite telemetry connection</small></div></div>
            <div className="ops-divider" />
            <div className="ops-readout"><span>Inference runner</span><strong>{modelState}</strong></div>
            <div className="ops-readout"><span>Model version</span><strong className="mono-value">{modelVersion}</strong></div>
            <div className="ops-readout"><span>Checkpoint file</span><strong>{health ? (health.checkpoint_available ? 'Available' : 'Not loaded') : 'Not reported'}</strong></div>
            <p className="ops-honesty-note"><Info size={13} /> Status is reported by the local API; it is not a hazard alert.</p>
            <button className="ops-text-link" onClick={() => onNavigate('method')}>Method & limitations <ArrowRight size={13} /></button>
          </article>

          <article className="ops-asset-panel">
            <div className="ops-panel-top compact"><div><span className="card-eyebrow">SCENE LIBRARY</span><h2>Choose an image</h2></div><span className="ops-count">{scenes.length} EXAMPLES</span></div>
            <div className="ops-scene-list">
              {scenes.slice(0, 3).map((scene, index) => <button className="ops-scene-row" key={scene.id} onClick={() => onChooseScene(scene.id)}>
                <span className="ops-scene-index">0{index + 1}</span><img src={scene.image_url} alt="" loading="lazy" /><span className="ops-scene-copy"><strong>{scene.name}</strong><small>{scene.region_label || 'Bundled synthetic preview'}</small></span><ArrowRight size={13} />
              </button>)}
              {scenes.length === 0 && <p className="ops-empty">Scene examples are unavailable until the API connects.</p>}
            </div>
            <p className="ops-synthetic-note"><Sparkles size={12} /> Bundled examples are synthetic, not satellite captures.</p>
          </article>
        </aside>
      </section>

      <section className="ops-measurements" aria-label="Measured session values">
        <article className="ops-measure-card"><span><Clock3 size={14} /> LAST RUN DURATION</span><strong>{result ? `${result.metrics.runtime_ms} ms` : '—'}</strong><small>{result ? 'Measured in this session' : 'No run recorded this session'}</small></article>
        <article className="ops-measure-card"><span><Gauge size={14} /> CONSISTENCY CUE</span><strong>{result ? `${(result.confidence_summary.mean * 100).toFixed(0)}%` : '—'}</strong><small>{result ? 'Not calibrated confidence' : 'Not measured'}</small></article>
        <article className="ops-measure-card"><span><Activity size={14} /> STRUCTURE PROXY</span><strong>{result ? `${(result.metrics.input_output_edge_agreement_proxy * 100).toFixed(0)}%` : '—'}</strong><small>{result ? 'Image-space proxy, not accuracy' : 'Not measured'}</small></article>
        <article className="ops-measure-card ops-measure-scene"><span><Database size={14} /> EXAMPLE SCENES</span><strong>{scenes.length}</strong><small>Available in the local demo</small></article>
      </section>

      <section className="ops-latest-run">
        <div className="ops-latest-icon"><Radar size={17} /></div><div className="ops-latest-copy"><span className="card-eyebrow">ANALYSIS ACTIVITY</span><h2>{result ? 'Latest local interpretation' : 'Ready for image review'}</h2><p>{result ? `${result.source.name} · ${result.input.width} × ${result.input.height} · ${result.model_version}` : 'Choose a bundled scene or upload a supported image to create a session result.'}</p></div>
        {result && <span className={`run-mode-badge ${result.is_ai_inference ? 'model' : ''}`}>{result.is_ai_inference ? 'MODEL INFERENCE' : 'DEVELOPMENT MODE'}</span>}
        <button className="button-secondary" onClick={() => onNavigate('analyse')}>{result ? 'Open result' : 'Start an analysis'} <ArrowRight size={14} /></button>
      </section>
      <p className="ops-footer-note"><ShieldAlert size={13} /> Earth textures and spacecraft are for visual context only; no live orbital position feed is connected.</p>
    </main>
  )
}
