---
name: Next.js Custom Server
description: Expert guidance on setting up a custom Next.js server for programmatic control — when to use, configuration options, and integration with existing backends.
---

# Next.js Custom Server

Expert guidance on setting up a custom Next.js server for programmatic control — when to use, configuration options, and integration with existing backends.

@doc-version: 16.2.6

## Core Concepts

Custom server ให้คุณ start Next.js programmatically สำหรับ custom patterns ที่ built-in router ไม่รองรับ

> **ส่วนใหญ่ไม่จำเป็นต้องใช้** — ใช้เมื่อ integrated router ไม่ตอบโจทย์เท่านั้น

**Trade-offs:**
- ❌ สูญเสีย Automatic Static Optimization
- ❌ ใช้ร่วมกับ `output: 'standalone'` ไม่ได้
- ❌ ไม่ผ่าน Next.js Compiler/bundling

## Guidelines

### 1. Basic Custom Server

```ts
// server.ts
import { createServer } from 'http'
import next from 'next'

const port = parseInt(process.env.PORT || '3000', 10)
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  createServer((req, res) => {
    handle(req, res)
  }).listen(port)

  console.log(
    `> Server listening at http://localhost:${port} as ${
      dev ? 'development' : process.env.NODE_ENV
    }`
  )
})
```

### 2. Package.json Scripts

```json
{
  "scripts": {
    "dev": "node server.js",
    "build": "next build",
    "start": "NODE_ENV=production node server.js"
  }
}
```

### 3. `next()` Options

```ts
import next from 'next'

const app = next({
  dev: process.env.NODE_ENV !== 'production',  // Dev mode
  dir: '.',                                     // Project directory
  conf: {},                                     // next.config.js overrides
  quiet: false,                                 // Hide server info errors
  hostname: 'localhost',                        // Hostname
  port: 3000,                                   // Port
  httpServer: server,                           // Existing HTTP server
  turbopack: true,                              // Enable Turbopack (default)
  webpack: false,                               // Enable webpack instead
})
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `dev` | Boolean | `false` | Dev mode |
| `dir` | String | `'.'` | Project location |
| `conf` | Object | `{}` | next.config.js overrides |
| `quiet` | Boolean | `false` | Hide error messages |
| `hostname` | String | — | Hostname server runs behind |
| `port` | Number | — | Port server runs behind |
| `httpServer` | http.Server | — | Existing HTTP server |
| `turbopack` | Boolean | `true` | Enable Turbopack |
| `webpack` | Boolean | — | Enable webpack |

### 4. With Express

```ts
// server.ts
import express from 'express'
import next from 'next'

const port = parseInt(process.env.PORT || '3000', 10)
const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const server = express()

  // Custom API routes
  server.get('/api/custom', (req, res) => {
    res.json({ message: 'Custom API' })
  })

  // WebSocket or custom logic
  server.get('/custom-route', (req, res) => {
    // Custom handling
    return app.render(req, res, '/custom-page', req.query)
  })

  // Let Next.js handle everything else
  server.all('*', (req, res) => {
    return handle(req, res)
  })

  server.listen(port, () => {
    console.log(`> Ready on http://localhost:${port}`)
  })
})
```

### 5. With Existing HTTP Server

```ts
// server.ts
import { createServer } from 'http'
import next from 'next'

const dev = process.env.NODE_ENV !== 'production'
const httpServer = createServer()

const app = next({
  dev,
  httpServer, // Pass existing server
})

const handle = app.getRequestHandler()

app.prepare().then(() => {
  httpServer.on('request', (req, res) => {
    handle(req, res)
  })

  httpServer.listen(3000, () => {
    console.log('> Ready on http://localhost:3000')
  })
})
```

### 6. With WebSocket (Socket.io)

```ts
// server.ts
import { createServer } from 'http'
import { Server } from 'socket.io'
import next from 'next'

const dev = process.env.NODE_ENV !== 'production'
const app = next({ dev })
const handle = app.getRequestHandler()

app.prepare().then(() => {
  const httpServer = createServer((req, res) => {
    handle(req, res)
  })

  const io = new Server(httpServer)

  io.on('connection', (socket) => {
    console.log('Client connected')
    socket.on('message', (data) => {
      io.emit('message', data)
    })
  })

  httpServer.listen(3000, () => {
    console.log('> Ready on http://localhost:3000')
  })
})
```

## When to Use Custom Server

**ใช้เมื่อ:**
- ต้องการ WebSocket support (Socket.io, ws)
- ต้อง integrate กับ existing Express/Fastify/Koa server
- ต้องการ custom request handling ที่ Proxy ทำไม่ได้
- ต้องการ programmatic control เหนือ server lifecycle

**ไม่ควรใช้เมื่อ:**
- ต้องการแค่ API routes → ใช้ Route Handlers
- ต้องการ request interception → ใช้ Proxy
- ต้องการ redirects/rewrites → ใช้ next.config.js
- ต้องการ deploy บน serverless/edge

## Important Notes

- `server.js` **ไม่ผ่าน** Next.js Compiler — ต้องใช้ syntax ที่ Node.js version ปัจจุบันรองรับ
- **ไม่ใช้ร่วมกับ** `output: 'standalone'` ได้ (standalone สร้าง `server.js` ของตัวเอง)
- **สูญเสีย** Automatic Static Optimization
- ใช้ `nodemon` สำหรับ auto-restart ตอน dev

## Quick Reference

| Approach | Use Case | Performance |
|----------|----------|:-:|
| `next start` (default) | ส่วนใหญ่ | ✅ Best |
| Custom server | WebSocket, existing backend | ⚠️ ลด optimization |
| `output: 'standalone'` | Docker/containerized | ✅ Good |
| Route Handlers | API endpoints | ✅ Best |
| Proxy | Request interception | ✅ Best |

## สรุป

1. **ส่วนใหญ่ไม่จำเป็น** — ใช้ Route Handlers + Proxy แทน
2. **ใช้เมื่อ** ต้องการ WebSocket หรือ integrate กับ existing server
3. **Trade-off:** สูญเสีย Automatic Static Optimization
4. **ไม่ใช้ร่วมกับ** `output: 'standalone'`
5. **`server.js` ไม่ผ่าน bundler** — ต้อง compatible กับ Node.js version
6. **อัปเดต scripts** ใน package.json ให้ใช้ `node server.js`
