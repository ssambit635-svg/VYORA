import { ArrowRight, Activity, Clock3, Gauge, Info, Orbit, Radar, ShieldAlert, Signal } from 'lucide-react'
import { lazy, Suspense, useRef } from 'react'
import type { Health, InferenceResult } from '../types'

const InteractiveEarth = lazy(() => import('./InteractiveEarth').then((module) => ({ default: module.InteractiveEarth })))
type Page = 'overview' | 'analyse' | 'scenes' | 'method'
interface Props {
  health: Health | null
  result: InferenceResult | null
  onNavigate: (page: Page) => void
}

export function OverviewPage({ health, result, onNavigate }: Props) {
  const earthStageRef = useRef<HTMLElement>(null)
  const modelState = health?.is_ai_inference ? 'Checkpoint inference' : health ? 'Development rules' : 'API unavailable'
  const channelStats = result?.input.channel_stats ?? []
  const modelVersion = health?.model_version ?? 'Not reported'
  return (
    <main className="workspace-page overview-page" id="overview" ref={earthStageRef}>
      <div className="ops-heading">
        <div><span className="section-kicker">VYORA / OPERATIONS OVERVIEW</span><h1>Earth observation, <em>in context.</em></h1><p>Explore the 3D scene, inspect measured image statistics and review session state.</p></div>
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
            <div className="ops-earth-legend"><span><i className="legend-goes" /> GOES spacecraft model</span><span><i className="legend-landsat" /> Landsat 8 model</span></div>
          </div>
          <div className="ops-earth-footer"><span><Orbit size={13} /> Drag to rotate · Scroll over Earth to zoom</span><span>NASA Earth textures · NASA spacecraft 3D assets</span></div>
        </article>

        <aside className="ops-side-stack" aria-label="Session and input profile">
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
            <div className="ops-panel-top compact"><div><span className="card-eyebrow">CURRENT INPUT</span><h2>{result ? result.source.name : 'No image in this session'}</h2></div><span className="ops-count">{result ? result.source.type.toUpperCase() : 'EMPTY'}</span></div>
            {result ? <>
              <div className="ops-readout"><span>Image dimensions</span><strong>{result.input.width} × {result.input.height}</strong></div>
              <div className="ops-readout"><span>Input kind</span><strong>{result.input.input_kind ?? `${result.input.channels} channel preview`}</strong></div>
              <div className="ops-readout"><span>Channels</span><strong>{result.input.polarizations?.join(' / ') ?? result.input.channels}</strong></div>
              <p className="ops-synthetic-note"><Info size={12} /> Pixel summaries below are image statistics, not accuracy scores.</p>
            </> : <>
              <p className="ops-input-empty">Open a scene from the Scenes tab or upload an image in Analyse. Scene selection lives in one place.</p>
              <button className="ops-text-link" onClick={() => onNavigate('scenes')}>Open scene library <ArrowRight size={13} /></button>
            </>}
          </article>
        </aside>
      </section>

      <section className="ops-measurements" aria-label="Measured session values">
        <article className="ops-measure-card"><span><Clock3 size={14} /> LAST RUN DURATION</span><strong>{result ? `${result.metrics.runtime_ms} ms` : '—'}</strong><small>{result ? 'Measured in this session' : 'No run recorded this session'}</small></article>
        <article className="ops-measure-card"><span><Gauge size={14} /> MEAN CONSISTENCY CUE</span><strong>{result ? `${(result.confidence_summary.mean * 100).toFixed(1)}%` : '—'}</strong><small>{result ? 'Not calibrated confidence' : 'Not measured'}</small></article>
        <article className="ops-measure-card"><span><Activity size={14} /> STRUCTURE PROXY</span><strong>{result ? `${(result.metrics.input_output_edge_agreement_proxy * 100).toFixed(1)}%` : '—'}</strong><small>{result ? 'Edge agreement, not accuracy' : 'Not measured'}</small></article>
        <article className="ops-measure-card"><span><Orbit size={14} /> INPUT PIXELS</span><strong>{result ? (result.input.width * result.input.height).toLocaleString() : '—'}</strong><small>{result ? `${result.input.width} × ${result.input.height} image` : 'No input measured'}</small></article>
      </section>

      <section className="ops-statistics" aria-label="Measured image statistics">
        <div className="ops-statistics-heading"><div><span className="card-eyebrow">MEASURED FROM THIS RUN</span><h2>Image statistics</h2></div><span className="ops-statistics-method">Output-map summaries · not real-world certainty</span></div>
        {result ? <div className="ops-statistics-grid">
          <article className="ops-stat-card">
            <div className="ops-stat-title"><div><span className="stat-micro-label">OUTPUT PIXELS</span><h3>Consistency-map bands</h3></div><span className={`ops-level-tag level-${result.confidence_summary.level}`}>{result.confidence_summary.level.toUpperCase()} MEAN</span></div>
            <p className="ops-stat-description">Share of output pixels within each displayed consistency range. These are not probabilities of correctness.</p>
            <div className="ops-band-stack" role="img" aria-label={`Low ${result.confidence_summary.low_pct} percent, medium ${result.confidence_summary.medium_pct} percent, high ${result.confidence_summary.high_pct} percent`}>
              <i style={{ width: `${result.confidence_summary.low_pct}%` }} /><i style={{ width: `${result.confidence_summary.medium_pct}%` }} /><i style={{ width: `${result.confidence_summary.high_pct}%` }} />
            </div>
            <div className="ops-band-legend"><span><i /> LOW <small>&lt; 45%</small><b>{result.confidence_summary.low_pct.toFixed(1)}%</b></span><span><i /> MID <small>45–70%</small><b>{result.confidence_summary.medium_pct.toFixed(1)}%</b></span><span><i /> HIGH <small>≥ 70%</small><b>{result.confidence_summary.high_pct.toFixed(1)}%</b></span></div>
            <small className="ops-stat-note">{result.confidence_summary.method_note}</small>
          </article>
          <article className="ops-stat-card ops-histogram-card">
            <div className="ops-stat-title"><div><span className="stat-micro-label">NORMALIZED INPUT</span><h3>Channel distributions</h3></div><span className="ops-count">16 BINS</span></div>
            {channelStats.length ? channelStats.map((channel) => {
              const maxBin = Math.max(1, ...channel.histogram)
              return <div className="ops-channel-row" key={channel.label}>
                <strong className="ops-channel-name">{channel.label}</strong>
                <div className="ops-channel-histogram" role="img" aria-label={`${channel.label} 16-bin normalized pixel histogram`}>
                  {channel.histogram.map((count, index) => <i key={index} style={{ height: `${Math.max(3, count / maxBin * 100)}%` }} />)}
                </div>
                <span className="ops-channel-summary">p02 {channel.p02.toFixed(2)} · p50 {channel.p50.toFixed(2)} · p98 {channel.p98.toFixed(2)}</span>
              </div>
            }) : <p className="ops-no-stat">Channel percentiles were not returned for this input.</p>}
            <small className="ops-stat-note">Histogram bins use per-channel normalized image values.</small>
          </article>
        </div> : <div className="ops-stat-empty"><span>—</span><p>Run an image to populate pixel-band shares and per-channel histogram statistics. No sample values are shown as live data.</p></div>}
      </section>

      <section className="ops-latest-run">
        <div className="ops-latest-icon"><Radar size={17} /></div><div className="ops-latest-copy"><span className="card-eyebrow">ANALYSIS ACTIVITY</span><h2>{result ? 'Latest local interpretation' : 'Ready for image review'}</h2><p>{result ? `${result.source.name} · ${result.input.width} × ${result.input.height} · ${result.model_version}` : 'Choose a scene in the Scenes tab or upload a supported image to create a session result.'}</p></div>
        {result && <span className={`run-mode-badge ${result.is_ai_inference ? 'model' : ''}`}>{result.is_ai_inference ? 'MODEL INFERENCE' : 'DEVELOPMENT MODE'}</span>}
        <button className="button-secondary" onClick={() => onNavigate('analyse')}>{result ? 'Open result' : 'Start an analysis'} <ArrowRight size={14} /></button>
      </section>
      <p className="ops-footer-note"><ShieldAlert size={13} /> Earth textures and spacecraft are for visual context only; no live orbital position feed is connected.</p>
    </main>
  )
}
