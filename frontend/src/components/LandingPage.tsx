import { Activity, ArrowDownRight, ArrowRight, Check, Eye, ExternalLink, FileJson2, Layers3, Radar, ShieldCheck, Waypoints } from 'lucide-react'
import type { Health } from '../types'
import { InteractiveEarth, NASA_EYES_URL } from './InteractiveEarth'
import { SiteFooter } from './SiteFooter'

interface Props {
  sceneCount: number
  health: Health | null
  onEnter: () => void
  onMethod: () => void
}

export function LandingPage({ sceneCount, health, onEnter, onMethod }: Props) {
  const runnerLabel = health ? (health.is_ai_inference ? 'Checkpoint inference available' : 'Development renderer active') : 'Checking local API status'
  return (
    <main className="public-page" id="home">
      <section className="public-hero" id="product">
        <div className="hero-copy-block">
          <div className="eyebrow-line"><span className="status-square" /> EARTH OBSERVATION · SAR INTERPRETATION</div>
          <h1>Read the signal.<br /><span>Keep the evidence.</span></h1>
          <p className="hero-description">A clear workspace for comparing radar imagery with an estimated visual interpretation—without hiding the source or overstating what the model knows.</p>
          <div className="hero-cta-row">
            <button className="button-primary" onClick={onEnter}>Enter the demo workspace <ArrowRight size={16} /></button>
            <button className="button-quiet" onClick={onMethod}>How it works <ArrowDownRight size={16} /></button>
          </div>
          <div className="hero-assurance"><ShieldCheck size={16} /><span>Local demo access · No account credentials collected</span></div>
        </div>
        <div className="hero-globe-column">
          <div className="hero-earth-panel">
            <div className="earth-caption"><span>INTERACTIVE EARTH</span><span>VECTOR GLOBE · NOT LIVE DATA</span></div>
            <InteractiveEarth />
          </div>
          <a className="hero-satellite-link" href={NASA_EYES_URL} target="_blank" rel="noreferrer">
            <span><Radar size={15} /> Open real satellite positions in NASA Eyes</span><ExternalLink size={14} />
          </a>
          <p className="hero-satellite-note">NASA’s live satellite view opens separately; orbit markers here are illustrative only.</p>
        </div>
        <div className="hero-bottomline">
          <span>OBSERVE</span><i /><span>COMPARE</span><i /><span>REVIEW</span>
          <span className="bottomline-scenes"><b>{sceneCount}</b> bundled demonstration scenes</span>
        </div>
      </section>

      <section className="public-workflow" id="workflow">
        <div className="section-intro">
          <span className="section-kicker">A TRACEABLE WORKFLOW</span>
          <h2>Evidence first.<br />Interpretation second.</h2>
          <p>Follow one scene through the local API, visual review and a human-authored note. Each stage stays labelled for what it actually is.</p>
        </div>
        <div className="workflow-diagram" role="list" aria-label="Vyora analysis workflow">
          <article className="workflow-node" role="listitem"><span className="workflow-number">01</span><Layers3 size={19} /><span className="workflow-node-label">INPUT</span><h3>Choose a scene</h3><p>Bundled synthetic example or a supported local image.</p></article>
          <div className="workflow-arrow" aria-hidden="true"><ArrowRight size={20} /><span>local API</span></div>
          <article className="workflow-node" role="listitem"><span className="workflow-number">02</span><Eye size={19} /><span className="workflow-node-label">ESTIMATE</span><h3>Compare views</h3><p>Keep source, estimate and consistency cue in view.</p></article>
          <div className="workflow-arrow" aria-hidden="true"><ArrowRight size={20} /><span>human review</span></div>
          <article className="workflow-node" role="listitem"><span className="workflow-number">03</span><Check size={19} /><span className="workflow-node-label">REVIEW</span><h3>Note & export</h3><p>Mark an image region, add a note and export the record.</p></article>
        </div>
      </section>

      <section className="public-data-section" id="dataset">
        <div className="public-section-heading"><span className="section-kicker">DIFFERENT SENSORS · DIFFERENT EVIDENCE</span><h2>Radar is not a camera.</h2><p>These cards explain the general sensor types. The source archive’s A/B folder labels do not independently verify satellite provenance.</p></div>
        <div className="sensor-card-grid">
          <article className="sensor-card"><span className="sensor-symbol radar"><Radar size={18} /></span><span className="card-eyebrow">GENERAL SENSOR CONTEXT</span><h3>Synthetic aperture radar</h3><p>Active radar measures microwave backscatter. It can acquire at night and is less affected by cloud cover than optical imagery.</p><small>Radar texture and brightness are not direct land-cover labels.</small></article>
          <article className="sensor-card"><span className="sensor-symbol optical"><Eye size={18} /></span><span className="card-eyebrow">GENERAL SENSOR CONTEXT</span><h3>Multispectral optical</h3><p>Optical sensors measure reflected sunlight across visible and infrared bands. Clouds can obscure the surface.</p><small>A paired image target is a training reference, not perfect ground truth.</small></article>
          <article className="sensor-card mapping-card"><span className="sensor-symbol mapping"><Waypoints size={18} /></span><span className="card-eyebrow">CURRENT CHECKPOINT CONTRACT</span><h3>Prepared PNG pair</h3><p>The documented B-side input is grayscale and duplicated into two model channels; the paired A-side image is the RGB-style target.</p><small>This is not raw SAFE inference or a verified separate VV/VH checkpoint.</small></article>
        </div>
      </section>

      <section className="public-review-section" id="review">
        <div className="public-section-heading"><span className="section-kicker">WHAT A RUN ACTUALLY RETURNS</span><h2>Useful views.<br />No invented certainty.</h2><p>The summary reflects API output for the selected run. Missing model outputs stay marked as unavailable.</p></div>
        <div className="review-card-grid">
          <article><span className="review-index">01</span><Eye size={18} /><h3>Source & estimate</h3><p>Compare the input with an RGB-style pixel estimate. The estimate is not recovered true colour.</p></article>
          <article><span className="review-index">02</span><Activity size={18} /><h3>Consistency</h3><p>Inspect the API-returned stability cue. Its method depends on the active runner; it is not calibrated uncertainty.</p></article>
          <article><span className="review-index">03</span><Layers3 size={18} /><h3>Run summary</h3><p>See dimensions, API processing time, input type and CRS when present. Palette shares are not validated class detections.</p></article>
          <article><span className="review-index">04</span><FileJson2 size={18} /><h3>Human review</h3><p>Mark an image-space region, add a user-authored note and export that annotation as JSON.</p></article>
        </div>
      </section>

      <section className="public-status-section">
        <div className="status-copy"><span className="section-kicker">LIVE API-REPORTED STATE</span><h2>Know which runner produced the view.</h2><p>The workspace reads its current mode and version from the API rather than assuming a model is active.</p></div>
        <div className="runner-status-card"><span className={`runner-status-mark ${health?.is_ai_inference ? 'model' : ''}`} /><div><small>EXECUTION STATUS</small><strong>{runnerLabel}</strong><span>{health?.model_version ?? 'Waiting for API health response'}</span></div><button className="text-link" onClick={onEnter}>Open workspace <ArrowRight size={14} /></button></div>
      </section>

      <section className="public-limits" id="limits">
        <span className="section-kicker">SCOPE, STATED PLAINLY</span>
        <p>Vyora is an image-interpretation demonstrator. Its current model is <strong>not a flood detector, cyclone forecast, or official warning system.</strong></p>
        <span>Feature segmentation and attention maps are not produced by the current model. Verify image estimates with authoritative data and expert review.</span>
      </section>
      <section className="public-final-cta"><div><span className="section-kicker">START WITH THE EVIDENCE</span><h2>Open a scene. Inspect every step.</h2><p>Use the local demo workspace to explore the source, result and review tools.</p></div><button className="button-primary" onClick={onEnter}>Enter demo workspace <ArrowRight size={16} /></button></section>
      <SiteFooter runnerLabel={health ? health.mode.toUpperCase() : 'API CHECKING'} />
    </main>
  )
}
