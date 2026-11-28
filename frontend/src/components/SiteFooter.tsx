import { ArrowUpRight, BookOpen, Layers3, Radar } from 'lucide-react'
import { NASA_EYES_URL } from '../externalLinks'

type Page = 'overview' | 'analyse' | 'scenes' | 'method'

interface Props {
  runnerLabel: string
  workspace?: boolean
  onNavigate?: (page: Page) => void
}

const GOES_LOOP_URL = 'https://www.star.nesdis.noaa.gov/goes/fulldisk_band.php?sat=G19&band=GEOCOLOR&length=12'

export function SiteFooter({ runnerLabel, workspace = false, onNavigate }: Props) {
  return (
    <footer className={`site-footer ${workspace ? 'workspace-site-footer' : ''}`}>
      <div className="site-footer-main">
        <div className="footer-about">
          <a className="footer-brand" href={workspace ? '#overview' : '#home'} onClick={workspace ? () => onNavigate?.('overview') : undefined} aria-label="Vyora home">
            <img src="/assets/vyora-brand.png" alt="Vyora" />
          </a>
          <p>Local-first image review. Keep the source visible and the limits clear.</p>
          <span className="footer-scope">Research prototype · Not a warning product</span>
        </div>

        <nav className="footer-nav" aria-label="Footer navigation">
          <h2>Explore</h2>
          {workspace ? <>
            <button onClick={() => onNavigate?.('overview')}><Layers3 size={14} /> Overview</button>
            <button onClick={() => onNavigate?.('analyse')}><Radar size={14} /> Analyse</button>
            <button onClick={() => onNavigate?.('scenes')}><BookOpen size={14} /> Scenes</button>
            <button onClick={() => onNavigate?.('method')}><BookOpen size={14} /> Method & limits</button>
          </> : <>
            <a href="#workflow">Workflow</a>
            <a href="#scene-library">Example scenes</a>
            <a href="#limits">Scope & limitations</a>
          </>}
        </nav>

        <div className="footer-references">
          <h2>External Earth references</h2>
          <a href={NASA_EYES_URL} target="_blank" rel="noreferrer">NASA Eyes · 3D satellite tracker <ArrowUpRight size={14} /></a>
          <p>Official external view of Earth-observing satellites; not connected to Vyora runs.</p>
          <a href={GOES_LOOP_URL} target="_blank" rel="noreferrer">GOES full-disk animation · NOAA <ArrowUpRight size={14} /></a>
          <p>Real satellite imagery loop. Opens outside this local app.</p>
        </div>
      </div>
      <div className="site-footer-bottom">
        <span>VYORA · LOCAL RESEARCH DEMO</span>
        <span>Runner: {runnerLabel}</span>
        <span>Not ground truth · Not an official map</span>
      </div>
    </footer>
  )
}
