---
name: Next.js Progressive Web Apps
description: Expert guidance on building PWAs with Next.js — web app manifest, push notifications, service workers, VAPID keys, install prompts, and security.
---

# Next.js Progressive Web Apps

Expert guidance on building PWAs with Next.js — web app manifest, push notifications, service workers, VAPID keys, install prompts, and security.

@doc-version: 16.2.6

## Core Concepts

PWAs ให้ web apps มี features เหมือน native apps:
- Install ลง home screen (ไม่ต้องผ่าน app store)
- Push notifications
- Offline support (optional)
- Cross-platform จาก codebase เดียว
- Deploy updates ทันที

## Guidelines

### 1. Web App Manifest

```ts
// app/manifest.ts
import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'My Next.js PWA',
    short_name: 'MyPWA',
    description: 'A Progressive Web App built with Next.js',
    start_url: '/',
    display: 'standalone',
    background_color: '#ffffff',
    theme_color: '#000000',
    icons: [
      {
        src: '/icon-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  }
}
```

**Requirements สำหรับ installable PWA:**
- Valid web app manifest
- Served over HTTPS
- Icons (192x192 + 512x512 minimum)

### 2. Service Worker (`public/sw.js`)

```js
// public/sw.js
self.addEventListener('push', function (event) {
  if (event.data) {
    const data = event.data.json()
    const options = {
      body: data.body,
      icon: data.icon || '/icon.png',
      badge: '/badge.png',
      vibrate: [100, 50, 100],
      data: {
        dateOfArrival: Date.now(),
        primaryKey: '2',
      },
    }
    event.waitUntil(self.registration.showNotification(data.title, options))
  }
})

self.addEventListener('notificationclick', function (event) {
  event.notification.close()
  event.waitUntil(clients.openWindow('https://your-website.com'))
})
```

### 3. VAPID Keys (Push Notifications)

```bash
# Install web-push CLI
npm install -g web-push

# Generate keys
web-push generate-vapid-keys
```

```env
# .env
NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
```

### 4. Server Actions (Push Notification Backend)

```ts
// app/actions.ts
'use server'

import webpush from 'web-push'

webpush.setVapidDetails(
  'mailto:your-email@example.com',
  process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!,
  process.env.VAPID_PRIVATE_KEY!
)

let subscription: PushSubscription | null = null

export async function subscribeUser(sub: PushSubscription) {
  subscription = sub
  // Production: store in database
  // await db.subscriptions.create({ data: sub })
  return { success: true }
}

export async function unsubscribeUser() {
  subscription = null
  // Production: remove from database
  return { success: true }
}

export async function sendNotification(message: string) {
  if (!subscription) throw new Error('No subscription available')

  try {
    await webpush.sendNotification(
      subscription,
      JSON.stringify({
        title: 'Notification',
        body: message,
        icon: '/icon.png',
      })
    )
    return { success: true }
  } catch (error) {
    console.error('Error sending push notification:', error)
    return { success: false, error: 'Failed to send notification' }
  }
}
```

### 5. Push Notification Manager (Client)

```tsx
// app/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { subscribeUser, unsubscribeUser, sendNotification } from './actions'

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

export default function PushNotificationManager() {
  const [isSupported, setIsSupported] = useState(false)
  const [subscription, setSubscription] = useState<PushSubscription | null>(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      setIsSupported(true)
      registerServiceWorker()
    }
  }, [])

  async function registerServiceWorker() {
    const registration = await navigator.serviceWorker.register('/sw.js', {
      scope: '/',
      updateViaCache: 'none',
    })
    const sub = await registration.pushManager.getSubscription()
    setSubscription(sub)
  }

  async function subscribeToPush() {
    const registration = await navigator.serviceWorker.ready
    const sub = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(
        process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY!
      ),
    })
    setSubscription(sub)
    await subscribeUser(JSON.parse(JSON.stringify(sub)))
  }

  async function unsubscribeFromPush() {
    await subscription?.unsubscribe()
    setSubscription(null)
    await unsubscribeUser()
  }

  if (!isSupported) return <p>Push notifications not supported.</p>

  return (
    <div>
      {subscription ? (
        <>
          <p>Subscribed to push notifications.</p>
          <button onClick={unsubscribeFromPush}>Unsubscribe</button>
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Notification message"
          />
          <button onClick={() => sendNotification(message)}>Send Test</button>
        </>
      ) : (
        <button onClick={subscribeToPush}>Subscribe to Notifications</button>
      )}
    </div>
  )
}
```

### 6. Install Prompt

```tsx
'use client'

import { useState, useEffect } from 'react'

export function InstallPrompt() {
  const [isIOS, setIsIOS] = useState(false)
  const [isStandalone, setIsStandalone] = useState(false)

  useEffect(() => {
    setIsIOS(/iPad|iPhone|iPod/.test(navigator.userAgent))
    setIsStandalone(window.matchMedia('(display-mode: standalone)').matches)
  }, [])

  if (isStandalone) return null // Already installed

  return (
    <div>
      <h3>Install App</h3>
      {isIOS && (
        <p>
          Tap the share button ⎋ then "Add to Home Screen" ➕
        </p>
      )}
    </div>
  )
}
```

### 7. Security Headers

```js
// next.config.js
module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
        ],
      },
      {
        source: '/sw.js',
        headers: [
          { key: 'Content-Type', value: 'application/javascript; charset=utf-8' },
          { key: 'Cache-Control', value: 'no-cache, no-store, must-revalidate' },
          { key: 'Content-Security-Policy', value: "default-src 'self'; script-src 'self'" },
        ],
      },
    ]
  },
}
```

### 8. Testing Locally

```bash
# Run with HTTPS (required for service workers)
next dev --experimental-https
```

**Checklist:**
- Browser notifications enabled
- Accept permission prompt
- HTTPS (or localhost)
- If not working → try different browser

## Push Notification Browser Support

| Browser | Support |
|---------|:---:|
| Chrome (desktop + Android) | ✅ |
| Safari (macOS 13+) | ✅ |
| iOS Safari (16.4+, installed to home screen) | ✅ |
| Firefox | ✅ |
| Edge | ✅ |

## Extending PWA

| Feature | How |
|---------|-----|
| Offline support | [Serwist](https://github.com/serwist/serwist) with Next.js |
| Background sync | Service Worker Background Sync API |
| File system access | File System Access API |
| Static export | `output: 'export'` (no Server Actions) |

## Quick Reference

| File | Purpose |
|------|---------|
| `app/manifest.ts` | Web app manifest (name, icons, display) |
| `public/sw.js` | Service worker (push, notifications) |
| `app/actions.ts` | Server Actions (subscribe, send notification) |
| `.env` | VAPID keys |
| `public/icon-*.png` | App icons (192x192, 512x512) |

## สรุป

1. **Manifest** — `app/manifest.ts` กำหนด name, icons, display mode
2. **Service Worker** — `public/sw.js` handle push events + notification clicks
3. **VAPID Keys** — `web-push generate-vapid-keys` สำหรับ push notifications
4. **Server Actions** — subscribe/unsubscribe/send notifications
5. **Install prompt** — iOS instructions + `display-mode: standalone` check
6. **HTTPS required** — `next dev --experimental-https` สำหรับ local testing
7. **Security headers** — nosniff, DENY, no-cache สำหรับ sw.js
8. **Production** — store subscriptions ใน database
