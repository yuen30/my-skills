---
name: Next.js Analytics
description: Expert guidance on adding analytics to Next.js — Web Vitals, useReportWebVitals, client instrumentation, and sending metrics to external services.
---

# Next.js Analytics

Expert guidance on adding analytics to Next.js — Web Vitals, useReportWebVitals, client instrumentation, and sending metrics to external services.

@doc-version: 16.2.6

## Core Concepts

Next.js มี built-in support สำหรับ measuring และ reporting performance metrics:
- **`useReportWebVitals`** hook — จัดการ reporting เอง
- **Client Instrumentation** — `instrumentation-client.ts` สำหรับ global analytics setup
- **Vercel Analytics** — managed service (auto collect + visualize)

## Guidelines

### 1. Client Instrumentation (`instrumentation-client.ts`)

สำหรับ advanced analytics — รันก่อน frontend code เริ่มทำงาน:

```ts
// instrumentation-client.ts (project root)

// Initialize analytics before the app starts
console.log('Analytics initialized')

// Set up global error tracking
window.addEventListener('error', (event) => {
  reportError(event.error)
})

// Example: Initialize third-party analytics
// posthog.init('phc_xxx', { api_host: 'https://app.posthog.com' })
```

**ใช้สำหรับ:**
- Global analytics initialization
- Error tracking setup
- Performance monitoring tools
- Third-party SDK initialization

### 2. Web Vitals with `useReportWebVitals`

#### Setup

```tsx
// app/_components/web-vitals.tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    console.log(metric)
  })

  return null
}
```

```tsx
// app/layout.tsx
import { WebVitals } from './_components/web-vitals'

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <WebVitals />
        {children}
      </body>
    </html>
  )
}
```

> แยก `WebVitals` เป็น component ต่างหาก — confine client boundary เฉพาะ component นี้

#### Handle Specific Metrics

```tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    switch (metric.name) {
      case 'FCP':
        // First Contentful Paint
        break
      case 'LCP':
        // Largest Contentful Paint
        break
      case 'CLS':
        // Cumulative Layout Shift
        break
      case 'INP':
        // Interaction to Next Paint
        break
      case 'FID':
        // First Input Delay
        break
      case 'TTFB':
        // Time to First Byte
        break
    }
  })

  return null
}
```

### 3. Web Vitals Metrics

| Metric | Full Name | วัดอะไร |
|--------|-----------|---------|
| TTFB | Time to First Byte | เวลาที่ server ตอบกลับ byte แรก |
| FCP | First Contentful Paint | เวลาที่ content แรกปรากฏบนหน้าจอ |
| LCP | Largest Contentful Paint | เวลาที่ content ใหญ่ที่สุดปรากฏ |
| FID | First Input Delay | เวลาตอบสนองต่อ interaction แรก |
| CLS | Cumulative Layout Shift | ความเสถียรของ layout (ไม่กระโดด) |
| INP | Interaction to Next Paint | เวลาตอบสนองต่อ interactions ทั้งหมด |

### 4. Sending to External Systems

#### Generic Endpoint

```tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    const body = JSON.stringify(metric)
    const url = 'https://example.com/analytics'

    // Use sendBeacon if available (reliable even on page unload)
    if (navigator.sendBeacon) {
      navigator.sendBeacon(url, body)
    } else {
      fetch(url, { body, method: 'POST', keepalive: true })
    }
  })

  return null
}
```

#### Google Analytics

```tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    window.gtag('event', metric.name, {
      value: Math.round(
        metric.name === 'CLS' ? metric.value * 1000 : metric.value
      ), // values must be integers
      event_label: metric.id, // id unique to current page load
      non_interaction: true,  // avoids affecting bounce rate
    })
  })

  return null
}
```

#### PostHog

```tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'
import posthog from 'posthog-js'

export function WebVitals() {
  useReportWebVitals((metric) => {
    posthog.capture('web_vital', {
      metric_name: metric.name,
      metric_value: metric.value,
      metric_id: metric.id,
      metric_rating: metric.rating, // 'good' | 'needs-improvement' | 'poor'
    })
  })

  return null
}
```

#### Custom Analytics API Route

```tsx
// app/_components/web-vitals.tsx
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    fetch('/api/analytics', {
      method: 'POST',
      body: JSON.stringify({
        name: metric.name,
        value: metric.value,
        id: metric.id,
        rating: metric.rating,
        navigationType: metric.navigationType,
        timestamp: Date.now(),
      }),
      keepalive: true,
    })
  })

  return null
}
```

```tsx
// app/api/analytics/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  const metric = await request.json()

  // Store in database, send to analytics service, etc.
  await db.webVitals.create({ data: metric })

  return NextResponse.json({ success: true })
}
```

### 5. Metric Object Shape

```ts
interface Metric {
  id: string           // Unique ID for current page load
  name: string         // 'FCP' | 'LCP' | 'CLS' | 'INP' | 'FID' | 'TTFB'
  value: number        // Metric value (ms for timing, score for CLS)
  rating: string       // 'good' | 'needs-improvement' | 'poor'
  navigationType: string // 'navigate' | 'reload' | 'back-forward' | etc.
  delta: number        // Difference from previous report
  entries: PerformanceEntry[] // Related performance entries
}
```

### 6. Vercel Analytics (Managed)

ถ้า deploy บน Vercel — ใช้ managed service:

```bash
npm install @vercel/analytics
```

```tsx
// app/layout.tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

- Auto collect Web Vitals
- Dashboard visualization
- ไม่ต้อง setup เพิ่ม

## Quick Reference

| วิธี | ใช้เมื่อ |
|------|---------|
| `useReportWebVitals` | Custom analytics, ส่งไป external service |
| `instrumentation-client.ts` | Global setup (error tracking, SDK init) |
| Vercel Analytics | Deploy บน Vercel, ต้องการ managed solution |
| `navigator.sendBeacon` | ส่ง data แม้ user ปิดหน้า (reliable) |

## สรุป

1. **`useReportWebVitals`** — hook สำหรับ report Web Vitals (แยกเป็น Client Component)
2. **`instrumentation-client.ts`** — global analytics/error tracking setup
3. **Web Vitals:** TTFB, FCP, LCP, FID, CLS, INP
4. **ใช้ `navigator.sendBeacon`** — reliable แม้ user ปิดหน้า
5. **Vercel Analytics** — managed solution ถ้า deploy บน Vercel
6. **แยก WebVitals component** — confine client boundary ให้เล็กที่สุด
