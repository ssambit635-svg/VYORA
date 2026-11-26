import { Activity, ArrowDownRight, ArrowRight, Check, CircleDot, Eye, FileJson2, Layers3, Radar, ShieldCheck, Waypoints } from 'lucide-react'
import type { Health } from '../types'

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
        <div className="hero-earth-panel" aria-label="Illustrative point-cloud globe">
          <div className="earth-caption"><span>GLOBAL VIEW</span><span>ILLUSTRATION ONLY</span></div>
          <img src="/assets/vyora-earth-pointcloud.png" alt="Subdued lavender point-cloud Earth illustration" />
          <div className="earth-footnote"><CircleDot size={12} /> Not a live activity map or current satellite feed</div>
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
          <p>Move from a selected scene to a side-by-side visual review, then record a human note. Each step stays labelled for what it actually is.</p>
          <button className="text-link" onClick={onEnter}>Open the workspace <ArrowRight size={15} /></button>
        </div>
        <div className="workflow-steps">
          <article><span className="workflow-number">01</span><Layers3 size={18} /><h3>Choose a scene</h3><p>Start with a bundled example or select a supported local image.</p></article>
          <article><span className="workflow-number">02</span><Eye size={18} /><h3>Compare views</h3><p>Keep source, estimate and the consistency cue visible together.</p></article>
          <article><span className="workflow-number">03</span><Check size={18} /><h3>Review & export</h3><p>Mark a region, add a human note and export the review record.</p></article>
        </div>
      </section>

      <section className="public-data-section" id="dataset">
        <div className="public-section-heading"><span className="section-kicker">TWO SENSORS · DIFFERENT EVIDENCE</span><h2>Radar is not a camera.</h2><p>Sentinel‑1 and Sentinel‑2 measure different things. The A/B labels below describe the prepared image pairs; they are not satellite product names.</p></div>
        <div className="sensor-card-grid">
          <article className="sensor-card"><span className="sensor-symbol radar"><Radar size={18} /></span><span className="card-eyebrow">B-SIDE · SAR INPUT</span><h3>Sentinel‑1</h3><p>Active radar measures microwave backscatter. It can acquire at night and is less affected by cloud cover than optical imagery.</p><small>Radar texture and brightness are not direct land-cover labels.</small></article>
          <article className="sensor-card"><span className="sensor-symbol optical"><Eye size={18} /></span><span className="card-eyebrow">A-SIDE · PAIRED REFERENCE</span><h3>Sentinel‑2</h3><p>Optical multispectral imagery measures reflected sunlight, including visible and near-infrared bands. Clouds can obscure the surface.</p><small>A paired target is a training reference, not perfect ground truth.</small></article>
          <article className="sensor-card mapping-card"><span className="sensor-symbol mapping"><Waypoints size={18} /></span><span className="card-eyebrow">CURRENT CHECKPOINT CONTRACT</span><h3>Prepared PNG pair</h3><p>The documented B-side input is grayscale and duplicated into two model channels; the paired A-side image is the RGB-style target.</p><small>This is not raw SAFE inference or a verified separate VV/VH checkpoint.</small></article>
        </div>
      </section>

      <section className="public-review-section" id="review">
        <div className="public-section-heading"><span className="section-kicker">WHAT A RUN ACTUALLY RETURNS</span><h2>Four useful views.<br />No invented certainty.</h2><p>The summary reflects API output for the selected run. Missing model outputs stay marked as unavailable.</p></div>
        <div className="review-card-grid">
          <article><span className="review-index">01</span><Eye size={18} /><h3>Source & estimate</h3><p>Compare the input with an RGB-style pixel estimate. The estimate is not recovered true colour.</p></article>
          <article><span className="review-index">02</span><Activity size={18} /><h3>Consistency</h3><p>Inspect the API-returned stability cue. Its method depends on the active runner; it is not calibrated uncertainty.</p></article>
          <article><span className="review-index">03</span><Layers3 size={18} /><h3>Intelligence summary</h3><p>See dimensions, API processing time, input type and CRS when present. Palette shares are explicitly not validated class detections.</p></article>
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
      <footer className="public-footer"><span>VYORA<span className="wordmark-period">.</span></span><span>Earth observation interface · Research prototype</span><span className="public-live-status"><i /> {health ? health.mode.toUpperCase() : 'API CHECKING'}</span></footer>
    </main>
  )
}
