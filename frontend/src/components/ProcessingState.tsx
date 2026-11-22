import { LoaderCircle } from 'lucide-react'
import { useEffect, useState } from 'react'

const STEPS = [
  'Validating image format and size',
  'Normalising backscatter and reducing speckle',
  'Producing the colour interpretation',
  'Estimating confidence and feature shares',
]

export function ProcessingState({ sourceName }: { sourceName: string }) {
  const [active, setActive] = useState(0)
  useEffect(() => {
    const timer = window.setInterval(() => setActive((v) => Math.min(v + 1, STEPS.length - 1)), 700)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <div className="processing-card" role="status" aria-live="polite">
      <div className="radar-spinner" aria-hidden="true"><span /><span /><span /><LoaderCircle size={22} /></div>
      <h3>Interpreting scene</h3>
      <p>Working locally on the laptop server — nothing is sent to a paid or external service.</p>
      <div className="processing-source">{sourceName}</div>
      <ol className="processing-steps">
        {STEPS.map((step, index) => (
          <li key={step} className={index < active ? 'done' : index === active ? 'current' : ''}>
            <span className="step-dot" aria-hidden="true" />{step}
          </li>
        ))}
      </ol>
      <small>Step list shows server stages; it is not a measured progress percentage.</small>
    </div>
  )
}
