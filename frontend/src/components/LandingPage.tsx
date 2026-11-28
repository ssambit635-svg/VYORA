import '@fontsource/inter/latin-400.css'
import '@fontsource/inter/latin-500.css'
import '@fontsource/inter/latin-600.css'
import '@fontsource/space-grotesk/latin-500.css'
import '@fontsource/space-grotesk/latin-600.css'
import { Activity, ArrowRight, Check, Database, Eye, Layers3, Radar, ShieldAlert } from 'lucide-react'
import type { DemoScene, Health } from '../types'
import { lazy, Suspense, useRef } from 'react'
import { NASA_EYES_URL } from '../externalLinks'
const InteractiveEarth = lazy(() => import('./InteractiveEarth').then((module) => ({ default: module.InteractiveEarth })))
import { SiteFooter } from './SiteFooter'

interface Props {
  sceneCount: number
  scenes: DemoScene[]
  health: Health | null
  onEnter: () => void
  onMethod: () => void
}

export function LandingPage({ sceneCount, scenes, health, onEnter, onMethod }: Props) {
  const scrollStageRef = useRef<HTMLElement>(null)
  const mode = health ? (health.is_ai_inference ? 'Checkpoint inference' : 'Development rules') : 'Checking local API'
  const checkpoint = health ? (health.checkpoint_available ? 'Available' : 'Not loaded') : 'Checking'
  return (
    <main className="public-page dashboard-landing" id="home">
      <section className="landing-scroll-stage" ref={scrollStageRef} aria-label="Vyora overview">
        <div className="dashboard-board">
          <div className="dashboard-intro">
            <div>
              <span className="section-kicker">VYORA OVERVIEW</span>
              <h1>Earth observation, made reviewable.</h1>
              <p>Confidence-aware SAR interpretation. Inspect the source, returned estimate and review evidence in one place.</p>
            </div>
            <button className="button-primary dashboard-start" onClick={onEnter}><Radar size={16} /> Start an analysis <ArrowRight size={15} /></button>
          </div>

          <div className="dashboard-hero-grid">
            <aside className="dashboard-side-column" aria-label="Scene and model status">
              <section className="dashboard-card landing-scenes-card" id="scene-library">
                <div className="dashboard-card-heading">
                  <div><span className="card-eyebrow">SCENE LIBRARY</span><h2>Start with a scene</h2></div>
                  <span className="dashboard-count"><Database size={12} /> {sceneCount} available</span>
                </div>
                <div className="landing-scene-list">
                  {scenes.slice(0, 4).map((scene) => (
                    <div className="landing-scene-row" key={scene.id}>
                      <img src={scene.image_url} alt="" loading="lazy" />
                      <span><strong>{scene.name}</strong><small>{scene.region_label || 'Bundled example'}</small></span>
                      <ArrowRight size={14} />
                    </div>
                  ))}
                  {scenes.length === 0 && <p className="landing-empty-scenes">Examples appear here when the local API is available.</p>}
                </div>
                <button className="landing-text-button landing-scene-cta" onClick={onEnter}>Open scene library <ArrowRight size={14} /></button>
                <p className="landing-card-note"><ShieldAlert size={13} /> Synthetic examples, not satellite captures.</p>
              </section>

              <section className="dashboard-card landing-model-card">
                <div className="dashboard-card-heading">
                  <div><span className="card-eyebrow">MODEL STATUS</span><h2>{health?.is_ai_inference ? 'Checkpoint ready' : health ? 'Demo mode' : 'Connecting'}</h2></div>
                  <span className={`landing-state-dot ${health?.is_ai_inference ? 'is-model' : ''}`} aria-label={health?.is_ai_inference ? 'Checkpoint inference available' : 'Development mode'} />
                </div>
                <div className="landing-status-row"><span>Execution</span><strong>{mode}</strong></div>
                <div className="landing-status-row"><span>Version</span><strong className="landing-mono">{health?.model_version ?? 'Waiting for API'}</strong></div>
                <div className="landing-status-row"><span>Checkpoint</span><strong>{checkpoint}</strong></div>
              </section>
            </aside>

            <section className="dashboard-card landing-globe-card" aria-label="Interactive 3D Earth and spacecraft models">
              <div className="globe-card-header"><span className="card-eyebrow">SPATIAL CONTEXT</span><span className="globe-live-tag"><i /> 3D MODEL · NOT LIVE TRACKING</span></div>
              <div className="landing-globe-scroll-frame">
                <Suspense fallback={<div className="interactive-earth-loading">Loading 3D Earth…</div>}>
                  <InteractiveEarth scrollStageRef={scrollStageRef} />
                </Suspense>
                <span className="globe-coordinate-label globe-label-top">EARTH / 01</span>
                <span className="globe-coordinate-label globe-label-bottom">BLUE MARBLE · NASA</span>
              </div>
              <div className="globe-card-caption">
                <strong>Earth, in orbit.</strong>
                <span>NASA Blue Marble texture · GOES and Landsat 8 spacecraft models · illustrative orbits, not to scale.</span>
              </div>
            </section>

            <aside className="dashboard-side-column dashboard-insight-column" aria-label="Interpretation status">
              <section className="dashboard-card landing-confidence-card">
                <div className="dashboard-card-heading">
                  <div><span className="card-eyebrow">INTERPRETATION CONFIDENCE</span><h2>Evidence before score.</h2></div>
                  <span className="confidence-menu" aria-hidden="true">···</span>
                </div>
                <div className="confidence-dial" aria-hidden="true"><div className="confidence-dial-track" /><div className="confidence-dial-value" /><span>—</span></div>
                <div className="confidence-empty-state"><Activity size={15} /><div><strong>No run selected</strong><span>This model returns a consistency cue, not calibrated confidence.</span></div></div>
                <div className="landing-output-status">
                  <div><span>Calibrated confidence</span><strong>Not reported</strong></div>
                  <div><span>Consistency cue</span><strong>After a run</strong></div>
                  <div><span>Feature masks</span><strong>Unavailable</strong></div>
                </div>
                <button className="landing-text-button" onClick={onEnter}>Choose a scene to begin <ArrowRight size={14} /></button>
              </section>
              <section className="dashboard-card landing-source-card">
                <span className="card-eyebrow">SPACECRAFT MODELS</span>
                <a href="https://science.nasa.gov/mission/goes-spacecraft-3d-model/" target="_blank" rel="noreferrer"><span><i className="satellite-status-dot" /> GOES · NASA 3D model</span><ArrowRight size={13} /></a>
                <a href="https://science.nasa.gov/mission/landsat-8/" target="_blank" rel="noreferrer"><span><i className="satellite-status-dot satellite-status-blue" /> Landsat 8 · NASA 3D model</span><ArrowRight size={13} /></a>
                <small>Rendered models only. No position feed is connected.</small>
              </section>
            </aside>
          </div>

          <div className="dashboard-facts" aria-label="Current workspace facts">
            <article><span><Database size={14} /> EXAMPLE SCENES</span><strong>{sceneCount}</strong><small>Bundled synthetic previews</small></article>
            <article><span><Activity size={14} /> ACTIVE RUNNER</span><strong>{health ? (health.is_ai_inference ? 'Checkpoint' : 'Development') : 'Checking'}</strong><small>{health?.model_version ?? 'Reported by the local API'}</small></article>
            <article><span><Eye size={14} /> RESULT REVIEW</span><strong>Source + estimate</strong><small>Compared side by side in the workspace</small></article>
            <article><span><Layers3 size={14} /> HUMAN REVIEW</span><strong>Notes & export</strong><small>Image-space annotations, not map labels</small></article>
          </div>
        </div>
      </section>

      <section className="public-workflow landing-workflow" id="workflow">
        <div className="section-intro">
          <span className="section-kicker">A TRACEABLE WORKFLOW</span>
          <h2>Evidence first.<br />Interpretation second.</h2>
          <p>Follow a scene through the local API, visual review and a human-authored note. Each stage stays labelled for what it actually is.</p>
          <button className="landing-text-button" onClick={onMethod}>Review scope & limits <ArrowRight size={14} /></button>
        </div>
        <div className="workflow-diagram" role="list" aria-label="Vyora analysis workflow">
          <article className="workflow-node" role="listitem"><span className="workflow-number">01</span><Layers3 size={19} /><span className="workflow-node-label">INPUT</span><h3>Choose a scene</h3><p>Bundled synthetic example or a supported local image.</p></article>
          <div className="workflow-arrow" aria-hidden="true"><ArrowRight size={20} /><span>local API</span></div>
          <article className="workflow-node" role="listitem"><span className="workflow-number">02</span><Eye size={19} /><span className="workflow-node-label">ESTIMATE</span><h3>Compare views</h3><p>Keep the source and returned estimate visible together.</p></article>
          <div className="workflow-arrow" aria-hidden="true"><ArrowRight size={20} /><span>human review</span></div>
          <article className="workflow-node" role="listitem"><span className="workflow-number">03</span><Check size={19} /><span className="workflow-node-label">REVIEW</span><h3>Note & export</h3><p>Mark an image region, add a note and export the record.</p></article>
        </div>
      </section>

      <section className="landing-scope" id="limits">
        <div><span className="section-kicker">SCOPE, STATED PLAINLY</span><h2>Not a warning product.</h2></div>
        <p>Vyora is an image-interpretation demonstrator. Outputs are estimates, not ground truth. The current model does not detect floods or cyclones; verify results with authoritative data and expert review.</p>
        <a href={NASA_EYES_URL} target="_blank" rel="noreferrer">Open NASA Eyes for real satellite positions <ArrowRight size={14} /></a>
      </section>
      <SiteFooter runnerLabel={health ? health.mode.toUpperCase() : 'API CHECKING'} />
    </main>
  )
}
