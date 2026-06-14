'use client'

import { useEffect, useRef } from 'react'
import * as THREE from 'three'

interface ThreeBackgroundProps {
  className?: string
}

export default function ThreeBackground({ className = '' }: ThreeBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current) return

    const container = containerRef.current
    const width = container.clientWidth
    const height = container.clientHeight

    // Scene setup
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0x0a0b0f)

    // Camera
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
    camera.position.z = 5

    // Renderer
    const renderer = new THREE.WebGLRenderer({ 
      antialias: true, 
      alpha: true,
      powerPreference: 'high-performance'
    })
    renderer.setSize(width, height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setClearColor(0x000000, 0)
    container.appendChild(renderer.domElement)

    // Create floating geometric shapes (cyberpunk style)
    const shapes: THREE.Mesh[] = []
    
    // Main cube
    const cubeGeometry = new THREE.BoxGeometry(1.2, 1.2, 1.2)
    const cubeMaterial = new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      metalness: 0.8,
      roughness: 0.2,
      transparent: true,
      opacity: 0.6,
    })
    const cube = new THREE.Mesh(cubeGeometry, cubeMaterial)
    cube.position.set(0, 0, 0)
    scene.add(cube)
    shapes.push(cube)

    // Wireframe cube (outer)
    const wireGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5)
    const wireMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ffa3,
      wireframe: true,
      transparent: true,
      opacity: 0.3,
    })
    const wireCube = new THREE.Mesh(wireGeometry, wireMaterial)
    wireCube.position.set(0, 0, 0)
    scene.add(wireCube)
    shapes.push(wireCube)

    // Small orbiting particles
    const particleCount = 50
    const particleGeometry = new THREE.BufferGeometry()
    const positions = new Float32Array(particleCount * 3)
    
    for (let i = 0; i < particleCount; i++) {
      const angle = (i / particleCount) * Math.PI * 2
      const radius = 2 + Math.random() * 1.5
      positions[i * 3] = Math.cos(angle) * radius
      positions[i * 3 + 1] = Math.sin(angle) * radius
      positions[i * 3 + 2] = (Math.random() - 0.5) * 2
    }
    
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    const particleMaterial = new THREE.PointsMaterial({
      color: 0x6366f1,
      size: 0.05,
      transparent: true,
      opacity: 0.8,
    })
    const particles = new THREE.Points(particleGeometry, particleMaterial)
    scene.add(particles)

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
    scene.add(ambientLight)

    const pointLight1 = new THREE.PointLight(0x6366f1, 1, 10)
    pointLight1.position.set(3, 3, 3)
    scene.add(pointLight1)

    const pointLight2 = new THREE.PointLight(0x00ffa3, 0.8, 10)
    pointLight2.position.set(-3, -3, 3)
    scene.add(pointLight2)

    // Animation
    let animationId: number
    const clock = new THREE.Clock()

    function animate() {
      const elapsed = clock.getElapsedTime()
      
      // Rotate main cube
      cube.rotation.x = elapsed * 0.3
      cube.rotation.y = elapsed * 0.5
      
      // Counter-rotate wireframe
      wireCube.rotation.x = -elapsed * 0.2
      wireCube.rotation.y = -elapsed * 0.3

      // Float effect
      cube.position.y = Math.sin(elapsed) * 0.2
      wireCube.position.y = Math.sin(elapsed * 0.8) * 0.15

      // Rotate particles
      particles.rotation.y = elapsed * 0.1

      // Pulse effect on material
      const pulse = 0.5 + Math.sin(elapsed * 2) * 0.1
      cubeMaterial.opacity = pulse

      renderer.render(scene, camera)
      animationId = requestAnimationFrame(animate)
    }

    animate()

    // Handle resize
    function handleResize() {
      const w = container.clientWidth
      const h = container.clientHeight
      camera.aspect = w / h
      camera.updateProjectionMatrix()
      renderer.setSize(w, h)
    }

    window.addEventListener('resize', handleResize)

    // Cleanup
    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', handleResize)
      
      shapes.forEach((mesh: THREE.Mesh) => {
        mesh.geometry.dispose()
        if (Array.isArray(mesh.material)) {
          mesh.material.forEach((m: THREE.Material) => m.dispose())
        } else {
          mesh.material.dispose()
        }
      })
      particleGeometry.dispose()
      particleMaterial.dispose()
      renderer.dispose()
      container.removeChild(renderer.domElement)
    }
  }, [])

  return (
    <div 
      ref={containerRef} 
      className={`absolute inset-0 ${className}`}
      style={{ background: 'transparent' }}
    />
  )
}