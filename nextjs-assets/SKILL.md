---
name: Next.js Asset Optimization
description: Expert guidance on optimizing images and fonts in Next.js — next/image, next/font, local/remote images, Google Fonts, lazy loading, blur placeholders, and responsive sizing.
---

# Next.js Asset Optimization

Expert guidance on optimizing images in Next.js using the Image component — local/remote images, lazy loading, blur placeholders, and responsive sizing.

@doc-version: 16.2.6

## Core Concepts

`<Image>` จาก `next/image` extends HTML `<img>` ด้วย:
- **Size optimization** — serve ภาพขนาดถูกต้องต่อ device + format WebP
- **Visual stability** — ป้องกัน layout shift อัตโนมัติ
- **Faster page loads** — lazy loading ด้วย native browser + blur-up placeholders
- **Asset flexibility** — resize on-demand แม้ภาพอยู่บน remote server

## Guidelines

### 1. Basic Usage

```tsx
import Image from 'next/image'

export default function Page() {
  return <Image src="/hero.jpg" alt="Hero image" width={1200} height={600} />
}
```

### 2. Local Images

#### จาก `public` folder

```tsx
import Image from 'next/image'

export default function Page() {
  return (
    <Image
      src="/profile.png"
      alt="Picture of the author"
      width={500}
      height={500}
    />
  )
}
```

#### Static Import (แนะนำ — auto width/height/blur)

```tsx
import Image from 'next/image'
import ProfileImage from './profile.png'

export default function Page() {
  return (
    <Image
      src={ProfileImage}
      alt="Picture of the author"
      // width={500} — automatically provided
      // height={500} — automatically provided
      // blurDataURL="data:..." — automatically provided
      placeholder="blur" // Optional blur-up while loading
    />
  )
}
```

**ข้อดีของ static import:**
- `width` และ `height` ถูกกำหนดอัตโนมัติ
- `blurDataURL` ถูกสร้างอัตโนมัติ
- ป้องกัน layout shift โดยไม่ต้องระบุขนาดเอง

#### Dynamic Import (Server Component)

สำหรับ images ที่ไม่สามารถ static import ได้:

```tsx
import Image from 'next/image'

async function PostImage({ imageFilename, alt }: { imageFilename: string; alt: string }) {
  const { default: image } = await import(`../content/blog/images/${imageFilename}`)
  // image contains width, height, and blurDataURL
  return <Image src={image} alt={alt} />
}
```

```tsx
// ใช้ path alias ได้
const { default: image } = await import(`@/content/blog/images/${imageFilename}`)
```

> Path ต้องมี static prefix (เช่น `../content/blog/images/`) — ทุกไฟล์ที่ match prefix จะถูก bundle

### 3. Remote Images

```tsx
import Image from 'next/image'

export default function Page() {
  return (
    <Image
      src="https://s3.amazonaws.com/my-bucket/profile.png"
      alt="Picture of the author"
      width={500}
      height={500}
    />
  )
}
```

**ต้องระบุเอง:**
- `width` + `height` (ใช้คำนวณ aspect ratio ป้องกัน layout shift)
- หรือใช้ `fill` prop แทน (ภาพเต็ม parent element)

#### Config Remote Patterns (บังคับ)

ต้อง whitelist remote hosts ใน `next.config.ts`:

```ts
// next.config.ts
import type { NextConfig } from 'next'

const config: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 's3.amazonaws.com',
        port: '',
        pathname: '/my-bucket/**',
        search: '',
      },
      {
        protocol: 'https',
        hostname: 'cdn.example.com',
      },
      {
        protocol: 'https',
        hostname: '*.unsplash.com',
      },
    ],
  },
}

export default config
```

> ระบุให้เฉพาะเจาะจงที่สุดเพื่อป้องกัน malicious usage

### 4. `fill` Property — Responsive Images

เมื่อไม่รู้ขนาดภาพล่วงหน้า ใช้ `fill` ให้ภาพเต็ม parent:

```tsx
import Image from 'next/image'

export default function Page() {
  return (
    <div className="relative h-64 w-full">
      <Image
        src="/banner.jpg"
        alt="Banner"
        fill
        className="object-cover"
      />
    </div>
  )
}
```

**ข้อกำหนด:**
- Parent element ต้องมี `position: relative` (หรือ `absolute`/`fixed`)
- Parent ต้องมีขนาดที่กำหนด (width + height)

### 5. Sizes Property — Responsive Breakpoints

บอก browser ว่าภาพจะกว้างเท่าไหร่ในแต่ละ breakpoint:

```tsx
<Image
  src="/hero.jpg"
  alt="Hero"
  fill
  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
/>
```

**ทำไมต้องใช้ `sizes`:**
- ช่วย browser เลือก srcset ที่เหมาะสม
- ลดขนาดภาพที่โหลดบน mobile
- ปรับปรุง performance อย่างมาก

### 6. Priority — Above-the-fold Images

สำหรับภาพที่อยู่ด้านบนสุดของหน้า (LCP element):

```tsx
<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority // ปิด lazy loading, preload ทันที
/>
```

**ใช้ `priority` เมื่อ:**
- ภาพเป็น Largest Contentful Paint (LCP) element
- ภาพอยู่ above-the-fold (เห็นทันทีไม่ต้อง scroll)
- ไม่ควรใช้กับทุกภาพ — เฉพาะ 1-2 ภาพแรกของหน้า

### 7. Placeholder — Blur-up Effect

```tsx
// Static import — blur อัตโนมัติ
import heroImage from './hero.jpg'

<Image
  src={heroImage}
  alt="Hero"
  placeholder="blur" // ใช้ blurDataURL ที่สร้างอัตโนมัติ
/>
```

```tsx
// Remote image — ต้องระบุ blurDataURL เอง
<Image
  src="https://cdn.example.com/photo.jpg"
  alt="Photo"
  width={800}
  height={600}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,/9j/4AAQ..." // base64 ขนาดเล็ก
/>
```

### 8. Common Patterns

#### Card with Image

```tsx
import Image from 'next/image'

function ProductCard({ product }: { product: { image: string; name: string; price: number } }) {
  return (
    <div className="overflow-hidden rounded-lg border">
      <div className="relative aspect-square">
        <Image
          src={product.image}
          alt={product.name}
          fill
          sizes="(max-width: 768px) 50vw, 25vw"
          className="object-cover"
        />
      </div>
      <div className="p-4">
        <h3>{product.name}</h3>
        <p>${product.price}</p>
      </div>
    </div>
  )
}
```

#### Avatar

```tsx
<Image
  src={user.avatar}
  alt={user.name}
  width={40}
  height={40}
  className="rounded-full"
/>
```

#### Background Image

```tsx
<div className="relative h-screen w-full">
  <Image
    src="/background.jpg"
    alt=""
    fill
    priority
    className="object-cover -z-10"
  />
  <div className="relative z-10 flex items-center justify-center h-full">
    <h1 className="text-white text-5xl">Welcome</h1>
  </div>
</div>
```

## Quick Reference

| Prop | ใช้เมื่อ | ค่า |
|------|---------|-----|
| `src` | ทุกภาพ | string URL หรือ static import |
| `alt` | ทุกภาพ (accessibility) | string อธิบายภาพ |
| `width` + `height` | รู้ขนาดล่วงหน้า | number (pixels) |
| `fill` | ไม่รู้ขนาด / responsive | boolean |
| `sizes` | ใช้กับ `fill` หรือ responsive | media query string |
| `priority` | Above-the-fold / LCP | boolean |
| `placeholder` | Blur-up effect | `"blur"` หรือ `"empty"` |
| `quality` | ปรับคุณภาพ | 1-100 (default: 75) |
| `loading` | ควบคุม lazy loading | `"lazy"` (default) หรือ `"eager"` |

## สรุป

1. **ใช้ `<Image>` แทน `<img>` เสมอ** — ได้ optimization ฟรี
2. **Static import เมื่อทำได้** — auto width/height/blur
3. **Remote images ต้อง config `remotePatterns`** — security
4. **ใช้ `fill` + `sizes`** สำหรับ responsive images
5. **ใส่ `priority`** เฉพาะ above-the-fold images (LCP)
6. **ระบุ `alt` เสมอ** — accessibility
