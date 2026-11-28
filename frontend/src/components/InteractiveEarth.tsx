import { RotateCcw, ZoomIn, ZoomOut } from 'lucide-react'
import { useCallback, useEffect, useRef } from 'react'
import type { RefObject } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'

const INITIAL_YAW = -0.28
const INITIAL_PITCH = -0.08
interface Props {
  scrollStageRef: RefObject<HTMLElement>
  enableScrollZoom?: boolean
}

type GlobeInteraction = { yaw: number; pitch: number; dragging: boolean; lastX: number; lastY: number }

function makeFallbackSatellite(accent: string) {
  const group = new THREE.Group()
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(.14, .17, .14),
    new THREE.MeshStandardMaterial({ color: '#d4d9e6', metalness: .68, roughness: .36 }),
  )
  group.add(body)
  const panelMaterial = new THREE.MeshStandardMaterial({ color: accent, metalness: .42, roughness: .42, emissive: accent, emissiveIntensity: .08 })
  for (const side of [-1, 1]) {
    const wing = new THREE.Mesh(new THREE.BoxGeometry(.22, .018, .14), panelMaterial)
    wing.position.x = side * .19
    group.add(wing)
  }
  const antenna = new THREE.Mesh(
    new THREE.ConeGeometry(.052, .1, 8),
    new THREE.MeshStandardMaterial({ color: '#f2eee3', metalness: .7, roughness: .3 }),
  )
  antenna.rotation.z = Math.PI
  antenna.position.y = -.12
  group.add(antenna)
  return group
}

export function InteractiveEarth({ scrollStageRef, enableScrollZoom = false }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const zoomTargetRef = useRef(6.05)
  const interactionRef = useRef<GlobeInteraction>({ yaw: INITIAL_YAW, pitch: INITIAL_PITCH, dragging: false, lastX: 0, lastY: 0 })

  useEffect(() => {
    const canvas = canvasRef.current
    const wrapper = wrapperRef.current
    if (!canvas || !wrapper) return

    let renderer: THREE.WebGLRenderer
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, powerPreference: 'high-performance' })
    } catch {
      wrapper.classList.add('earth-webgl-unavailable')
      return
    }
    let disposed = false
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.8))
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.08

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(34, 1, .1, 80)
    camera.position.set(0, .02, 6.05)
    zoomTargetRef.current = 6.05
    const handleWheel = (event: WheelEvent) => {
      if (!enableScrollZoom) return
      event.preventDefault()
      zoomTargetRef.current = THREE.MathUtils.clamp(zoomTargetRef.current + event.deltaY * .0045, 3.6, 8.5)
    }
    if (enableScrollZoom) wrapper.addEventListener('wheel', handleWheel, { passive: false })
    const ambient = new THREE.HemisphereLight('#dfe8ff', '#10131c', 1.05)
    scene.add(ambient)
    const sun = new THREE.DirectionalLight('#fff4df', 2.6)
    sun.position.set(-4.4, 2.7, 5.2)
    scene.add(sun)
    const rim = new THREE.DirectionalLight('#9b82e7', 1.15)
    rim.position.set(3.5, -1.5, -4.2)
    scene.add(rim)

    const earthRoot = new THREE.Group()
    scene.add(earthRoot)
    const earthRadius = 1.42
    const sphereGeometry = new THREE.SphereGeometry(earthRadius, 112, 80)
    const textureLoader = new THREE.TextureLoader()
    const textures: THREE.Texture[] = []
    const configureTexture = (texture: THREE.Texture, color = true) => {
      texture.colorSpace = color ? THREE.SRGBColorSpace : THREE.NoColorSpace
      texture.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy())
      textures.push(texture)
      return texture
    }

    const earth = new THREE.Mesh(
      sphereGeometry,
      new THREE.MeshStandardMaterial({ color: '#b5bdd0', roughness: .94, metalness: 0, emissive: '#17111f', emissiveIntensity: .12 }),
    )
    earth.rotation.y = Math.PI * .78
    earthRoot.add(earth)

    textureLoader.load('/assets/earth-day.webp', (dayTexture) => {
      if (disposed) { dayTexture.dispose(); return }
      configureTexture(dayTexture)
      const material = earth.material as THREE.MeshStandardMaterial
      material.map = dayTexture
      material.color.set('#dce3f2')
      material.needsUpdate = true
    })
    textureLoader.load('/assets/earth-night.webp', (nightTexture) => {
      if (disposed) { nightTexture.dispose(); return }
      configureTexture(nightTexture)
      const material = earth.material as THREE.MeshStandardMaterial
      material.emissiveMap = nightTexture
      material.emissive.set('#c18b4b')
      material.emissiveIntensity = .42
      material.needsUpdate = true
    })

    const clouds = new THREE.Mesh(
      new THREE.SphereGeometry(earthRadius * 1.008, 96, 64),
      new THREE.MeshStandardMaterial({ color: '#e8eaf2', transparent: true, opacity: .19, depthWrite: false, roughness: 1 }),
    )
    earthRoot.add(clouds)
    textureLoader.load('/assets/earth-clouds.webp', (cloudTexture) => {
      if (disposed) { cloudTexture.dispose(); return }
      configureTexture(cloudTexture)
      const material = clouds.material as THREE.MeshStandardMaterial
      material.map = cloudTexture
      material.alphaMap = cloudTexture
      material.needsUpdate = true
    })

    const atmosphere = new THREE.Mesh(
      new THREE.SphereGeometry(earthRadius * 1.038, 96, 64),
      new THREE.ShaderMaterial({
        transparent: true,
        side: THREE.BackSide,
        depthWrite: false,
        uniforms: { glowColor: { value: new THREE.Color('#8d84e8') } },
        vertexShader: `varying vec3 vNormal; varying vec3 vViewPosition; void main(){ vec4 mvPosition=modelViewMatrix*vec4(position,1.0); vNormal=normalize(normalMatrix*normal); vViewPosition=-mvPosition.xyz; gl_Position=projectionMatrix*mvPosition; }`,
        fragmentShader: `uniform vec3 glowColor; varying vec3 vNormal; varying vec3 vViewPosition; void main(){ float rim=pow(1.0-max(dot(normalize(vNormal),normalize(vViewPosition)),0.0),2.5); gl_FragColor=vec4(glowColor, rim*.16); }`,
      }),
    )
    earthRoot.add(atmosphere)

    const orbitMaterial = (color: string, opacity: number) => new THREE.LineBasicMaterial({ color, transparent: true, opacity, depthWrite: false })
    const satelliteAnchors: THREE.Group[] = []
    const gltfLoader = new GLTFLoader()
    gltfLoader.setMeshoptDecoder(MeshoptDecoder)
    const disposeObject = (root: THREE.Object3D) => root.traverse((item) => {
      if (item instanceof THREE.Mesh) {
        item.geometry.dispose()
        const materials = Array.isArray(item.material) ? item.material : [item.material]
        materials.forEach((material) => material.dispose())
      }
    })
    const addOrbit = (radius: number, tilt: THREE.Euler, tint: string, opacity: number, phase: number, modelPath: string, fallbackColor: string) => {
      const orbit = new THREE.Group()
      orbit.rotation.copy(tilt)
      const curve = new THREE.EllipseCurve(0, 0, radius, radius * .7, 0, Math.PI * 2, false, 0)
      const points = curve.getPoints(180).map((p) => new THREE.Vector3(p.x, 0, p.y))
      const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), orbitMaterial(tint, opacity))
      orbit.add(line)
      const anchor = new THREE.Group()
      anchor.position.set(radius, 0, 0)
      anchor.rotation.y = phase
      anchor.add(makeFallbackSatellite(fallbackColor))
      orbit.add(anchor)
      scene.add(orbit)
      satelliteAnchors.push(orbit)

      gltfLoader.load(modelPath, (gltf) => {
        const model = gltf.scene
        if (disposed) { disposeObject(model); return }
        const bounds = new THREE.Box3().setFromObject(model)
        const center = bounds.getCenter(new THREE.Vector3())
        const size = bounds.getSize(new THREE.Vector3())
        const scale = .42 / Math.max(size.x, size.y, size.z, .001)
        model.scale.setScalar(scale)
        model.position.set(-center.x * scale, -center.y * scale, -center.z * scale)
        model.traverse((item) => {
          if (item instanceof THREE.Mesh) {
            item.castShadow = false
            item.receiveShadow = false
            const mats = Array.isArray(item.material) ? item.material : [item.material]
            mats.forEach((mat) => { if ('roughness' in mat) (mat as THREE.MeshStandardMaterial).roughness = Math.max(.32, (mat as THREE.MeshStandardMaterial).roughness ?? .45) })
          }
        })
        for (const child of [...anchor.children]) { anchor.remove(child); disposeObject(child) }
        anchor.add(model)
      }, undefined, () => {
        // The hand-built fallback remains visible if the optional NASA GLB cannot load.
      })
    }
    addOrbit(1.94, new THREE.Euler(.65, .06, -.28), '#b5a5e8', .48, .4, '/assets/nasa-goes.glb', '#a78bfa')
    addOrbit(2.12, new THREE.Euler(-.82, .24, .42), '#91aacd', .28, 2.5, '/assets/nasa-landsat8.glb', '#77b5c9')

    const resize = () => {
      const { width, height } = wrapper.getBoundingClientRect()
      if (!width || !height) return
      renderer.setSize(width, height, false)
      camera.aspect = width / height
      camera.updateProjectionMatrix()
    }
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(wrapper)
    resize()

    let scrollProgress = 0
    let targetScrollProgress = 0
    let frame = 0
    let previousTime = 0
    let visible = true
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const measureScroll = () => {
      const stage = scrollStageRef.current
      if (!stage || reduceMotion || enableScrollZoom) { targetScrollProgress = 0; return }
      const rect = stage.getBoundingClientRect()
      const headerHeight = document.querySelector('.landing-header')?.getBoundingClientRect().height ?? 0
      targetScrollProgress = THREE.MathUtils.clamp((headerHeight - rect.top) / Math.max(1, window.innerHeight * .68), 0, 1)
    }
    measureScroll()
    window.addEventListener('scroll', measureScroll, { passive: true })
    window.addEventListener('resize', measureScroll)
    const visibilityObserver = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting }, { rootMargin: '120px' })
    visibilityObserver.observe(wrapper)

    const render = (time: number) => {
      frame = requestAnimationFrame(render)
      if (!visible || time - previousTime < 1000 / 40) return
      const delta = previousTime ? Math.min(50, time - previousTime) : 25
      previousTime = time
      scrollProgress = THREE.MathUtils.damp(scrollProgress, targetScrollProgress, 4.5, delta / 1000)
      const interaction = interactionRef.current
      const turn = reduceMotion ? 0 : time * .000012
      earthRoot.rotation.y = turn + scrollProgress * 1.45 + interaction.yaw
      earthRoot.rotation.x = interaction.pitch + Math.sin(scrollProgress * Math.PI) * .045
      clouds.rotation.y = earthRoot.rotation.y + (reduceMotion ? 0 : time * .0000025)
      satelliteAnchors[0].rotation.y = time * .000055 + scrollProgress * 2.4
      satelliteAnchors[1].rotation.y = -time * .00004 - scrollProgress * 1.8
      const zoom = enableScrollZoom ? zoomTargetRef.current : 6.05 - Math.sin(scrollProgress * Math.PI) * .3 - scrollProgress * .14
      camera.position.z = THREE.MathUtils.damp(camera.position.z, zoom, 3.4, delta / 1000)
      camera.position.y = THREE.MathUtils.damp(camera.position.y, .02 + scrollProgress * .1, 3, delta / 1000)
      camera.lookAt(0, 0, 0)
      renderer.render(scene, camera)
    }
    frame = requestAnimationFrame(render)

    return () => {
      disposed = true
      cancelAnimationFrame(frame)
      window.removeEventListener('scroll', measureScroll)
      window.removeEventListener('resize', measureScroll)
      if (enableScrollZoom) wrapper.removeEventListener('wheel', handleWheel)
      resizeObserver.disconnect()
      visibilityObserver.disconnect()
      scene.traverse((item) => {
        if (item instanceof THREE.Mesh) {
          item.geometry.dispose()
          const materials = Array.isArray(item.material) ? item.material : [item.material]
          materials.forEach((material) => material.dispose())
        }
      })
      textures.forEach((texture) => texture.dispose())
      renderer.dispose()
    }
  }, [scrollStageRef, enableScrollZoom])

  const reset = useCallback(() => {
    interactionRef.current.yaw = INITIAL_YAW
    interactionRef.current.pitch = INITIAL_PITCH
    zoomTargetRef.current = 6.05
  }, [])
  const changeZoom = useCallback((amount: number) => {
    zoomTargetRef.current = THREE.MathUtils.clamp(zoomTargetRef.current + amount, 3.6, 8.5)
  }, [])

  return (
    <div className="interactive-earth" ref={wrapperRef}>
      <canvas
        ref={canvasRef}
        className="interactive-earth-canvas"
        aria-label={`Three-dimensional Earth with NASA GOES and Landsat spacecraft models on illustrative, not-to-scale orbits. Drag to rotate; press arrow keys to rotate or Home to reset.${enableScrollZoom ? ' Scroll over the globe to zoom.' : ' Scrolling the page moves the camera.'}`}
        role="img"
        tabIndex={0}
        onPointerDown={(event) => {
          interactionRef.current.dragging = true
          interactionRef.current.lastX = event.clientX
          interactionRef.current.lastY = event.clientY
          event.currentTarget.setPointerCapture(event.pointerId)
        }}
        onPointerMove={(event) => {
          const state = interactionRef.current
          if (!state.dragging) return
          state.yaw += (event.clientX - state.lastX) * .006
          state.pitch = THREE.MathUtils.clamp(state.pitch + (event.clientY - state.lastY) * .006, -.8, .8)
          state.lastX = event.clientX
          state.lastY = event.clientY
        }}
        onPointerUp={() => { interactionRef.current.dragging = false }}
        onPointerCancel={() => { interactionRef.current.dragging = false }}
        onKeyDown={(event) => {
          if (event.key === 'ArrowLeft') { event.preventDefault(); interactionRef.current.yaw -= .16 }
          if (event.key === 'ArrowRight') { event.preventDefault(); interactionRef.current.yaw += .16 }
          if (event.key === 'ArrowUp') { event.preventDefault(); interactionRef.current.pitch = THREE.MathUtils.clamp(interactionRef.current.pitch - .12, -.8, .8) }
          if (event.key === 'ArrowDown') { event.preventDefault(); interactionRef.current.pitch = THREE.MathUtils.clamp(interactionRef.current.pitch + .12, -.8, .8) }
          if (event.key === 'Home') { event.preventDefault(); reset() }
        }}
      />
      {enableScrollZoom && <div className="globe-zoom-controls" aria-label="Earth zoom controls"><button onClick={() => changeZoom(-.55)} aria-label="Zoom in" title="Zoom in"><ZoomIn size={15} /></button><button onClick={() => changeZoom(.55)} aria-label="Zoom out" title="Zoom out"><ZoomOut size={15} /></button></div>}
      <button className="globe-reset" onClick={reset} aria-label="Reset Earth view" title="Reset Earth view"><RotateCcw size={14} /></button>
      <span className="globe-drag-hint">DRAG TO ROTATE <i /> {enableScrollZoom ? 'SCROLL TO ZOOM' : 'SCROLL TO EXPLORE'}</span>
      <div className="earth-spacecraft-tags" aria-hidden="true"><span>GOES</span><span>LANDSAT 8</span></div>
    </div>
  )
}
