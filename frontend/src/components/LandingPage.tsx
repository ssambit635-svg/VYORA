import '@fontsource/inter/latin-400.css'
import '@fontsource/inter/latin-500.css'
import '@fontsource/inter/latin-600.css'
import '@fontsource/space-grotesk/latin-500.css'
import '@fontsource/space-grotesk/latin-600.css'
import { ArrowDown, ArrowRight, ArrowUpRight, Check, Eye, Layers3, Radar, ShieldAlert } from 'lucide-react'
import { lazy, Suspense, useEffect, useRef } from 'react'
import type { DemoScene, Health } from '../types'
import { NASA_EYES_URL } from '../externalLinks'
import { SiteFooter } from './SiteFooter'

const InteractiveEarth = lazy(() => import('./InteractiveEarth').then((module) => ({ default: module.InteractiveEarth })))

interface Props {
  sceneCount: number
  scenes: DemoScene[]
  health: Health | null
  onEnter: () => void
  onMethod: () => void
}

export function LandingPage({ sceneCount, scenes, health, onEnter, onMethod }: Props) {
  const journeyRef = useRef<HTMLElement>(null)
  const carouselRef = useRef<HTMLElement>(null)
  const satelliteLabel = health?.is_ai_inference ? 'Checkpoint inference' : health ? 'Development runner' : 'API status unavailable'

  useEffect(() => {
    const updateDepth = () => {
      const stage = journeyRef.current
      if (stage) {
        const rect = stage.getBoundingClientRect()
        const headerHeight = document.querySelector('.landing-header')?.getBoundingClientRect().height ?? 0
        const travel = Math.max(1, rect.height - window.innerHeight + headerHeight)
        const progress = Math.max(0, Math.min(1, (headerHeight - rect.top) / travel))
        stage.style.setProperty('--journey-progress', progress.toFixed(3))
        stage.style.setProperty('--journey-shift', `${-window.innerWidth * .08 * progress}px`)
        stage.style.setProperty('--journey-shift-mobile', `${-window.innerWidth * .04 * progress}px`)
        stage.style.setProperty('--surface-shift', `${-36 * progress}px`)
        stage.style.setProperty('--orbit-shift', `${27 * progress}px`)
      }
      const carousel = carouselRef.current
      if (carousel) {
        const rect = carousel.getBoundingClientRect()
        const progress = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / Math.max(1, rect.height + window.innerHeight)))
        carousel.style.setProperty('--carousel-progress', progress.toFixed(3))
        carousel.style.setProperty('--carousel-shift', `${-window.innerWidth * .04 * progress}px`)
      }
    }
    updateDepth()
    window.addEventListener('scroll', updateDepth, { passive: true })
    window.addEventListener('resize', updateDepth)
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add('is-visible'); revealObserver.unobserve(entry.target) }
      })
    }, { threshold: .25 })
    document.querySelectorAll('.manifesto-copy.reveal-lines').forEach((element) => revealObserver.observe(element))
    return () => { window.removeEventListener('scroll', updateDepth); window.removeEventListener('resize', updateDepth); revealObserver.disconnect() }
  }, [])

  return (
    <main className="public-page cinematic-landing" id="home">
      <section className="landing-journey" ref={journeyRef} aria-label="Earth observation for careful interpretation">
        <div className="journey-sticky">
          <div className="journey-gridlines" aria-hidden="true" />
          <div className="journey-copy reveal-lines">
            <span className="hero-overline"><i /> EARTH OBSERVATION · MADE REVIEWABLE</span>
            <h1><span>See the signal.</span><span>Understand the</span><span className="hero-accent">evidence.</span></h1>
            <p>Vyora brings source imagery, model estimates and human review into one clear workflow—without pretending an estimate is ground truth.</p>
            <div className="journey-actions">
              <button className="button-primary" onClick={onEnter}>Explore the workspace <ArrowRight size={16} /></button>
              <a href="#approach">Discover the approach <ArrowDown size={14} /></a>
            </div>
            <div className="journey-footnote"><span>01 / 04</span><i /> LOCAL-FIRST IMAGE REVIEW</div>
          </div>
          <div className="journey-earth-wrap" aria-label="Interactive Earth and spacecraft models">
            <div className="journey-orbit orbit-one" aria-hidden="true" /><div className="journey-orbit orbit-two" aria-hidden="true" />
            <div className="journey-earth">
              <Suspense fallback={<div className="landing-earth-loading">Preparing the Earth model…</div>}>
                <InteractiveEarth scrollStageRef={journeyRef} />
              </Suspense>
            </div>
            <div className="journey-coordinate journey-coordinate-top">EARTH / 01 <span>ILLUSTRATIVE ORBITS</span></div>
            <div className="journey-caption"><span className="caption-beacon" /> GOES + LANDSAT 8 · NASA 3D MODELS <small>Not a live tracking feed</small></div>
            <div className="journey-parallax-chip chip-surface"><Layers3 size={13} /> SOURCE IMAGERY</div>
            <div className="journey-parallax-chip chip-orbit"><Radar size={13} /> ORBITAL VIEW</div>
          </div>
          <div className="journey-scroll-indicator"><span>SCROLL TO EXPLORE</span><i /></div>
          <div className="journey-vignette" aria-hidden="true" />
        </div>
      </section>

      <section className="landing-manifesto" id="approach">
        <div className="manifesto-index">01 <i /> THE VYORA APPROACH</div>
        <div className="manifesto-copy reveal-lines"><h2><span>Good analysis starts</span><span>with what you can see.</span></h2><p>Every result stays close to its source. Inspect the input, compare the returned estimate, and leave a note where another person can pick up the thread.</p></div>
        <div className="manifesto-orbit-art" aria-hidden="true"><div className="manifesto-ring" /><span>V</span><i /><b /></div>
      </section>

      <section className="landing-scene-section" id="scene-library" ref={carouselRef}>
        <div className="scene-section-heading">
          <div><span className="section-kicker">A PLACE TO BEGIN</span><h2>Real review starts<br />with a closer look.</h2></div>
          <div className="scene-heading-note"><span>{String(sceneCount).padStart(2, '0')}</span><p>bundled example scenes<br />Synthetic previews, clearly labelled</p></div>
        </div>
        <div className="scene-carousel-window"><div className="scene-carousel-track">
          {scenes.slice(0, 6).map((scene, index) => <article className={`landing-scene-card card-arc-${index % 5}`} key={scene.id}>
            <div className="landing-scene-image"><img src={scene.image_url} alt="" loading="lazy" /><span>EXAMPLE · SYNTHETIC</span></div>
            <div className="landing-scene-meta"><span>SCENE {String(index + 1).padStart(2, '0')}</span><ArrowUpRight size={14} /></div>
            <h3>{scene.name}</h3><p>{scene.region_label || 'Bundled demonstration scene'}</p>
          </article>)}
          {scenes.length === 0 && <div className="scene-empty-note"><Layers3 size={17} /><span>Example scenes appear here when the API is available.</span></div>}
        </div></div>
        <div className="carousel-caption"><span><i /> SCENES ARE SYNTHETIC DEMONSTRATIONS</span><span>01 — {String(Math.max(1, scenes.length)).padStart(2, '0')}</span></div>
      </section>

      <section className="landing-workflow feature-workflow" id="workflow">
        <div className="workflow-heading"><span className="section-kicker">A TRACEABLE WORKFLOW</span><h2>From image to<br /><em>informed review.</em></h2><p>No black box hand-off. Each step keeps the inputs and the limits in view.</p><button className="landing-inline-link" onClick={onMethod}>Read the method & limits <ArrowRight size={14} /></button></div>
        <div className="workflow-steps">
          <article><span className="step-index">01</span><Layers3 /><small>INPUT</small><h3>Choose a scene</h3><p>Start with a bundled example or a supported local image.</p><i className="step-connector" /></article>
          <article><span className="step-index">02</span><Eye /><small>INTERPRET</small><h3>Compare the views</h3><p>Keep the source alongside the returned estimate.</p><i className="step-connector" /></article>
          <article><span className="step-index">03</span><Check /><small>REVIEW</small><h3>Leave a record</h3><p>Add an image-space note and export the review.</p></article>
        </div>
      </section>

      <section className="landing-trust" id="limits">
        <div className="trust-mark"><ShieldAlert size={20} /><span>HONEST BY DESIGN</span></div>
        <div className="trust-copy"><h2>Clarity includes<br /><em>knowing what it isn’t.</em></h2><p>Vyora is an image-interpretation demonstrator, not a flood or cyclone detector, official map, or warning service. Outputs are estimates, not ground truth. Always verify with authoritative sources and expert review.</p></div>
        <a className="trust-external" href={NASA_EYES_URL} target="_blank" rel="noreferrer"><span>Looking for actual satellite positions?</span><strong>Open NASA Eyes <ArrowUpRight size={14} /></strong></a>
      </section>

      <section className="landing-final-cta"><div><span className="section-kicker">YOUR REVIEW WORKSPACE</span><h2>Make room for<br />the evidence.</h2></div><button className="button-primary" onClick={onEnter}>Enter the workspace <ArrowRight size={16} /></button><span className="cta-status"><i /> {satelliteLabel}</span></section>
      <SiteFooter runnerLabel={health ? health.mode.toUpperCase() : 'API CHECKING'} />
    </main>
  )
}
