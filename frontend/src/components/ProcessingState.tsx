import { LoaderCircle } from 'lucide-react'

export function ProcessingState({ sourceName }: { sourceName: string }) {
  return (
    <div className="processing-card" role="status" aria-live="polite">
      <span className="processing-indicator" aria-hidden="true"><LoaderCircle size={22} /></span>
      <h3>Running analysis</h3>
      <p>Waiting for the local API to finish this image run.</p>
      <div className="processing-source">{sourceName}</div>
      <small>The result view will show only values returned by the API.</small>
    </div>
  )
}
