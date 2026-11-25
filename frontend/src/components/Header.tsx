import { Activity, Menu, X } from 'lucide-react'
import { useState } from 'react'
import type { Health } from '../types'

export function Header({ health }: { health: Health | null }) {
  const [open, setOpen] = useState(false)
  const isModel = health?.is_ai_inference
  const isLegacyPng = health?.model_version.includes('paired-png-prototype-v0.1') ?? false
  return (
    <header className="site-header">
      <div className="container header-inner">
        <a className="brand" href="#top" aria-label="Vyora home">
          <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
          <span className="brand-name">VYORA<span className="brand-dot">.</span></span>
        </a>
        <nav className={open ? 'nav open' : 'nav'} aria-label="Main navigation">
          <a href="#workspace" onClick={() => setOpen(false)}>Workspace</a>
          <a href="#method" onClick={() => setOpen(false)}>Method</a>
          <a href="#limits" onClick={() => setOpen(false)}>Limitations</a>
        </nav>
        <div className="header-side">
          <span className={`mode-pill ${isModel ? 'model' : 'dev'}`} title={health?.runner_note}>
            <Activity size={13} strokeWidth={2.2} />
            {isModel
              ? isLegacyPng ? 'LEGACY PNG MODEL' : health?.model_version.includes('paired-png-prototype') ? 'PNG PROTOTYPE' : 'MODEL MODE'
              : 'DEVELOPMENT MODE'}
          </span>
          <button className="icon-btn menu-btn" onClick={() => setOpen(!open)} aria-label={open ? 'Close menu' : 'Open menu'}>
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>
    </header>
  )
}
