import { Download, Hand, Plus, ScanSearch } from 'lucide-react'
import { useMemo, useRef, useState } from 'react'
import type { InferenceResult } from '../types'

type View = 'input' | 'output' | 'consistency'
type Region = { x: number; y: number; width: number; height: number }
type ReviewNote = { id: string; region: Region; text: string; createdAt: string }

interface Props {
  result: InferenceResult
}

export function SARInspectionTools({ result }: Props) {
  const trueDualPol = result.input.distinct_channels === true
  const [channel, setChannel] = useState<'composite' | 'one' | 'two'>('composite')
  const [view, setView] = useState<View>('input')
  const [region, setRegion] = useState<Region | null>(null)
  const [selection, setSelection] = useState<{ x: number; y: number } | null>(null)
  const [notes, setNotes] = useState<ReviewNote[]>([])
  const [draft, setDraft] = useState('')
  const selectionSurface = useRef<HTMLDivElement>(null)
  const imageUrls: Record<View, string> = {
    input: result.urls.input,
    output: result.urls.colour,
    consistency: result.urls.confidence,
  }
  const stats = result.input.channel_stats ?? []
  const currentChannel = channel === 'one' ? 0 : 1
  const histogram = stats[currentChannel]?.histogram ?? []
  const histogramMaximum = Math.max(1, ...histogram)
  const zoomRegion = region ?? { x: 1 / 3, y: 1 / 3, width: 1 / 3, height: 1 / 3 }
  const imageCenter = useMemo(() => ({
    x: zoomRegion.x + zoomRegion.width / 2,
    y: zoomRegion.y + zoomRegion.height / 2,
  }), [zoomRegion.x, zoomRegion.y, zoomRegion.width, zoomRegion.height])
  const backgroundPosition = (center: number, fraction: number) => {
    const scale = 1 / Math.max(0.01, fraction)
    return scale <= 1.001 ? 50 : Math.max(0, Math.min(100, ((center * scale - 0.5) / (scale - 1)) * 100))
  }

  function pointerPosition(clientX: number, clientY: number) {
    const rect = selectionSurface.current?.getBoundingClientRect()
    if (!rect) return null
    return {
      x: Math.max(0, Math.min(1, (clientX - rect.left) / rect.width)),
      y: Math.max(0, Math.min(1, (clientY - rect.top) / rect.height)),
    }
  }

  function finishSelection(clientX: number, clientY: number) {
    if (!selection) return
    const end = pointerPosition(clientX, clientY)
    if (!end) return
    const x = Math.min(selection.x, end.x)
    const y = Math.min(selection.y, end.y)
    const width = Math.abs(end.x - selection.x)
    const height = Math.abs(end.y - selection.y)
    if (width > 0.008 && height > 0.008) setRegion({ x, y, width, height })
    setSelection(null)
  }

  function exportNotes() {
    const payload = {
      schema: 'vyora-human-review-notes/v1',
      result_id: result.result_id,
      created_at: new Date().toISOString(),
      notice: 'User-authored review annotations only. These are not model predictions, verified labels, or georeferenced polygons.',
      coordinate_system: 'normalized image coordinates [0,1], origin at top-left; not geographic coordinates',
      notes,
    }
    const blobUrl = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `vyora-review-${result.result_id.slice(0, 8)}.json`
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(blobUrl), 0)
  }

  return (
    <div className="inspection-tools">
      <section className="panel inspection-panel" aria-labelledby="channel-lens-title">
        <div className="tool-heading">
          <div><span className="step-tag">DIAGNOSTICS</span><h3 id="channel-lens-title">SAR Channel Lens</h3></div>
          <span className={`availability-pill ${trueDualPol ? 'available' : ''}`}>{trueDualPol ? 'VV + VH present' : 'No verified VV/VH pair'}</span>
        </div>
        <p className="tool-copy">Inspect source channels separately or view the diagnostic composite. Composite colors are a visualization convention, not optical RGB.</p>
        <div className="lens-tabs" role="group" aria-label="SAR channel view">
          <button className={channel === 'composite' ? 'selected' : ''} onClick={() => setChannel('composite')}>{trueDualPol ? 'VV / VH composite' : 'Input preview'}</button>
          <button className={channel === 'one' ? 'selected' : ''} onClick={() => setChannel('one')}>{trueDualPol ? 'VV' : 'Channel 1'}</button>
          <button className={channel === 'two' ? 'selected' : ''} onClick={() => setChannel('two')}>{trueDualPol ? 'VH' : 'Channel 2'}</button>
        </div>
        <div className="lens-content">
          <div className="lens-image-wrap">
            <img src={channel === 'composite' ? result.urls.input : (channel === 'one' ? result.urls.channel_1 : result.urls.channel_2)} alt={channel === 'composite' ? (trueDualPol ? 'SAR diagnostic composite: red is VV, green is VH, blue is their mean' : 'Input preview; separate polarization channels are not verified') : `${trueDualPol ? (channel === 'one' ? 'VV polarization' : 'VH polarization') : (channel === 'one' ? 'Model channel one' : 'Model channel two')} grayscale preview`} />
          </div>
          <div className="lens-stats">
            <strong>{channel === 'composite' ? (trueDualPol ? 'Composite key' : 'Input provenance') : (stats[currentChannel]?.label ?? `Channel ${currentChannel + 1}`)}</strong>
            <p>{channel === 'composite'
              ? trueDualPol ? 'R = VV · G = VH · B = mean(VV,VH)' : 'This input is not confirmed as two distinct polarizations. The grayscale PNG path duplicates its intensity across model channels.'
              : `Normalized intensity distribution for ${stats[currentChannel]?.label ?? 'this channel'}.`}</p>
            {channel !== 'composite' && stats[currentChannel] && <>
              <div className="stat-pairs"><span>Mean <b>{stats[currentChannel].mean.toFixed(3)}</b></span><span>2nd–98th pct <b>{stats[currentChannel].p02.toFixed(3)}–{stats[currentChannel].p98.toFixed(3)}</b></span></div>
              <div className="histogram" role="img" aria-label={`16-bin intensity histogram for ${stats[currentChannel].label}`}>
                {histogram.map((count, index) => <i key={index} title={`Bin ${index + 1}: ${count}`} style={{ height: `${Math.max(3, count / histogramMaximum * 100)}%` }} />)}
              </div>
              <small>16-bin normalized intensity histogram</small>
            </>}
          </div>
        </div>
      </section>

      <section className="panel inspection-panel" aria-labelledby="region-compare-title">
        <div className="tool-heading">
          <div><span className="step-tag">LOCAL INSPECTION</span><h3 id="region-compare-title">Region Zoom Compare</h3></div>
          <ScanSearch size={18} aria-hidden="true" />
        </div>
        <p className="tool-copy">Drag on the image to mark a region. The same normalized crop is shown across input, output and consistency views. Visual comparison only—not geographic validation.</p>
        <div className="view-tabs" role="group" aria-label="Image to select comparison region">
          {(['input', 'output', 'consistency'] as View[]).map((item) => <button key={item} className={view === item ? 'selected' : ''} onClick={() => setView(item)}>{item === 'input' ? 'Input' : item === 'output' ? 'Output' : 'Consistency'}</button>)}
        </div>
        <div
          ref={selectionSurface}
          className="region-selector"
          onPointerDown={(event) => { const point = pointerPosition(event.clientX, event.clientY); if (point) { event.currentTarget.setPointerCapture(event.pointerId); setSelection(point) } }}
          onPointerUp={(event) => finishSelection(event.clientX, event.clientY)}
          onPointerCancel={() => setSelection(null)}
          onPointerMove={(event) => {
            if (!selection || !selectionSurface.current) return
            const point = pointerPosition(event.clientX, event.clientY)
            if (!point) return
            const left = Math.min(selection.x, point.x)
            const top = Math.min(selection.y, point.y)
            const width = Math.abs(point.x - selection.x)
            const height = Math.abs(point.y - selection.y)
            const box = selectionSurface.current.querySelector<HTMLElement>('.region-selection.drawing')
            if (box) Object.assign(box.style, { left: `${left * 100}%`, top: `${top * 100}%`, width: `${width * 100}%`, height: `${height * 100}%` })
          }}
          role="application"
          aria-label="Drag to mark a region for zoom comparison"
        >
          <img src={imageUrls[view]} alt={`${view} view; drag to select a region`} draggable={false} />
          {region && <span className="region-selection" style={{ left: `${region.x * 100}%`, top: `${region.y * 100}%`, width: `${region.width * 100}%`, height: `${region.height * 100}%` }} />}
          {selection && <span className="region-selection drawing" />}
          {!region && !selection && <span className="selection-hint"><Hand size={14} /> Drag to mark area</span>}
        </div>
        <div className="zoom-compare-grid">
          {(['input', 'output', 'consistency'] as View[]).map((item) => <div className="zoom-card" key={item}>
            <div className="zoom-image" style={{ backgroundImage: `url("${imageUrls[item]}")`, backgroundSize: `${100 / zoomRegion.width}% ${100 / zoomRegion.height}%`, backgroundPosition: `${backgroundPosition(imageCenter.x, zoomRegion.width)}% ${backgroundPosition(imageCenter.y, zoomRegion.height)}%` }} aria-label={`Zoomed ${item} region`} role="img" />
            <strong>{item === 'input' ? 'Input' : item === 'output' ? 'Output' : 'Consistency'}</strong>
          </div>)}
        </div>
        <p className="coordinate-note">{region ? `Selected image region: x ${region.x.toFixed(2)}, y ${region.y.toFixed(2)}, w ${region.width.toFixed(2)}, h ${region.height.toFixed(2)} (normalized).` : 'No region selected; zoom previews show the tile center.'}</p>
      </section>

      <section className="panel inspection-panel" aria-labelledby="review-notes-title">
        <div className="tool-heading">
          <div><span className="step-tag">HUMAN REVIEW</span><h3 id="review-notes-title">Review Notes</h3></div>
          <button className="export-notes" onClick={exportNotes} disabled={notes.length === 0}><Download size={14} /> Export JSON</button>
        </div>
        <p className="tool-copy">Notes are user annotations on normalized image regions, not model predictions or verified geographic labels. Mark a region above before adding a note.</p>
        <div className="note-entry">
          <input value={draft} onChange={(event) => setDraft(event.target.value)} maxLength={500} placeholder="Add an observation for the selected region…" aria-label="Human review note" />
          <button onClick={() => {
            const text = draft.trim()
            if (!text || !region) return
            setNotes((existing) => [...existing, { id: crypto.randomUUID(), region, text, createdAt: new Date().toISOString() }])
            setDraft('')
          }} disabled={!region || !draft.trim()}><Plus size={15} /> Add note</button>
        </div>
        {notes.length === 0 ? <p className="notes-empty">No review notes yet.</p> : <ul className="review-note-list">{notes.map((note) => <li key={note.id}><span>{note.text}</span><small>x {note.region.x.toFixed(2)} · y {note.region.y.toFixed(2)} · {note.createdAt.slice(0, 16).replace('T', ' ')}</small></li>)}</ul>}
      </section>
    </div>
  )
}
