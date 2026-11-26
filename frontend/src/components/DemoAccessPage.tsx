import { ArrowLeft, ArrowRight, CircleUserRound, ShieldCheck } from 'lucide-react'

interface Props {
  onContinue: () => void
  onBack: () => void
}

export function DemoAccessPage({ onContinue, onBack }: Props) {
  return (
    <main className="access-page">
      <section className="access-card">
        <button className="back-link" onClick={onBack}><ArrowLeft size={15} /> Back to Vyora</button>
        <div className="access-icon"><CircleUserRound size={23} /></div>
        <span className="section-kicker">DEMO WORKSPACE</span>
        <h1>Enter the analyst view.</h1>
        <p>This build has no account or authentication service. Continue as a local demo analyst—no password is requested or stored.</p>
        <div className="access-notice"><ShieldCheck size={16} /><span>Demo session only · stored in this browser tab</span></div>
        <button className="button-primary access-submit" onClick={onContinue}>Continue as demo analyst <ArrowRight size={16} /></button>
        <small>For a production sign-in, connect a real identity provider and protected backend session.</small>
      </section>
      <div className="access-earth" aria-hidden="true"><img src="/assets/vyora-earth-pointcloud.png" alt="" /></div>
    </main>
  )
}
