import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'

export function InteractiveSatellite() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

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
    camera.position.set(0, .08, 5.3)
    scene.add(new THREE.HemisphereLight('#ececf0', '#1b1b1f', 1.7))
    const key = new THREE.DirectionalLight('#fff9f1', 2.4)
    key.position.set(-3, 4, 5)
    scene.add(key)
    const edge = new THREE.DirectionalLight('#c6b7dd', .8)
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
      object.rotation.set(-.22, -.38, .12)
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
      previous = time
      if (model) model.rotation.y = -.38 + Math.sin(time * .00024) * .055
      camera.lookAt(0, 0, 0)
      renderer.render(scene, camera)
    }
    frame = requestAnimationFrame(render)

    return () => {
      disposed = true
      cancelAnimationFrame(frame)
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

  return <div className="interactive-satellite" ref={wrapperRef}>
    <canvas ref={canvasRef} className="interactive-satellite-canvas" role="img" aria-label="Slowly turning NASA GOES spacecraft 3D model, shown for illustration and not live positioning." />
    <span className="satellite-model-caption">GOES · NASA 3D MODEL <i /> NOT TO SCALE</span>
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
