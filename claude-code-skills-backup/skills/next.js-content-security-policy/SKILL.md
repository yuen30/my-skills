---
name: Next.js Content Security Policy
description: Expert guidance on implementing CSP in Next.js — nonces with Proxy, static CSP headers, SRI (experimental), and third-party script handling.
---

# Next.js Content Security Policy

Expert guidance on implementing CSP in Next.js — nonces with Proxy, static CSP headers, SRI (experimental), and third-party script handling.

@doc-version: 16.2.6

## Core Concepts

Content Security Policy (CSP) ป้องกัน XSS, clickjacking, และ code injection attacks โดยระบุ origins ที่อนุญาตสำหรับ scripts, styles, images, fonts, etc.

**2 แนวทางหลัก:**
- **Nonce-based** — dynamic rendering, strict security, ใช้ Proxy สร้าง nonce ทุก request
- **Without nonces** — static CSP headers ใน `next.config.js`, ใช้ `'unsafe-inline'`

## Guidelines

### 1. Nonce-based CSP (Strict)

#### Proxy Implementation

```ts
// proxy.ts
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const isDev = process.env.NODE_ENV === 'development'

  const cspHeader = `
    default-src 'self';
    script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ''};
    style-src 'self' 'nonce-${nonce}';
    img-src 'self' blob: data:;
    font-src 'self';
    object-src 'none';
    base-uri 'self';
    form-action 'self';
    frame-ancestors 'none';
    upgrade-insecure-requests;
  `

  const contentSecurityPolicyHeaderValue = cspHeader.replace(/\s{2,}/g, ' ').trim()

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-nonce', nonce)
  requestHeaders.set('Content-Security-Policy', contentSecurityPolicyHeaderValue)

  const response = NextResponse.next({
    request: { headers: requestHeaders },
  })
  response.headers.set('Content-Security-Policy', contentSecurityPolicyHeaderValue)

  return response
}

export const config = {
  matcher: [
    {
      source: '/((?!api|_next/static|_next/image|favicon.ico).*)',
      missing: [
        { type: 'header', key: 'next-router-prefetch' },
        { type: 'header', key: 'purpose', value: 'prefetch' },
      ],
    },
  ],
}
```

#### How Nonces Work in Next.js

1. **Proxy สร้าง nonce** → ใส่ใน `Content-Security-Policy` header + `x-nonce` header
2. **Next.js extract nonce** → parse จาก CSP header (`'nonce-{value}'` pattern)
3. **Nonce ถูก apply อัตโนมัติ** ไปที่:
   - Framework scripts (React, Next.js runtime)
   - Page-specific JavaScript bundles
   - Inline styles/scripts ที่ Next.js generate
   - `<Script>` components ที่ใช้ `nonce` prop

#### Force Dynamic Rendering

Nonce ต้องการ dynamic rendering — ใช้ `connection()`:

```tsx
// app/page.tsx
import { connection } from 'next/server'

export default async function Page() {
  await connection() // Force dynamic rendering
  // Page content
}
```

#### Reading the Nonce

```tsx
// app/page.tsx
import { headers } from 'next/headers'
import Script from 'next/script'

export default async function Page() {
  const nonce = (await headers()).get('x-nonce')

  return (
    <Script
      src="https://www.googletagmanager.com/gtag/js"
      strategy="afterInteractive"
      nonce={nonce}
    />
  )
}
```

#### Third-party Scripts with Nonce

```tsx
// app/layout.tsx
import { GoogleTagManager } from '@next/third-parties/google'
import { headers } from 'next/headers'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const nonce = (await headers()).get('x-nonce')

  return (
    <html lang="en">
      <body>
        {children}
        <GoogleTagManager gtmId="GTM-XYZ" nonce={nonce} />
      </body>
    </html>
  )
}
```

อัปเดต CSP ให้รองรับ third-party domains:

```ts
const cspHeader = `
  script-src 'self' 'nonce-${nonce}' 'strict-dynamic' https://www.googletagmanager.com;
  connect-src 'self' https://www.google-analytics.com;
  img-src 'self' data: https://www.google-analytics.com;
`
```

### 2. CSP Without Nonces (Static)

สำหรับแอปที่ไม่ต้องการ strict nonce — ใช้ `'unsafe-inline'`:

```js
// next.config.js
const isDev = process.env.NODE_ENV === 'development'

const cspHeader = `
  default-src 'self';
  script-src 'self' 'unsafe-inline'${isDev ? " 'unsafe-eval'" : ''};
  style-src 'self' 'unsafe-inline';
  img-src 'self' blob: data:;
  font-src 'self';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
`

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: cspHeader.replace(/\n/g, ''),
          },
        ],
      },
    ]
  },
}
```

**ข้อดี:** Static generation ยังทำงานได้, CDN cache ได้
**ข้อเสีย:** `'unsafe-inline'` อนุญาต inline scripts ทั้งหมด (less secure)

### 3. Subresource Integrity — SRI (Experimental)

Hash-based CSP ที่ยังคง static generation ได้:

```js
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    sri: {
      algorithm: 'sha256', // or 'sha384' or 'sha512'
    },
  },
}

module.exports = nextConfig
```

**SRI ทำอะไร:**
- Generate cryptographic hashes ของ JS files ตอน build
- เพิ่ม `integrity` attributes ใน script tags
- Browser verify ว่าไฟล์ไม่ถูกแก้ไขระหว่างทาง

**ข้อดีเทียบกับ nonces:**
- Static generation ยังทำงานได้
- CDN cache ได้
- Performance ดีกว่า (ไม่ต้อง SSR ทุก request)

**ข้อจำกัด:**
- Experimental — อาจเปลี่ยนหรือถูกลบ
- App Router only
- Build-time only — ไม่รองรับ dynamically generated scripts

### 4. Nonce vs No-Nonce vs SRI

| Feature | Nonce | No-Nonce | SRI (Experimental) |
|---------|:---:|:---:|:---:|
| Security level | สูงสุด | ปานกลาง | สูง |
| Static generation | ❌ | ✅ | ✅ |
| CDN caching | ❌ | ✅ | ✅ |
| Performance | ช้ากว่า (SSR ทุก request) | เร็ว | เร็ว |
| PPR compatible | ❌ | ✅ | ✅ |
| Inline scripts | เฉพาะที่มี nonce | ทั้งหมด (`unsafe-inline`) | ❌ |

#### เมื่อไหร่ใช้ Nonces:
- Strict security requirements (ห้าม `'unsafe-inline'`)
- Handle sensitive data
- ต้องอนุญาต specific inline scripts
- Compliance requirements

#### เมื่อไหร่ใช้ No-Nonce:
- Performance สำคัญกว่า
- Static pages เป็นหลัก
- ไม่มี strict compliance requirements

### 5. Development vs Production

| | Development | Production |
|---|---|---|
| `'unsafe-eval'` | ✅ ต้องใช้ (React debugging) | ❌ ไม่ต้อง |
| `'unsafe-inline'` (styles) | อาจต้องใช้ | ใช้ nonce แทน |
| Nonce | ทำงานได้ | ทำงานได้ |

### 6. Common CSP Directives

```
default-src 'self';                    # Default: เฉพาะ same origin
script-src 'self' 'nonce-xxx';         # Scripts: same origin + nonce
style-src 'self' 'nonce-xxx';          # Styles: same origin + nonce
img-src 'self' blob: data:;            # Images: same origin + blob + data URI
font-src 'self';                       # Fonts: same origin
object-src 'none';                     # Objects: block ทั้งหมด
base-uri 'self';                       # Base URL: same origin
form-action 'self';                    # Forms: submit เฉพาะ same origin
frame-ancestors 'none';                # Frames: ห้าม embed (ป้องกัน clickjacking)
upgrade-insecure-requests;             # Force HTTPS
connect-src 'self' https://api.x.com;  # Fetch/XHR: same origin + specific APIs
```

## Troubleshooting

| ปัญหา | วิธีแก้ |
|--------|---------|
| Inline styles blocked | ใช้ CSS Modules หรือ external files |
| Dynamic imports blocked | ตรวจสอบ `'strict-dynamic'` ใน script-src |
| WebAssembly blocked | เพิ่ม `'wasm-unsafe-eval'` |
| Third-party scripts blocked | เพิ่ม domain ใน script-src |
| Nonce not applied | ตรวจสอบว่า proxy runs บน route นั้น |
| Static assets blocked | ตรวจสอบ CSP allows `/_next/static/` |

## สรุป

1. **Nonce-based** — strict ที่สุด, ต้อง dynamic rendering, ใช้ Proxy
2. **Without nonces** — `'unsafe-inline'`, static generation ได้, less secure
3. **SRI (experimental)** — hash-based, static generation ได้, App Router only
4. **Development ต้อง `'unsafe-eval'`** — React debugging
5. **Next.js apply nonce อัตโนมัติ** — ไม่ต้องใส่เองทุก tag
6. **Third-party scripts** — ใช้ `nonce` prop + เพิ่ม domains ใน CSP
