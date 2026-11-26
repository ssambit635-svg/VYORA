import { ArrowRight, Binary, Gauge, Layers, ScanLine, ShieldAlert } from 'lucide-react'
import type { Health } from '../types'

interface Props {
  health: Health | null
}

export function MethodSection({ health }: Props) {
  const isModel = health?.is_ai_inference ?? false
  const isPngPrototype = health?.input_representation.startsWith('grayscale_') ?? false
  const pipeline = [
    {
      icon: ScanLine,
      title: isPngPrototype ? 'Paired PNG input' : isModel ? 'SAR input contract' : 'Demo scene input',
      text: isPngPrototype
        ? 'A grayscale PNG is duplicated into two model channels. It is not separate VV/VH.'
        : isModel
          ? health?.accepted_model_input ?? 'Input representation is reported by the API.'
          : 'Bundled scenes are synthetic interface examples; this mode does not use a trained model.',
    },
    {
      icon: Binary,
      title: isModel ? 'Checkpoint inference' : 'Development renderer',
      text: isModel
        ? `The local checkpoint reports version ${health?.model_version ?? 'unknown'}. The output is an image estimate, not ground truth.`
        : 'The API reports development mode. Do not describe this run as trained-model inference.',
    },
    {
      icon: Gauge,
      title: 'Consistency cue',
      text: 'Original-versus-flipped prediction agreement is a stability measure, not calibrated uncertainty or a hazard probability.',
    },
    {
      icon: Layers,
      title: 'Review & export',
      text: 'Compare views, inspect a selected image region, add a human-authored note and export result files.',
    },
  ]
  return (
    <>
      <section className="method-section" id="method" aria-labelledby="method-title">
        <div className="container">
          <div className="section-title">
            <span className="eyebrow">HOW IT WORKS</span>
            <h2 id="method-title">A transparent pipeline, not a magic photograph.</h2>
            <p>Each stage is labelled from the API state. Image estimates and consistency cues are not geographic verification or official warning products.</p>
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
            <h2>What Vyora is — and what it is not.</h2>
            <p className="lead">The current result is an <strong>estimated image interpretation</strong>. It is not restored true colour, a validated flood map, a cyclone forecast, or an official warning.</p>
          </div>
          <div className="limit-list">
            <div><ShieldAlert size={19} /><div><strong>Not a hazard detector</strong><span>No flood, cyclone, water, vegetation, building or land-cover detection head is established by this colorization workflow.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Input provenance matters</strong><span>Bundled examples are synthetic. A grayscale PNG is not labelled as distinct VV/VH; image coordinates are not geographic coordinates.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Consistency is not confidence</strong><span>Agreement under a flip measures prediction stability, not certainty about the real world.</span></div></div>
            <div><ShieldAlert size={19} /><div><strong>Human notes are annotations</strong><span>Review notes are user-authored and require independent verification before becoming training labels.</span></div></div>
          </div>
        </div>
      </section>
    </>
  )
}
