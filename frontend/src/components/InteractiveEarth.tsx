import { RotateCcw } from 'lucide-react'
import { useCallback, useEffect, useRef } from 'react'

type LandDots = { points: [number, number][] }
type SpherePoint = [number, number, number]
type GlobeState = { yaw: number; pitch: number; dragging: boolean; lastX: number; lastY: number }
type Projected = { x: number; y: number; z: number }

const INITIAL_YAW = -0.58
const INITIAL_PITCH = -0.18
const NASA_EYES_URL = 'https://eyes.nasa.gov/apps/earth/#/satellites'

export function InteractiveEarth() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const stateRef = useRef<GlobeState>({ yaw: INITIAL_YAW, pitch: INITIAL_PITCH, dragging: false, lastX: 0, lastY: 0 })
  const pointsRef = useRef<SpherePoint[]>([])

  useEffect(() => {
    let cancelled = false
    fetch('/assets/earth-land-dots.json')
      .then((response) => response.ok ? response.json() as Promise<LandDots> : Promise.reject(new Error('Globe data unavailable')))
      .then((data) => {
        if (cancelled) return
        pointsRef.current = data.points.map(([lon, lat]) => {
          const phi = lat * Math.PI / 180
          const lambda = lon * Math.PI / 180
          return [Math.cos(phi) * Math.sin(lambda), Math.sin(phi), Math.cos(phi) * Math.cos(lambda)]
        })
      })
      .catch(() => { if (!cancelled) pointsRef.current = [] })
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    const wrapper = wrapperRef.current
    const context = canvas?.getContext('2d')
    if (!canvas || !wrapper || !context) return

    let frame = 0
    let width = 0
    let height = 0
    let pixelRatio = 1
    let previous = 0
    let lastDraw = 0
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const resize = () => {
      const rect = wrapper.getBoundingClientRect()
      pixelRatio = Math.min(window.devicePixelRatio || 1, 2)
      width = rect.width
      height = rect.height
      canvas.width = Math.round(width * pixelRatio)
      canvas.height = Math.round(height * pixelRatio)
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0)
    }
    const observer = new ResizeObserver(resize)
    observer.observe(wrapper)
    resize()

    const project = (x: number, y: number, z: number, yaw: number, pitch: number, radius: number, cx: number, cy: number): Projected => {
      const cosYaw = Math.cos(yaw), sinYaw = Math.sin(yaw)
      const x1 = x * cosYaw + z * sinYaw
      const z1 = z * cosYaw - x * sinYaw
      const cosPitch = Math.cos(pitch), sinPitch = Math.sin(pitch)
      const y1 = y * cosPitch - z1 * sinPitch
      const z2 = y * sinPitch + z1 * cosPitch
      return { x: cx + x1 * radius, y: cy - y1 * radius, z: z2 }
    }
    const toVector = (lon: number, lat: number): SpherePoint => {
      const phi = lat * Math.PI / 180
      const lambda = lon * Math.PI / 180
      return [Math.cos(phi) * Math.sin(lambda), Math.sin(phi), Math.cos(phi) * Math.cos(lambda)]
    }
    const latitudeLines: SpherePoint[][] = []
    for (let lat = -75; lat <= 75; lat += 15) {
      const line: SpherePoint[] = []
      for (let lon = -180; lon <= 180; lon += 3) line.push(toVector(lon, lat))
      latitudeLines.push(line)
    }
    const longitudeLines: SpherePoint[][] = []
    for (let lon = -165; lon <= 180; lon += 15) {
      const line: SpherePoint[] = []
      for (let lat = -70; lat <= 70; lat += 3) line.push(toVector(lon, lat))
      longitudeLines.push(line)
    }
    const lineOnSphere = (coordinates: SpherePoint[], yaw: number, pitch: number, radius: number, cx: number, cy: number, color: string, lineWidth: number) => {
      context.beginPath()
      let started = false
      for (const [x, y, z] of coordinates) {
        const p = project(x, y, z, yaw, pitch, radius, cx, cy)
        if (p.z > 0) {
          if (!started) context.moveTo(p.x, p.y)
          else context.lineTo(p.x, p.y)
          started = true
        } else started = false
      }
      context.strokeStyle = color
      context.lineWidth = lineWidth
      context.stroke()
    }
    const orbitPoint = (angle: number, inclination: number, node: number, altitude: number) => {
      const along = Math.cos(angle)
      const across = Math.sin(angle)
      const x0 = along
      const y0 = across * Math.sin(inclination)
      const z0 = across * Math.cos(inclination)
      return {
        x: (x0 * Math.cos(node) - y0 * Math.sin(node)) * altitude,
        y: (x0 * Math.sin(node) + y0 * Math.cos(node)) * altitude,
        z: z0 * altitude,
      }
    }
    const drawOrbit = (yaw: number, pitch: number, radius: number, cx: number, cy: number, angle: number, inclination: number, node: number, altitude: number, front: boolean) => {
      const samples = 240
      context.beginPath()
      let started = false
      for (let i = 0; i <= samples; i += 1) {
        const t = i / samples * Math.PI * 2
        const point = orbitPoint(t, inclination, node, altitude)
        const p = project(point.x, point.y, point.z, yaw, pitch, radius, cx, cy)
        if ((p.z > 0) === front) {
          if (!started) context.moveTo(p.x, p.y)
          else context.lineTo(p.x, p.y)
          started = true
        } else started = false
      }
      context.setLineDash(front ? [] : [2, 6])
      context.strokeStyle = front ? 'rgba(179, 159, 224, .68)' : 'rgba(107, 95, 132, .32)'
      context.lineWidth = front ? 1.1 : .8
      context.stroke()
      context.setLineDash([])
      const satellite = orbitPoint(angle, inclination, node, altitude)
      const p = project(satellite.x, satellite.y, satellite.z, yaw, pitch, radius, cx, cy)
      if (front && p.z > 0) drawSatellite(p.x, p.y, radius, angle + node)
    }
    const drawSatellite = (x: number, y: number, radius: number, heading: number) => {
      const size = Math.max(6, radius * .045)
      context.save()
      context.translate(x, y)
      context.rotate(heading)
      context.fillStyle = '#d7caf7'
      context.strokeStyle = '#d7caf7'
      context.lineWidth = 1
      context.fillRect(-size * .25, -size * .32, size * .5, size * .64)
      context.fillStyle = '#83cbbd'
      context.fillRect(-size * 1.45, -size * .25, size * .95, size * .5)
      context.fillRect(size * .5, -size * .25, size * .95, size * .5)
      context.beginPath()
      context.moveTo(0, -size * .3)
      context.lineTo(size * .2, -size * .72)
      context.stroke()
      context.restore()
    }

    const render = (time: number) => {
      if (!width || !height || time - lastDraw < 1000 / 30) { frame = requestAnimationFrame(render); return }
      const dt = previous ? Math.min(50, time - previous) : 33
      previous = time
      lastDraw = time
      const state = stateRef.current
      const motionTime = reduceMotion ? 0 : time
      if (!reduceMotion && !state.dragging) state.yaw += dt * .000012

      context.clearRect(0, 0, width, height)
      const cx = width / 2
      const cy = height / 2
      const radius = Math.min(width, height) * .385
      const yaw = state.yaw
      const pitch = state.pitch

      // Subtle, matte orbit paths behind the globe.
      drawOrbit(yaw, pitch, radius, cx, cy, motionTime * .00016, .68, -.52, 1.2, false)
      drawOrbit(yaw, pitch, radius, cx, cy, motionTime * .00011 + 1.9, 1.08, .9, 1.31, false)

      const sphere = context.createRadialGradient(cx - radius * .34, cy - radius * .38, radius * .06, cx, cy, radius * 1.12)
      sphere.addColorStop(0, '#211b30')
      sphere.addColorStop(.62, '#120f1c')
      sphere.addColorStop(1, '#09080e')
      context.beginPath()
      context.arc(cx, cy, radius, 0, Math.PI * 2)
      context.fillStyle = sphere
      context.fill()
      context.save()
      context.beginPath()
      context.arc(cx, cy, radius, 0, Math.PI * 2)
      context.clip()

      // Graticule is a visual reference only; it is not a map coordinate display.
      for (const line of latitudeLines) lineOnSphere(line, yaw, pitch, radius, cx, cy, 'rgba(159, 145, 190, .13)', .65)
      for (const line of longitudeLines) lineOnSphere(line, yaw, pitch, radius, cx, cy, 'rgba(159, 145, 190, .12)', .65)

      for (const [x, y, z] of pointsRef.current) {
        const p = project(x, y, z, yaw, pitch, radius, cx, cy)
        if (p.z <= 0) continue
        const detail = .7 + p.z * .5
        context.fillStyle = p.z > .7 ? 'rgba(207, 192, 245, .94)' : 'rgba(164, 143, 213, .78)'
        const dot = Math.max(.65, radius * .0052 * detail)
        context.fillRect(p.x - dot / 2, p.y - dot / 2, dot, dot)
      }

      // Front hemisphere of each orbit, with simple spacecraft silhouettes.
      drawOrbit(yaw, pitch, radius, cx, cy, motionTime * .00016, .68, -.52, 1.2, true)
      drawOrbit(yaw, pitch, radius, cx, cy, motionTime * .00011 + 1.9, 1.08, .9, 1.31, true)
      context.restore()
      context.beginPath()
      context.arc(cx, cy, radius, 0, Math.PI * 2)
      context.strokeStyle = 'rgba(196, 180, 232, .32)'
      context.lineWidth = 1
      context.stroke()

      frame = requestAnimationFrame(render)
    }
    frame = requestAnimationFrame(render)
    return () => {
      cancelAnimationFrame(frame)
      observer.disconnect()
    }
  }, [])

  const rotate = useCallback((dx: number, dy: number) => {
    const state = stateRef.current
    state.yaw += dx * .008
    state.pitch = Math.max(-1.05, Math.min(1.05, state.pitch + dy * .008))
  }, [])
  const reset = useCallback(() => {
    stateRef.current.yaw = INITIAL_YAW
    stateRef.current.pitch = INITIAL_PITCH
  }, [])

  return (
    <div className="interactive-earth" ref={wrapperRef}>
      <canvas
        ref={canvasRef}
        className="interactive-earth-canvas"
        aria-label="Interactive purple Earth globe with illustrative satellite orbits. Drag to rotate; use arrow keys or the reset button. Satellite positions are not live."
        role="img"
        tabIndex={0}
        onPointerDown={(event) => {
          stateRef.current.dragging = true
          stateRef.current.lastX = event.clientX
          stateRef.current.lastY = event.clientY
          event.currentTarget.setPointerCapture(event.pointerId)
        }}
        onPointerMove={(event) => {
          const state = stateRef.current
          if (!state.dragging) return
          rotate(event.clientX - state.lastX, event.clientY - state.lastY)
          state.lastX = event.clientX
          state.lastY = event.clientY
        }}
        onPointerUp={() => { stateRef.current.dragging = false }}
        onPointerCancel={() => { stateRef.current.dragging = false }}
        onKeyDown={(event) => {
          if (event.key === 'ArrowLeft') { event.preventDefault(); rotate(-13, 0) }
          if (event.key === 'ArrowRight') { event.preventDefault(); rotate(13, 0) }
          if (event.key === 'ArrowUp') { event.preventDefault(); rotate(0, -10) }
          if (event.key === 'ArrowDown') { event.preventDefault(); rotate(0, 10) }
          if (event.key === 'Home') { event.preventDefault(); reset() }
        }}
      />
      <button className="globe-reset" onClick={reset} aria-label="Reset globe orientation" title="Reset globe orientation"><RotateCcw size={13} /></button>
      <span className="globe-drag-hint">Drag to rotate · arrow keys · Home to reset</span>
    </div>
  )
}

export { NASA_EYES_URL }
