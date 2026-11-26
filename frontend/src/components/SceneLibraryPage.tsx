import { ArrowRight, CircleAlert } from 'lucide-react'
import type { DemoScene } from '../types'

interface Props {
  scenes: DemoScene[]
  onAnalyse: (sceneId: string) => void
}

export function SceneLibraryPage({ scenes, onAnalyse }: Props) {
  return (
    <main className="workspace-page scene-library-page">
      <div className="page-title-row">
        <div><span className="section-kicker">SCENE LIBRARY</span><h1>Choose a scene to inspect.</h1><p>Examples are bundled for interface testing. Review each scene’s data note before interpreting its output.</p></div>
        <span className="count-chip">{scenes.length} scenes</span>
      </div>
      {scenes.length ? <div className="scene-library-grid">{scenes.map((scene, index) => <article className="library-scene-card" key={scene.id}>
        <div className="library-image"><img src={scene.image_url} alt={`${scene.name} demonstration preview`} loading="lazy" /><span className="scene-index">0{index + 1}</span><span className="synthetic-label">SYNTHETIC PREVIEW</span></div>
        <div className="library-scene-body"><span className="card-eyebrow">{scene.scene_type}</span><h2>{scene.name}</h2><p>{scene.description}</p><div className="scene-region">{scene.region_label}</div><div className="scene-data-note"><CircleAlert size={14} /><span>{scene.data_note}</span></div><button className="button-secondary" onClick={() => onAnalyse(scene.id)}>Open in analysis <ArrowRight size={14} /></button></div>
      </article>)}</div> : <div className="data-card empty-scenes"><h2>No scenes available</h2><p>Check that the local API is running and the demo manifest is present.</p></div>}
    </main>
  )
}
