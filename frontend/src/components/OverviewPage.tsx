import { ArrowRight, Clock3, Database, Gauge, Info, Radar, ShieldAlert } from 'lucide-react'
import type { DemoScene, Health, InferenceResult } from '../types'

type Page = 'overview' | 'analyse' | 'scenes' | 'method'
interface Props {
  health: Health | null
  scenes: DemoScene[]
  result: InferenceResult | null
  onNavigate: (page: Page) => void
  onChooseScene: (sceneId: string) => void
}

export function OverviewPage({ health, scenes, result, onNavigate, onChooseScene }: Props) {
  const modelState = health?.is_ai_inference ? 'Checkpoint inference' : health ? 'Development rules' : 'Checking API…'
  const modelVersion = health?.model_version ?? 'Waiting for backend'
  return (
    <main className="workspace-page overview-page" id="overview">
      <div className="page-title-row">
        <div><span className="section-kicker">VYORA OVERVIEW</span><h1>Earth observation, made reviewable.</h1><p>One place to inspect source imagery, model output and the evidence behind a run.</p></div>
        <button className="button-primary compact-button" onClick={() => onNavigate('analyse')}><Radar size={16} /> Start an analysis</button>
      </div>

      <section className="overview-hero-grid" aria-label="Workspace overview">
        <article className="data-card scene-library-card">
          <div className="card-heading"><div><span className="card-eyebrow">SCENE LIBRARY</span><h2>Start from a scene</h2></div><span className="count-chip"><Database size={13} /> {scenes.length} available</span></div>
          <div className="mini-scene-list">
            {scenes.slice(0, 4).map((scene) => <button className="mini-scene" key={scene.id} onClick={() => onChooseScene(scene.id)}>
              <img src={scene.image_url} alt="" loading="lazy" />
              <span><strong>{scene.name}</strong><small>{scene.region_label}</small></span>
              <ArrowRight size={14} />
            </button>)}
            {scenes.length === 0 && <p className="empty-copy">Demo scenes will appear when the API is available.</p>}
          </div>
          <p className="card-footnote"><Info size={12} /> Bundled examples are synthetic previews, not satellite captures.</p>
        </article>

        <article className="data-card earth-dashboard-card">
          <div className="earth-card-top"><span className="card-eyebrow">SPATIAL CONTEXT</span><span className="illustration-tag">ILLUSTRATION</span></div>
          <img src="/assets/vyora-earth-pointcloud.png" alt="Decorative point-cloud Earth; not live geospatial data" />
          <div className="earth-card-copy"><strong>Global perspective.</strong><span>This graphic is not a live map, feed, or analysis result.</span></div>
          <div className="earth-grid-lines" aria-hidden="true" />
        </article>

        <article className="data-card model-card">
          <div className="card-heading"><div><span className="card-eyebrow">MODEL STATUS</span><h2>{health?.is_ai_inference ? 'Checkpoint ready' : health ? 'Demo mode' : 'Connecting'}</h2></div><span className={`state-dot ${health?.is_ai_inference ? 'good' : ''}`} /></div>
          <div className="model-status-row"><span>Execution state</span><strong>{modelState}</strong></div>
          <div className="model-status-row"><span>Version</span><strong className="mono-value">{modelVersion}</strong></div>
          <div className="model-status-row"><span>Checkpoint file</span><strong>{health ? (health.checkpoint_available ? 'Available' : 'Not loaded') : 'Checking'}</strong></div>
          <div className="model-disclaimer"><ShieldAlert size={15} /><span>Model state is reported by the local API. It is not a hazard-detection status.</span></div>
          <button className="text-link" onClick={() => onNavigate('method')}>Review method & limits <ArrowRight size={14} /></button>
        </article>
      </section>

      <section className="metric-row" aria-label="Measured session values">
        <article className="metric-card"><span><Database size={15} /> DEMO SCENES</span><strong>{scenes.length}</strong><small>Available from this API session</small></article>
        <article className="metric-card"><span><Clock3 size={15} /> LAST RUN TIME</span><strong>{result ? `${result.metrics.runtime_ms} ms` : '—'}</strong><small>{result ? 'Observed for the current result' : 'Run a scene to record this value'}</small></article>
        <article className="metric-card"><span><Gauge size={15} /> FLIP CONSISTENCY</span><strong>{result ? `${(result.confidence_summary.mean * 100).toFixed(0)}%` : '—'}</strong><small>{result ? 'Stability cue, not calibrated confidence' : 'Not measured in this session'}</small></article>
        <article className="metric-card"><span><Radar size={15} /> STRUCTURE PROXY</span><strong>{result ? `${(result.metrics.input_output_edge_agreement_proxy * 100).toFixed(0)}%` : '—'}</strong><small>{result ? 'Image proxy, not accuracy' : 'Not measured in this session'}</small></article>
      </section>

      <section className="latest-run-card">
        <div><span className="card-eyebrow">SESSION ACTIVITY</span><h2>{result ? 'Latest run' : 'No analysis in this session yet'}</h2><p>{result ? `${result.source.name} · ${result.input.width} × ${result.input.height} · ${result.model_version}` : 'Choose a scene to create a result. Only values measured in this session are shown here.'}</p></div>
        {result && <span className={`run-mode-badge ${result.is_ai_inference ? 'model' : ''}`}>{result.is_ai_inference ? 'MODEL INFERENCE' : 'DEVELOPMENT MODE'}</span>}
        <button className="button-secondary" onClick={() => onNavigate('analyse')}>{result ? 'Open result workspace' : 'Choose a scene'} <ArrowRight size={14} /></button>
      </section>
    </main>
  )
}
