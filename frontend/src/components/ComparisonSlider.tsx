import { MoveHorizontal } from 'lucide-react'
import { useRef } from 'react'

interface Props {
  inputUrl: string
  colourUrl: string
  confidenceUrl: string
  showConfidence: boolean
  position: number
  onPosition: (value: number) => void
  inputLabel?: string
  outputLabel?: string
}

export function ComparisonSlider({
  inputUrl, colourUrl, confidenceUrl, showConfidence, position, onPosition,
  inputLabel = 'VV/VH INPUT', outputLabel = 'INTERPRETATION',
}: Props) {
  const container = useRef<HTMLDivElement>(null)
  const dragging = useRef(false)

  function update(clientX: number) {
    const rect = container.current?.getBoundingClientRect()
    if (!rect) return
    const value = ((clientX - rect.left) / rect.width) * 100
    onPosition(Math.max(1, Math.min(99, value)))
  }

  return (
    <div
      ref={container}
      className="compare"
      role="slider"
      tabIndex={0}
      aria-label={`Comparison: ${inputLabel} on the left, ${outputLabel} on the right`}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.round(position)}
      onPointerDown={(e) => { dragging.current = true; e.currentTarget.setPointerCapture(e.pointerId); update(e.clientX) }}
      onPointerMove={(e) => { if (dragging.current) update(e.clientX) }}
      onPointerUp={() => { dragging.current = false }}
      onPointerCancel={() => { dragging.current = false }}
      onKeyDown={(e) => {
        if (e.key === 'ArrowLeft') { e.preventDefault(); onPosition(Math.max(1, position - 4)) }
        if (e.key === 'ArrowRight') { e.preventDefault(); onPosition(Math.min(99, position + 4)) }
      }}
    >
      <img className="compare-img" src={colourUrl} alt="Estimated colour geographic interpretation" />
      {showConfidence && (
        <img
          className="compare-img compare-confidence"
          src={confidenceUrl}
          alt="Prediction consistency overlay, not calibrated uncertainty"
          style={{ clipPath: `inset(0 0 0 ${position}%)` }}
        />
      )}
      <img
        className="compare-img"
        src={inputUrl}
        alt={inputLabel === 'A-SIDE PNG' ? 'Uploaded grayscale A-side PNG tile' : 'VV/VH radar diagnostic composite (synthetic grayscale for demo scenes)'}
        style={{ clipPath: `inset(0 ${100 - position}% 0 0)` }}
      />
      <div className="compare-divider" style={{ left: `${position}%` }} aria-hidden="true">
        <span className="compare-handle"><MoveHorizontal size={19} /></span>
      </div>
      <span className="compare-label left">{inputLabel}</span>
      <span className="compare-label right">{showConfidence ? 'CONSISTENCY' : outputLabel}</span>
    </div>
  )
}
