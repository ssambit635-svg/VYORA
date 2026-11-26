import { ArrowRight, CircleAlert, Upload } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { fetchHealth, fetchScenes, runInference } from './api/client'
import { AppHeader } from './components/AppHeader'
import { DemoAccessPage } from './components/DemoAccessPage'
import { LandingPage } from './components/LandingPage'
import { MethodSection } from './components/MethodSection'
import { OverviewPage } from './components/OverviewPage'
import { ProcessingState } from './components/ProcessingState'
import { ResultWorkspace } from './components/ResultWorkspace'
import { SceneLibraryPage } from './components/SceneLibraryPage'
import { ScenePicker } from './components/ScenePicker'
import { UploadDropzone } from './components/UploadDropzone'
import type { DemoScene, Health, InferenceResult } from './types'

type WorkspacePage = 'overview' | 'analyse' | 'scenes' | 'method'
type Screen = 'landing' | 'access' | 'workspace'
const SESSION_KEY = 'vyora-local-demo-session'

export default function App() {
  const [screen, setScreen] = useState<Screen>(() => sessionStorage.getItem(SESSION_KEY) === 'active' ? 'workspace' : 'landing')
  const [page, setPage] = useState<WorkspacePage>('overview')
  const [health, setHealth] = useState<Health | null>(null)
  const [scenes, setScenes] = useState<DemoScene[]>([])
  const [selectedScene, setSelectedScene] = useState<string | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<InferenceResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const resultsRef = useRef<HTMLDivElement>(null)
  const pngPrototype = health?.input_representation.startsWith('grayscale_') ?? false

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setError('Cannot reach the local API. Start the backend before running a scene.'))
    fetchScenes().then((items) => {
      setScenes(items)
      setSelectedScene((current) => current ?? items[0]?.id ?? null)
    }).catch(() => setError('Demo scenes could not be loaded.'))
  }, [])

  function enterDemo() {
    sessionStorage.setItem(SESSION_KEY, 'active')
    setScreen('workspace')
    setPage('overview')
    setError('')
  }

  function exitDemo() {
    sessionStorage.removeItem(SESSION_KEY)
    setScreen('landing')
    setPage('overview')
    setResult(null)
    setFile(null)
    setError('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function chooseScene(sceneId: string) {
    setSelectedScene(sceneId)
    setFile(null)
    setError('')
    setPage('analyse')
  }

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

  function showWorkflow() {
    document.getElementById('workflow')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  return (
    <div className="app-shell">
      <AppHeader
        signedIn={screen === 'workspace'}
        access={screen === 'access'}
        activePage={page}
        onNavigate={setPage}
        onEnter={() => setScreen('access')}
        onBack={() => setScreen('landing')}
        onSignOut={exitDemo}
      />

      {screen === 'landing' && <LandingPage sceneCount={scenes.length} onEnter={() => setScreen('access')} onMethod={showWorkflow} />}
      {screen === 'access' && <DemoAccessPage onContinue={enterDemo} onBack={() => setScreen('landing')} />}
      {screen === 'workspace' && <>
        {page === 'overview' && <OverviewPage health={health} scenes={scenes} result={result} onNavigate={setPage} onChooseScene={chooseScene} />}
        {page === 'scenes' && <SceneLibraryPage scenes={scenes} onAnalyse={chooseScene} />}
        {page === 'method' && <div className="workspace-method"><div className="workspace-page method-intro"><span className="section-kicker">METHOD & LIMITS</span><h1>Every step stays inspectable.</h1><p>Read how this prototype handles inputs, consistency cues and the boundaries of its outputs.</p></div><MethodSection health={health} /></div>}
        {page === 'analyse' && <main className="workspace-page analysis-page">
          <div className="page-title-row analysis-title">
            <div><span className="section-kicker">ANALYSIS WORKSPACE</span><h1>Compare the signal with its estimate.</h1><p>Keep the source visible. Treat the output as an estimate, not ground truth or a hazard alert.</p></div>
            {health && <span className={`analysis-mode ${health.is_ai_inference ? 'model' : ''}`}>{health.is_ai_inference ? 'CHECKPOINT INFERENCE' : 'DEVELOPMENT MODE'}</span>}
          </div>
          <div className="analysis-grid">
            <div className="analysis-input-column">
              {!pngPrototype && <>
                <ScenePicker scenes={scenes} selectedId={file ? null : selectedScene} onSelect={(id) => { setFile(null); setSelectedScene(id); setError('') }} disabled={loading} />
                <div className="or-divider"><span>OR</span></div>
              </>}
              <UploadDropzone file={file} onFile={(selected) => { setFile(selected); if (selected) setError('') }} onError={setError} disabled={loading} pngPrototype={pngPrototype} />
              {error && <div className="error-box" role="alert"><CircleAlert size={17} /><span>{error}</span></div>}
              <button className="button-primary interpret-btn" onClick={interpret} disabled={loading || (!file && !selectedScene)}>
                {loading ? 'Interpreting…' : 'Interpret scene'} <ArrowRight size={16} />
              </button>
              <p className="form-note">Uploaded bytes are processed in memory. No map coordinates are inferred from a PNG.</p>
            </div>
            <div className="analysis-output-column" ref={resultsRef}>
              {loading ? <ProcessingState sourceName={file?.name ?? scenes.find((scene) => scene.id === selectedScene)?.name ?? 'Selected scene'} /> : result ? (
                <ResultWorkspace result={result} onReset={() => { setResult(null); setFile(null) }} />
              ) : <div className="analysis-empty data-card">
                <div className="empty-mark"><Upload size={20} /></div><span className="card-eyebrow">READY WHEN YOU ARE</span><h2>Your result will appear here.</h2><p>Choose a scene or upload a supported image, then run one interpretation. Results and measured values appear in this panel.</p>
                <div className="empty-hints"><span>Before / after</span><span>Consistency cue</span><span>PNG + JSON export</span></div>
              </div>}
            </div>
          </div>
        </main>}
      </>}

      {screen === 'workspace' && <footer className="workspace-footer"><span>VYORA<span className="wordmark-period">.</span></span><span>Local research prototype · Not an official map or warning product</span></footer>}
    </div>
  )
}
