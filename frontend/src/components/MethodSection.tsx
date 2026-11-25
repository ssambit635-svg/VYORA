import { ArrowRight, Binary, Gauge, Layers, ScanLine, ShieldAlert } from 'lucide-react'

const PNG_PIPELINE = [
  { icon: ScanLine, title: 'Paired PNG input', text: 'The supplied A-side grayscale tile is read as one channel and duplicated to fit this prototype model.' },
  { icon: Binary, title: 'ResU-Net model', text: 'A compact supervised encoder–decoder predicts RGB-style pixels from the grayscale A-side tile.' },
  { icon: Gauge, title: 'Consistency cue', text: 'Original-versus-flipped prediction agreement is shown as a stability cue, not calibrated uncertainty.' },
  { icon: Layers, title: 'Review & export', text: 'Compare the input and estimate with the slider; export the 256×256 PNG and JSON summary.' },
]

const GEOTIFF_PIPELINE = [
  { icon: ScanLine, title: 'Dual-pol input', text: 'A calibrated, co-registered Sentinel-1 GeoTIFF supplies VV and VH bands; each is robustly normalized and tiled.' },
  { icon: Binary, title: 'U-Net generator', text: 'A compact two-channel ResU-Net maps VV/VH to a three-channel Sentinel-2-style visual target when a trained checkpoint is available.' },
  { icon: Gauge, title: 'Consistency cue', text: 'Agreement between original and flipped predictions helps flag unstable regions; it is not calibrated uncertainty.' },
  { icon: Layers, title: 'Review & export', text: 'Compare against the original radar view; export PNG, JSON and an extent/CRS-preserving GeoTIFF preview.' },
]

export function MethodSection({ pngPrototype = false }: { pngPrototype?: boolean }) {
  const pipeline = pngPrototype ? PNG_PIPELINE : GEOTIFF_PIPELINE
  return (
    <>
      <section className="method-section" id="method" aria-labelledby="method-title">
        <div className="container">
          <div className="section-title">
            <span className="eyebrow">HOW IT WORKS</span>
            <h2 id="method-title">A transparent pipeline, not a magic photograph.</h2>
            <p>{pngPrototype
              ? 'This quick prototype uses the supplied paired A/B PNG folders. Its grayscale input and PNG targets are not equivalent to calibrated VV/VH rasters.'
              : 'Every stage is visible. The model is a small supervised encoder–decoder, chosen for stability and CPU inference over a flashy but unstable GAN.'}</p>
          </div>
          <div className="pipeline-grid">
            {pipeline.map(({ icon: Icon, title, text }, i) => (
              <article className="pipeline-card" key={title}>
                <span className="pipeline-number">0{i + 1}</span>
                <span className="pipeline-icon"><Icon size={20} /></span>
                <h3>{title}</h3>
                <p>{text}</p>
                {i < pipeline.length - 1 && <ArrowRight className="pipeline-arrow" size={16} aria-hidden="true" />}
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
            <p className="lead">Colours are an <strong>estimated visual interpretation</strong>. They are not restored true colour, and this tool is not an official map or disaster-warning system.</p>
          </div>
          <div className="limit-list">
            <div><ShieldAlert size={19} /><div><strong>No ground-truth claims</strong><span>Visual similarity is not geographic accuracy. Always verify with authoritative imagery and local knowledge.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>{pngPrototype ? 'PNG prototype limits' : 'Synthetic demo scenes'}</strong><span>{pngPrototype
              ? 'The current checkpoint uses grayscale A-side PNG tiles duplicated into two input channels; the input PNG has no map coordinates.'
              : 'Bundled scenes are procedurally generated illustrations, not real satellite captures or georeferenced products.'}</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Consistency is not confidence</strong><span>Agreement under a flip measures method stability, not certainty about the real world.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Domain shift is real</strong><span>Sensor, polarisation, resolution and season all affect results. Arbitrary satellite images are not guaranteed to work.</span></div></div>
          </div>
        </div>
      </section>
    </>
  )
}
