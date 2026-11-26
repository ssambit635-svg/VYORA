import { ArrowDownRight, ArrowRight, Check, CircleDot, Eye, Layers3, ShieldCheck } from 'lucide-react'

interface Props {
  sceneCount: number
  onEnter: () => void
  onMethod: () => void
}

export function LandingPage({ sceneCount, onEnter, onMethod }: Props) {
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

      <section className="public-limits" id="limits">
        <span className="section-kicker">SCOPE, STATED PLAINLY</span>
        <p>Vyora is an image-interpretation demonstrator. Its current model is <strong>not a flood detector, cyclone forecast, or official warning system.</strong></p>
        <span>Estimated pixels are not ground truth. Verify with authoritative data and expert review.</span>
      </section>
      <footer className="public-footer"><span>VYORA<span className="wordmark-period">.</span></span><span>Earth observation interface · Research prototype</span></footer>
    </main>
  )
}
