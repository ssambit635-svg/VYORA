import { ArrowRight, Binary, Gauge, Layers, ScanLine, ShieldAlert } from 'lucide-react'

const PIPELINE = [
  { icon: ScanLine, title: 'Dual-pol input', text: 'A calibrated, co-registered Sentinel-1 GeoTIFF supplies VV and VH bands; each is robustly normalized and tiled.' },
  { icon: Binary, title: 'U-Net generator', text: 'A compact two-channel ResU-Net maps VV/VH to a three-channel Sentinel-2-style visual target when a trained checkpoint is available.' },
  { icon: Gauge, title: 'Consistency cue', text: 'Agreement between original and flipped predictions helps flag unstable regions; it is not calibrated uncertainty.' },
  { icon: Layers, title: 'Review & export', text: 'Compare against the original radar view; export PNG, JSON and an extent/CRS-preserving GeoTIFF preview.' },
]

export function MethodSection() {
  return (
    <>
      <section className="method-section" id="method" aria-labelledby="method-title">
        <div className="container">
          <div className="section-title">
            <span className="eyebrow">HOW IT WORKS</span>
            <h2 id="method-title">A transparent pipeline, not a magic photograph.</h2>
            <p>Every stage is visible. The model is a small supervised encoder–decoder, chosen for stability and CPU inference over a flashy but unstable GAN.</p>
          </div>
          <div className="pipeline-grid">
            {PIPELINE.map(({ icon: Icon, title, text }, i) => (
              <article className="pipeline-card" key={title}>
                <span className="pipeline-number">0{i + 1}</span>
                <span className="pipeline-icon"><Icon size={20} /></span>
                <h3>{title}</h3>
                <p>{text}</p>
                {i < PIPELINE.length - 1 && <ArrowRight className="pipeline-arrow" size={16} aria-hidden="true" />}
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="limits-section" id="limits" aria-labelledby="limits-title">
        <div className="container limits-grid">
          <div>
            <span className="eyebrow">RESPONSIBLE USE</span>
            <h2 id="limits-title">What Vyora is — and what it is not.</h2>
            <p className="lead">Colours are an <strong>estimated geographic interpretation</strong>. They are not restored true colour, and this tool is not an official map or disaster-warning system.</p>
          </div>
          <div className="limit-list">
            <div><ShieldAlert size={19} /><div><strong>No ground truth claims</strong><span>Visual plausibility is not geographic accuracy. Always verify with authoritative imagery and local knowledge.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Synthetic demo scenes</strong><span>Bundled scenes are procedurally generated illustrations, not real satellite captures or georeferenced products.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Confidence has a narrow meaning</strong><span>It reflects consistency of the interpretation method, not certainty about the real world.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Domain shift is real</strong><span>Sensor, polarisation, resolution and season all affect results. Arbitrary SAR products are not guaranteed to work.</span></div></div>
          </div>
        </div>
      </section>
    </>
  )
}
