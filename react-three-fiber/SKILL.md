---
name: React Three Fiber
description: Expert guidance for building 3D experiences with React Three Fiber (R3F), Three.js, and Drei helpers.
---

# React Three Fiber

Expert guidance for building 3D experiences with React Three Fiber (R3F), Three.js, and Drei helpers.

## Capabilities

- Set up React Three Fiber projects from scratch
- Create 3D scenes with cameras, lights, and meshes
- Use Drei helpers for common patterns (OrbitControls, Environment, Text, etc.)
- Implement animations with useFrame hook
- Handle user interactions (click, hover, drag)
- Optimize performance (instancing, LOD, suspense, lazy loading)
- Integrate physics with @react-three/rapier or @react-three/cannon
- Post-processing effects with @react-three/postprocessing

## Guidelines

### Project Setup

- Use Vite + React for fast development
- Install core packages: `@react-three/fiber`, `three`, `@react-three/drei`
- Always pin Three.js version to avoid breaking changes
- Use TypeScript for better DX with 3D math types

### Scene Structure

```tsx
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Environment } from '@react-three/drei'

export default function App() {
  return (
    <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} />
      <mesh>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="orange" />
      </mesh>
      <OrbitControls />
      <Environment preset="city" />
    </Canvas>
  )
}
```

### Animation with useFrame

```tsx
import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

function SpinningBox() {
  const meshRef = useRef<THREE.Mesh>(null!)

  useFrame((state, delta) => {
    meshRef.current.rotation.y += delta
  })

  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}
```

### Performance Best Practices

- Use `instancedMesh` for repeated geometries
- Avoid creating new objects in useFrame (reuse vectors/quaternions)
- Use `React.memo` for static scene objects
- Leverage `Suspense` for async model loading
- Use `useGLTF.preload()` for critical models
- Set `frameloop="demand"` on Canvas if scene is mostly static
- Use `drei`'s `Bvh` component for complex raycasting

### Loading 3D Models

```tsx
import { useGLTF } from '@react-three/drei'

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url)
  return <primitive object={scene} />
}

useGLTF.preload('/model.glb')
```

### Common Drei Helpers

| Helper | Use Case |
|--------|----------|
| `OrbitControls` | Camera orbit/zoom/pan |
| `Environment` | HDR environment lighting |
| `Text` / `Text3D` | 3D text rendering |
| `Html` | HTML overlays in 3D space |
| `useGLTF` | Load GLTF/GLB models |
| `Float` | Floating animation |
| `MeshReflectorMaterial` | Reflective floors |
| `Sparkles` / `Stars` | Particle effects |

### Responsive Design

- Use `Canvas` with `style={{ width: '100%', height: '100vh' }}`
- Handle resize automatically (R3F does this by default)
- Use `useThree` hook to access viewport size for responsive layouts

## Dependencies

```json
{
  "@react-three/fiber": "^9",
  "@react-three/drei": "^10",
  "three": "^0.170",
  "@types/three": "^0.170"
}
```
