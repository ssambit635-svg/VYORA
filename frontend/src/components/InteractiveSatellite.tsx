import { RotateCcw, ZoomIn, ZoomOut } from 'lucide-react'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'

type SatelliteControls = { yaw: number; pitch: number; zoom: number; dragging: boolean; lastX: number; lastY: number }
const initialControls = (): SatelliteControls => ({ yaw: -.38, pitch: -.22, zoom: 5.3, dragging: false, lastX: 0, lastY: 0 })

export function InteractiveSatellite() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const controlsRef = useRef<SatelliteControls>(initialControls())

  useEffect(() => {
    const canvas = canvasRef.current
    const wrapper = wrapperRef.current
    if (!canvas || !wrapper) return
    let renderer: THREE.WebGLRenderer
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'high-performance' })
    } catch {
      wrapper.classList.add('satellite-webgl-unavailable')
      return
    }
    let disposed = false
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.12

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(31, 1, .1, 40)
    camera.position.set(0, .08, controlsRef.current.zoom)
    scene.add(new THREE.HemisphereLight('#eeeeee', '#1b1b1b', 1.7))
    const key = new THREE.DirectionalLight('#f5f5f5', 2.4)
    key.position.set(-3, 4, 5)
    scene.add(key)
    const edge = new THREE.DirectionalLight('#c6c6c6', .8)
    edge.position.set(3, -2, -3)
    scene.add(edge)

    const loader = new GLTFLoader()
    loader.setMeshoptDecoder(MeshoptDecoder)
    let model: THREE.Object3D | null = null
    loader.load('/assets/nasa-goes.glb', (gltf) => {
      const object = gltf.scene
      if (disposed) { disposeObject(object); return }
      const bounds = new THREE.Box3().setFromObject(object)
      const center = bounds.getCenter(new THREE.Vector3())
      const size = bounds.getSize(new THREE.Vector3())
      const scale = 2.75 / Math.max(size.x, size.y, size.z, .001)
      object.scale.setScalar(scale)
      object.position.set(-center.x * scale, -center.y * scale, -center.z * scale)
      object.traverse((item) => {
        if (item instanceof THREE.Mesh) {
          item.castShadow = false
          item.receiveShadow = false
          const materials = Array.isArray(item.material) ? item.material : [item.material]
          materials.forEach((material) => {
            if ('roughness' in material) (material as THREE.MeshStandardMaterial).roughness = Math.max(.38, (material as THREE.MeshStandardMaterial).roughness ?? .5)
          })
        }
      })
      model = object
      scene.add(object)
    }, undefined, () => wrapper.classList.add('satellite-model-fallback'))

    const handleWheel = (event: WheelEvent) => {
      event.preventDefault()
      controlsRef.current.zoom = THREE.MathUtils.clamp(controlsRef.current.zoom + event.deltaY * .0045, 4.4, 10)
    }
    wrapper.addEventListener('wheel', handleWheel, { passive: false })
    const resize = () => {
      const { width, height } = wrapper.getBoundingClientRect()
      if (!width || !height) return
      renderer.setSize(width, height, false)
      camera.aspect = width / height
      camera.updateProjectionMatrix()
    }
    const observer = new ResizeObserver(resize)
    observer.observe(wrapper)
    resize()
    let frame = 0
    let previous = 0
    const render = (time: number) => {
      frame = requestAnimationFrame(render)
      if (time - previous < 1000 / 40) return
      const delta = previous ? Math.min(50, time - previous) / 1000 : .025
      previous = time
      const state = controlsRef.current
      if (model) {
        const idleTurn = state.dragging ? 0 : Math.sin(time * .00018) * .018
        model.rotation.set(state.pitch, state.yaw + idleTurn, .12)
      }
      camera.position.z = THREE.MathUtils.damp(camera.position.z, state.zoom, 4, delta)
      camera.lookAt(0, 0, 0)
      renderer.render(scene, camera)
    }
    frame = requestAnimationFrame(render)

    return () => {
      disposed = true
      cancelAnimationFrame(frame)
      wrapper.removeEventListener('wheel', handleWheel)
      observer.disconnect()
      scene.traverse((item) => {
        if (item instanceof THREE.Mesh) {
          item.geometry.dispose()
          const materials = Array.isArray(item.material) ? item.material : [item.material]
          materials.forEach((material) => material.dispose())
        }
      })
      renderer.dispose()
    }
  }, [])

  const zoomBy = (distance: number) => {
    controlsRef.current.zoom = THREE.MathUtils.clamp(controlsRef.current.zoom + distance, 4.4, 10)
  }
  const resetView = () => { controlsRef.current = initialControls() }

  return <div className="interactive-satellite" ref={wrapperRef} role="group" aria-label="Interactive NASA GOES spacecraft model">
    <canvas
      ref={canvasRef}
      className="interactive-satellite-canvas"
      role="img"
      aria-label="Interactive NASA GOES three-dimensional spacecraft model. Drag to rotate; scroll to zoom; use arrow keys to rotate."
      tabIndex={0}
      onPointerDown={(event) => {
        const state = controlsRef.current
        state.dragging = true
        state.lastX = event.clientX
        state.lastY = event.clientY
        event.currentTarget.setPointerCapture(event.pointerId)
      }}
      onPointerMove={(event) => {
        const state = controlsRef.current
        if (!state.dragging) return
        state.yaw += (event.clientX - state.lastX) * .007
        state.pitch = THREE.MathUtils.clamp(state.pitch + (event.clientY - state.lastY) * .007, -1.1, 1.1)
        state.lastX = event.clientX
        state.lastY = event.clientY
      }}
      onPointerUp={() => { controlsRef.current.dragging = false }}
      onPointerCancel={() => { controlsRef.current.dragging = false }}
      onKeyDown={(event) => {
        if (event.key === 'ArrowLeft') { event.preventDefault(); controlsRef.current.yaw -= .12 }
        if (event.key === 'ArrowRight') { event.preventDefault(); controlsRef.current.yaw += .12 }
        if (event.key === 'ArrowUp') { event.preventDefault(); controlsRef.current.pitch = THREE.MathUtils.clamp(controlsRef.current.pitch - .1, -1.1, 1.1) }
        if (event.key === 'ArrowDown') { event.preventDefault(); controlsRef.current.pitch = THREE.MathUtils.clamp(controlsRef.current.pitch + .1, -1.1, 1.1) }
        if (event.key === 'Home') { event.preventDefault(); resetView() }
      }}
    />
    <div className="satellite-view-controls" aria-label="Spacecraft model controls">
      <button onClick={() => zoomBy(-.55)} aria-label="Zoom in spacecraft model" title="Zoom in"><ZoomIn size={14} /></button>
      <button onClick={() => zoomBy(.55)} aria-label="Zoom out spacecraft model" title="Zoom out"><ZoomOut size={14} /></button>
      <button onClick={resetView} aria-label="Reset spacecraft view" title="Reset view"><RotateCcw size={13} /></button>
    </div>
    <span className="satellite-model-caption">DRAG TO ROTATE <i /> SCROLL TO ZOOM <i /> GOES · NASA 3D MODEL · NOT TO SCALE</span>
  </div>
}

function disposeObject(root: THREE.Object3D) {
  root.traverse((item) => {
    if (item instanceof THREE.Mesh) {
      item.geometry.dispose()
      const materials = Array.isArray(item.material) ? item.material : [item.material]
      materials.forEach((material) => material.dispose())
    }
  })
}
