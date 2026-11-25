import { ArrowDown, CircleAlert, Cpu, Radio, Sparkles, Wifi } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { fetchHealth, fetchScenes, runInference } from './api/client'
import { Header } from './components/Header'
import { MethodSection } from './components/MethodSection'
import { ProcessingState } from './components/ProcessingState'
import { ResultWorkspace } from './components/ResultWorkspace'
import { ScenePicker } from './components/ScenePicker'
import { UploadDropzone } from './components/UploadDropzone'
import type { DemoScene, Health, InferenceResult } from './types'

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [scenes, setScenes] = useState<DemoScene[]>([])
  const [selectedScene, setSelectedScene] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<InferenceResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const resultsRef = useRef<HTMLDivElement>(null)
  const pngPrototype = health?.model_version.includes('paired-png-prototype') ?? false

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setError('Cannot reach the local API. Start the backend before running a scene.'))
    fetchScenes().then((items) => {
      setScenes(items)
      setSelectedScene((current) => current ?? items[0]?.id ?? null)
    }).catch(() => setError('Demo scenes could not be loaded.'))
  }, [])

  async function interpret() {
    if (!file && !selectedScene) {
      setError('Choose a demo scene or upload a SAR image first.')
      return
    }
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const response = await runInference(file ? { file } : { sceneId: selectedScene! })
      setResult(response)
      window.setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Inference failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div id="top" className="app-shell">
      <Header health={health} />
      <main>
        <section className="hero">
          <div className="hero-glow" aria-hidden="true" />
          <div className="container hero-inner">
            <div className="hero-copy">
              <span className="hero-eyebrow"><Radio size={14} /> HK26-PS-19 · SAR IMAGE COLORIZATION</span>
              <h1>See the shape of<br /><span>what radar sees.</span></h1>
              <p>{pngPrototype
                ? 'This prototype learns from paired A/B PNG tiles. It accepts a grayscale tile and estimates pixels from its paired side; the input is not separate VV/VH channels.'
                : 'Vyora maps paired VV/VH backscatter to an estimated optical-style view, while keeping the measured radar evidence visible.'}</p>
              <div className="hero-actions">
                <a className="primary-btn" href="#workspace">Try a demo scene <ArrowDown size={16} /></a>
                <a className="text-btn" href="#method">How the model works</a>
              </div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="orb">
                <div className="orb-ring one" /><div className="orb-ring two" /><div className="orb-ring three" />
                <div className="orb-core"><Sparkles size={30} /></div>
              </div>
              <div className="visual-chip chip-one"><span />RAW BACKSCATTER</div>
              <div className="visual-chip chip-two"><span />{pngPrototype ? 'PNG PROTOTYPE' : 'FLIP CONSISTENCY'}</div>
            </div>
          </div>
          <div className="container trust-row">
            <span><Wifi size={15} /> Runs locally on a laptop</span>
            <span><Cpu size={15} /> CPU-friendly compact model</span>
            <span><Sparkles size={15} /> No paid APIs or subscriptions</span>
            <span><CircleAlert size={15} /> {pngPrototype ? 'Prototype output, not ground truth' : 'Estimate, not ground truth'}</span>
          </div>
        </section>

        <section className="workspace container" id="workspace">
          <div className="section-title compact">
            <span className="eyebrow">INTERPRETATION WORKSPACE</span>
            <h2>Choose a scene, then look closer.</h2>
            <p>{pngPrototype
              ? 'Use the grayscale PNG side from the paired dataset. The bundled demo scenes are synthetic and are not training examples.'
              : 'Four synthetic preview scenes keep the demo reliable. For geospatial inference, upload a calibrated, co-registered two-band GeoTIFF with VV first and VH second.'}</p>
          </div>

          <div className="workspace-grid">
            <div className="input-column">
              {!pngPrototype && <>
                <ScenePicker scenes={scenes} selectedId={file ? null : selectedScene} onSelect={(id) => { setFile(null); setSelectedScene(id); setError('') }} disabled={loading} />
                <div className="or-divider"><span>OR</span></div>
              </>}
              <UploadDropzone file={file} onFile={(f) => { setFile(f); if (f) setError('') }} onError={setError} disabled={loading} pngPrototype={pngPrototype} />
              {error && <div className="error-box" role="alert"><CircleAlert size={17} /><span>{error}</span></div>}
              <button className="primary-btn interpret-btn" onClick={interpret} disabled={loading || (!file && !selectedScene)}>
                {loading ? 'Interpreting…' : 'Interpret scene'} <ArrowDown size={16} />
              </button>
              <p className="consent-note">By running a scene you acknowledge the output is an AI-estimated / rule-based interpretation, not an official map or warning product.</p>
            </div>

            <div className="output-column" ref={resultsRef}>
              {loading ? <ProcessingState sourceName={file?.name ?? scenes.find((s) => s.id === selectedScene)?.name ?? 'Selected scene'} /> : result ? (
                <ResultWorkspace result={result} onReset={() => { setResult(null); setFile(null) }} />
              ) : (
                <div className="empty-state panel">
                  <div className="empty-visual" aria-hidden="true"><span /><span /><span /></div>
                  <h3>Your result will appear here</h3>
                  <p>{pngPrototype
                    ? 'Compare the grayscale PNG input with the model estimate. This prototype does not provide calibrated uncertainty, land-cover classes, or map coordinates.'
                    : 'Compare the VV/VH radar composite with the estimated interpretation, inspect flip-view consistency, and export PNG, JSON or a GeoTIFF preview.'}</p>
                  <div className="empty-pills"><span>Before / after slider</span><span>Consistency cue</span><span>Prototype limits</span><span>PNG + JSON export</span></div>
                </div>
              )}
            </div>
          </div>
        </section>

        <MethodSection pngPrototype={pngPrototype} />
      </main>
      <footer className="site-footer">
        <div className="container footer-inner">
          <div><strong>VYORA<span className="brand-dot">.</span></strong><span>Confidence-aware SAR interpretation demonstrator · HK26-PS-19</span></div>
          <span>Local-first · Open source · Decision support only</span>
        </div>
      </footer>
    </div>
  )
}
