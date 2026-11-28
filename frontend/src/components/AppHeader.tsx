import { Activity, ArrowRight, BookOpen, LayoutDashboard, LogOut, Menu, Radar, X } from 'lucide-react'
import { useState } from 'react'

type Page = 'overview' | 'analyse' | 'scenes' | 'method'

interface Props {
  signedIn: boolean
  access?: boolean
  activePage?: Page
  onNavigate?: (page: Page) => void
  onEnter?: () => void
  onBack?: () => void
  onSignOut?: () => void
}

const navigation: { id: Page; label: string; icon: typeof LayoutDashboard }[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'analyse', label: 'Analyse', icon: Radar },
  { id: 'scenes', label: 'Scenes', icon: BookOpen },
  { id: 'method', label: 'Method', icon: Activity },
]

export function AppHeader({ signedIn, access = false, activePage, onNavigate, onEnter, onBack, onSignOut }: Props) {
  const [menuOpen, setMenuOpen] = useState(false)
  return (
    <header className={`app-header ${!signedIn && !access ? 'landing-header' : ''}`}>
      <div className="app-header-inner">
        <a className="wordmark" href={signedIn ? '#overview' : '#home'} onClick={(event) => {
          if (signedIn) { event.preventDefault(); onNavigate?.('overview') }
        }} aria-label="Vyora home">
          <img className="wordmark-image" src="/assets/vyora-brand.png" alt="Vyora" />
        </a>

        {signedIn ? (
          <>
            <nav className={`workspace-nav ${menuOpen ? 'open' : ''}`} aria-label="Workspace navigation">
              {navigation.map(({ id, label, icon: Icon }) => <button
                key={id}
                className={activePage === id ? 'active' : ''}
                onClick={() => { onNavigate?.(id); setMenuOpen(false) }}
                aria-current={activePage === id ? 'page' : undefined}
              ><Icon size={15} /><span>{label}</span></button>)}
            </nav>
            <div className="header-actions">
              <span className="local-session"><i /> Local demo</span>
              <div className="profile-control">
                <span className="profile-avatar" aria-hidden="true">DA</span>
                <span className="profile-label"><strong>Demo analyst</strong><small>Local session</small></span>
                <button className="signout-button" onClick={onSignOut} aria-label="Exit demo workspace"><LogOut size={15} /><span>Exit</span></button>
              </div>
              <button className="mobile-menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label={menuOpen ? 'Close navigation' : 'Open navigation'}>
                {menuOpen ? <X size={19} /> : <Menu size={19} />}
              </button>
            </div>
          </>
        ) : access ? (
          <button className="header-enter" onClick={onBack}>Back to Vyora</button>
        ) : (
          <>
            <nav className="public-nav" aria-label="Main navigation">
              <a className="landing-nav-active" href="#home">Home</a><a href="#scene-library">Scenes</a><a href="#workflow">Workflow</a><a href="#limits">Method</a>
            </nav>
            <button className="header-enter" onClick={onEnter}>Enter workspace <ArrowRight size={15} /></button>
          </>
        )}
      </div>
    </header>
  )
}
