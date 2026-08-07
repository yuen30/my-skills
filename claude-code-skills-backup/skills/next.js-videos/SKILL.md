---
name: Next.js Videos
description: Expert guidance on using and optimizing videos in Next.js — self-hosted, external embeds, streaming with Suspense, accessibility, and performance.
---

# Next.js Videos

Expert guidance on using and optimizing videos in Next.js — self-hosted, external embeds, streaming with Suspense, accessibility, and performance.

@doc-version: 16.2.6

## Core Concepts

Videos ใน Next.js ใช้ 2 วิธีหลัก:
- **`<video>`** — self-hosted / direct files (full control)
- **`<iframe>`** — external platforms (YouTube, Vimeo)

## Guidelines

### 1. Self-hosted Video (`<video>`)

```tsx
export function Video() {
  return (
    <video width="320" height="240" controls preload="none">
      <source src="/path/to/video.mp4" type="video/mp4" />
      <track
        src="/path/to/captions.vtt"
        kind="subtitles"
        srcLang="en"
        label="English"
      />
      Your browser does not support the video tag.
    </video>
  )
}
```

#### Common Attributes

| Attribute | Description | Tip |
|-----------|-------------|-----|
| `src` | Video file source | Use CDN URL for performance |
| `controls` | Show playback controls | Always include for accessibility |
| `preload` | `none` / `metadata` / `auto` | Use `none` to save bandwidth |
| `autoPlay` | Auto-start playback | Must pair with `muted` |
| `muted` | Mute audio | Required for autoPlay in most browsers |
| `loop` | Loop playback | Background videos |
| `playsInline` | Inline playback on iOS | Required for iOS autoPlay |
| `poster` | Thumbnail before play | Improve perceived performance |

#### Autoplay Pattern (Background Video)

```tsx
export function BackgroundVideo() {
  return (
    <video
      autoPlay
      muted
      loop
      playsInline
      className="absolute inset-0 w-full h-full object-cover -z-10"
    >
      <source src="/hero-bg.mp4" type="video/mp4" />
    </video>
  )
}
```

### 2. External Video (`<iframe>`)

```tsx
export default function Page() {
  return (
    <iframe
      src="https://www.youtube.com/embed/19g66ezsKAg"
      width="560"
      height="315"
      allowFullScreen
      loading="lazy"
      title="Video title for accessibility"
    />
  )
}
```

#### Responsive iframe

```tsx
export function ResponsiveVideo({ src }: { src: string }) {
  return (
    <div className="relative w-full aspect-video">
      <iframe
        src={src}
        className="absolute inset-0 w-full h-full"
        allowFullScreen
        loading="lazy"
        title="Embedded video"
      />
    </div>
  )
}
```

### 3. Streaming Video Component with Suspense

```tsx
// app/ui/video-component.tsx
export default async function VideoComponent() {
  const src = await getVideoSrc() // Fetch from CMS/API
  return (
    <video controls preload="none" aria-label="Video player">
      <source src={src} type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  )
}
```

```tsx
// app/page.tsx
import { Suspense } from 'react'
import VideoComponent from './ui/video-component'
import VideoSkeleton from './ui/video-skeleton'

export default function Page() {
  return (
    <section>
      <Suspense fallback={<VideoSkeleton />}>
        <VideoComponent />
      </Suspense>
    </section>
  )
}
```

```tsx
// app/ui/video-skeleton.tsx
export default function VideoSkeleton() {
  return (
    <div className="aspect-video w-full bg-gray-200 animate-pulse rounded-lg" />
  )
}
```

### 4. Self-hosted with Vercel Blob

```tsx
import { Suspense } from 'react'
import { list } from '@vercel/blob'

export default function Page() {
  return (
    <Suspense fallback={<p>Loading video...</p>}>
      <VideoComponent fileName="my-video.mp4" />
    </Suspense>
  )
}

async function VideoComponent({ fileName }: { fileName: string }) {
  const { blobs } = await list({ prefix: fileName, limit: 1 })
  const { url } = blobs[0]

  return (
    <video controls preload="none" aria-label="Video player">
      <source src={url} type="video/mp4" />
      Your browser does not support the video tag.
    </video>
  )
}
```

### 5. Subtitles and Captions

```tsx
<video controls preload="none" aria-label="Video player">
  <source src={videoUrl} type="video/mp4" />
  <track src={captionsUrl} kind="subtitles" srcLang="en" label="English" />
  <track src={thaiCaptionsUrl} kind="subtitles" srcLang="th" label="ไทย" />
  Your browser does not support the video tag.
</video>
```

### 6. Choosing Embedding Method

| Method | Use Case | Control |
|--------|----------|:---:|
| `<video>` (self-hosted) | Full control, custom player, background video | สูง |
| `<iframe>` (YouTube/Vimeo) | Easy embed, platform features, analytics | ต่ำ |
| `next-video` (open source) | Best of both, multiple hosting backends | ปานกลาง |

## Performance Best Practices

### Video Optimization

```
□ Compress with FFmpeg before upload
□ Use MP4 (compatibility) or WebM (smaller, web-optimized)
□ Adjust resolution/bitrate for target devices
□ Use preload="none" (save bandwidth)
□ Lazy load iframes (loading="lazy")
□ Use CDN for delivery
□ Add poster image (perceived performance)
```

### FFmpeg Compression

```bash
# Compress video for web
ffmpeg -i input.mp4 -vcodec h264 -acodec aac -crf 23 -preset medium output.mp4

# Create WebM version
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 output.webm

# Generate poster image
ffmpeg -i input.mp4 -ss 00:00:01 -frames:v 1 poster.jpg
```

### Multiple Sources (Format Fallback)

```tsx
<video controls preload="none">
  <source src="/video.webm" type="video/webm" />
  <source src="/video.mp4" type="video/mp4" />
  Your browser does not support the video tag.
</video>
```

## Accessibility

```
□ Always include controls attribute
□ Add subtitles/captions (<track>)
□ Include aria-label on <video>
□ Include title on <iframe>
□ Provide fallback content inside <video> tag
□ Don't autoplay with sound (use muted)
□ Provide text alternative for video content
```

## Video Platforms for Next.js

| Platform | Features |
|----------|----------|
| [next-video](https://next-video.dev) | Open source, multiple backends (Blob, S3, Mux) |
| [Cloudinary](https://next.cloudinary.dev) | `<CldVideoPlayer>`, adaptive bitrate |
| [Mux](https://www.mux.com/for/nextjs) | High-performance video API |
| [Vercel Blob](https://vercel.com/docs/storage/vercel-blob) | Simple storage, CDN included |
| [ImageKit](https://imagekit.io/docs/integration/nextjs) | `<IKVideo>` component |

## Quick Reference

| Pattern | When |
|---------|------|
| `<video>` + `preload="none"` | Self-hosted, save bandwidth |
| `<video autoPlay muted loop playsInline>` | Background video |
| `<iframe loading="lazy">` | External embed (YouTube) |
| Suspense + Server Component | Fetch video URL from API/CMS |
| `aspect-video` (Tailwind) | Responsive video container |
| `<track>` | Subtitles/captions |

## สรุป

1. **Self-hosted:** `<video>` + `preload="none"` + `controls`
2. **External:** `<iframe>` + `loading="lazy"` + `title`
3. **Streaming:** Suspense + Server Component สำหรับ async video URLs
4. **Autoplay:** ต้อง `muted` + `playsInline` (iOS)
5. **Accessibility:** captions, controls, aria-label, fallback content
6. **Performance:** compress (FFmpeg), CDN, poster image, lazy load
7. **Responsive:** `aspect-video` class หรือ CSS aspect-ratio
