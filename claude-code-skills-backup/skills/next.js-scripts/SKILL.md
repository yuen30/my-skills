---
name: Next.js Scripts
description: Expert guidance on loading and optimizing third-party scripts in Next.js — next/script strategies, inline scripts, event handlers, and web workers.
---

# Next.js Scripts

Expert guidance on loading and optimizing third-party scripts in Next.js — next/script strategies, inline scripts, event handlers, and web workers.

@doc-version: 16.2.6

## Core Concepts

`next/script` optimizes third-party script loading:
- Defers scripts ไม่ block main thread
- Loads once แม้ navigate หลาย routes
- 4 loading strategies ตาม priority
- Event handlers สำหรับ post-load logic

## Guidelines

### 1. Layout Scripts (Multiple Routes)

```tsx
// app/dashboard/layout.tsx
import Script from 'next/script'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <section>{children}</section>
      <Script src="https://example.com/script.js" />
    </>
  )
}
```

- โหลดเมื่อ user เข้า route ใน layout นี้
- โหลดครั้งเดียว แม้ navigate ระหว่าง routes

### 2. Application Scripts (All Routes)

```tsx
// app/layout.tsx
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
      <Script src="https://example.com/script.js" />
    </html>
  )
}
```

- โหลดทุก route
- โหลดครั้งเดียว

> **แนะนำ:** ใส่ scripts เฉพาะ pages/layouts ที่ต้องการ — ลด performance impact

### 3. Loading Strategies

| Strategy | When | Use Case |
|----------|------|----------|
| `beforeInteractive` | ก่อน hydration | Critical scripts (polyfills, bot detection) |
| `afterInteractive` (default) | หลัง hydration บางส่วน | Analytics, tag managers |
| `lazyOnload` | ตอน browser idle | Chat widgets, social embeds |
| `worker` (experimental) | Web worker | Heavy analytics, non-critical |

```tsx
// Critical — load before hydration
<Script src="https://example.com/polyfill.js" strategy="beforeInteractive" />

// Default — load after some hydration
<Script src="https://www.googletagmanager.com/gtag/js" strategy="afterInteractive" />

// Lazy — load during idle time
<Script src="https://connect.facebook.net/en_US/sdk.js" strategy="lazyOnload" />

// Web worker (experimental)
<Script src="https://example.com/heavy-analytics.js" strategy="worker" />
```

### 4. Event Handlers (Client Components Only)

```tsx
'use client'

import Script from 'next/script'

export default function Page() {
  return (
    <>
      <Script
        src="https://example.com/script.js"
        onLoad={() => {
          console.log('Script loaded')
        }}
        onReady={() => {
          console.log('Script ready (runs on every mount)')
        }}
        onError={(e) => {
          console.error('Script failed to load', e)
        }}
      />
    </>
  )
}
```

| Handler | When | Re-runs on navigation? |
|---------|------|:---:|
| `onLoad` | Script finished loading | ❌ Once |
| `onReady` | Script loaded + component mounted | ✅ Every mount |
| `onError` | Script failed to load | ❌ Once |

> Event handlers ต้องใช้ใน Client Components (`'use client'`)

### 5. Inline Scripts

```tsx
// With curly braces
<Script id="show-banner">
  {`document.getElementById('banner').classList.remove('hidden')`}
</Script>

// With dangerouslySetInnerHTML
<Script
  id="show-banner"
  dangerouslySetInnerHTML={{
    __html: `document.getElementById('banner').classList.remove('hidden')`,
  }}
/>
```

> **สำคัญ:** Inline scripts ต้องมี `id` prop — Next.js ใช้ track + optimize

### 6. Additional Attributes

```tsx
<Script
  src="https://example.com/script.js"
  id="example-script"
  nonce="XUENAJFW"           // CSP nonce
  data-test="script"         // Custom data attribute
  crossOrigin="anonymous"    // CORS
  referrerPolicy="no-referrer"
/>
```

Attributes ถูก forward ไปยัง `<script>` element ใน HTML

### 7. Common Use Cases

#### Google Analytics

```tsx
// app/layout.tsx
import Script from 'next/script'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
      <Script
        src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_ID}`}
        strategy="afterInteractive"
      />
      <Script id="google-analytics" strategy="afterInteractive">
        {`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${process.env.NEXT_PUBLIC_GA_ID}');
        `}
      </Script>
    </html>
  )
}
```

#### Google Tag Manager

```tsx
<Script
  src={`https://www.googletagmanager.com/gtm.js?id=${process.env.NEXT_PUBLIC_GTM_ID}`}
  strategy="afterInteractive"
/>
```

#### Chat Widget (Lazy)

```tsx
<Script
  src="https://widget.intercom.io/widget/xxx"
  strategy="lazyOnload"
/>
```

#### Third-party SDK with onReady

```tsx
'use client'

import Script from 'next/script'

export function MapComponent() {
  return (
    <>
      <div id="map" style={{ height: '400px' }} />
      <Script
        src="https://maps.googleapis.com/maps/api/js?key=xxx"
        strategy="lazyOnload"
        onReady={() => {
          new google.maps.Map(document.getElementById('map'), {
            center: { lat: 13.7563, lng: 100.5018 },
            zoom: 12,
          })
        }}
      />
    </>
  )
}
```

### 8. Web Worker Strategy (Experimental)

```js
// next.config.js
module.exports = {
  experimental: {
    nextScriptWorkers: true,
  },
}
```

```bash
npm install @qwik.dev/partytown
```

```tsx
<Script src="https://example.com/heavy-script.js" strategy="worker" />
```

- Script รันใน web worker (ไม่ block main thread)
- ใช้ Partytown
- มี trade-offs — ดู Partytown docs

## Quick Reference

| Strategy | Load Time | Block Main Thread? | Use Case |
|----------|-----------|:---:|---|
| `beforeInteractive` | Before hydration | ✅ | Polyfills, critical |
| `afterInteractive` | After partial hydration | ❌ | Analytics, GTM |
| `lazyOnload` | Browser idle | ❌ | Chat, social, non-critical |
| `worker` | Web worker | ❌ | Heavy analytics |

| Feature | Server Component | Client Component |
|---------|:---:|:---:|
| `<Script>` rendering | ✅ | ✅ |
| `onLoad` / `onReady` / `onError` | ❌ | ✅ |
| Inline scripts | ✅ | ✅ |

## สรุป

1. **ใช้ `next/script`** แทน `<script>` — optimized loading
2. **`afterInteractive`** (default) — เหมาะกับ analytics, GTM
3. **`lazyOnload`** — chat widgets, social embeds (ไม่เร่งด่วน)
4. **`beforeInteractive`** — เฉพาะ critical scripts (polyfills)
5. **Event handlers** — ต้องใช้ใน Client Components
6. **Inline scripts ต้องมี `id`** — Next.js track + optimize
7. **โหลดครั้งเดียว** — แม้ navigate หลาย routes ใน layout
8. **ใส่เฉพาะที่ต้องการ** — ลด unnecessary performance impact
