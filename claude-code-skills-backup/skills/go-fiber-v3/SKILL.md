---
name: Go Fiber v3
description: Expert guidance on Go Fiber v3 — migration from v2, new Binding system, Context interface, route chaining, domain routing, client package, services, and middleware changes.
---

# Go Fiber v3

Expert guidance on Go Fiber v3 — migration from v2, new Binding system, Context interface, route chaining, domain routing, client package, services, and middleware changes.

## Requirements

- **Go 1.25+** required
- Migration CLI: `fiber migrate --to v3`

## ⚠️ Strict Rules — ALWAYS Follow in v3

These rules are NON-NEGOTIABLE. Violating them produces v2 code that will NOT compile or will cause concurrency bugs.

### Rule 1: Context is an INTERFACE — Never use pointer `*fiber.Ctx`

```go
// ✅ CORRECT (v3) — interface, no pointer
func handler(c fiber.Ctx) error {
    return c.SendString("Hello")
}

// ❌ WRONG (v2 pattern) — WILL NOT COMPILE in v3
func handler(c *fiber.Ctx) error {
    return c.SendString("Hello")
}
```

**Why:** v3 เปลี่ยน `Ctx` เป็น interface เพื่อ:
- แก้ปัญหา concurrency (Ctx ถูก pool/reuse ใน v2 ทำให้เกิด race condition)
- รองรับ Custom Context (embed `fiber.Ctx` interface ใน struct ของคุณได้)
- Type-safe middleware data access ผ่าน generics

### Rule 2: Use Bind() — Never use deprecated Parsers

```go
// ✅ CORRECT (v3)
c.Bind().Body(&body)
c.Bind().Query(&query)
c.Bind().URI(&params)

// ❌ WRONG (v2 pattern) — REMOVED in v3
c.BodyParser(&body)
c.QueryParser(&query)
c.ParamsParser(&params)
```

### Rule 3: Use FromContext() — Never use string-key Locals

```go
// ✅ CORRECT (v3) — type-safe
reqID := requestid.FromContext(c)
sess := session.FromContext(c)

// ❌ WRONG (v2 pattern) — unsafe, collision-prone
reqID := c.Locals("requestid").(string)
sess := c.Locals("session").(*session.Session)
```

### Rule 4: Session must be Released

```go
// ✅ CORRECT (v3) — always release
func handler(c fiber.Ctx) error {
    sess := session.FromContext(c)
    defer sess.Release()  // REQUIRED — return to pool
    
    sess.Set("user", "john")
    return c.SendString("OK")
}

// ❌ WRONG — memory leak, pool exhaustion
func handler(c fiber.Ctx) error {
    sess := session.FromContext(c)
    // Missing Release()!
    sess.Set("user", "john")
    return c.SendString("OK")
}
```

### Rule 5: Custom Context Pattern

```go
// ✅ v3 Custom Context — embed the interface
type CustomCtx struct {
    fiber.Ctx  // Embed interface
    user *User
}

func NewCustomCtx(c fiber.Ctx) *CustomCtx {
    return &CustomCtx{Ctx: c}
}

// Use in app
app := fiber.New(fiber.Config{
    NewCtx: func(app *fiber.App) fiber.Ctx {
        return &CustomCtx{}
    },
})
```

## Key Changes

### 1. App & Router

#### Unified Listen

```go
// v3 — ListenConfig รวมทุกอย่างไว้ที่เดียว
app.Listen(fiber.ListenConfig{
    Addr:              ":3000",
    EnablePrefork:     true,
    CertFile:          "./cert.pem",
    KeyFile:           "./key.pem",
    GracefulShutdown:  true,
})
```

#### Standard Library Support

```go
// รับ net/http Handler ได้โดยตรง
app.Use(fiber.FromHTTPHandler(httpMiddleware))

// รับ fasthttp Handler ได้โดยตรง
app.Use(fiber.FromFasthttpHandler(fasthttpHandler))
```

#### Route Chaining (Express-style)

```go
app.RouteChain("/api/users").
    Get(getUsers).
    Post(createUser).
    Put(updateUser).
    Delete(deleteUser)
```

#### Domain Routing

```go
// แยก routes ตาม hostname
api := app.Domain("api.example.com")
api.Get("/users", getUsers)

web := app.Domain("www.example.com")
web.Get("/", renderHomePage)
```

#### Automatic HEAD

เมื่อสร้าง `GET` route → `HEAD` route ถูกสร้างอัตโนมัติ

### 2. Context — จุดที่ต้องแก้โค้ดเยอะที่สุด

#### Pointer → Interface

```go
// ❌ v2 — pointer
func handler(c *fiber.Ctx) error {
    return c.SendString("Hello")
}

// ✅ v3 — interface (ไม่มี *)
func handler(c fiber.Ctx) error {
    return c.SendString("Hello")
}
```

#### New Binding System

```go
// ❌ v2 — BodyParser, QueryParser, ParamsParser (ยกเลิกแล้ว)
c.BodyParser(&body)
c.QueryParser(&query)
c.ParamsParser(&params)

// ✅ v3 — Unified Bind
c.Bind().Body(&body)
c.Bind().Query(&query)
c.Bind().URI(&params)
c.Bind().Header(&headers)
c.Bind().Cookie(&cookies)

// Multiple sources พร้อมกัน
c.Bind().Body(&data).Query(&data)
```

#### Binary Format Support

```go
// CBOR
c.Bind().CBOR(&data)
c.CBOR(response)

// MsgPack
c.Bind().MsgPack(&data)
c.MsgPack(response)
```

### 3. Middleware Data Access — FromContext

```go
// ❌ v2 — String keys (unsafe, collision-prone)
reqID := c.Locals("requestid").(string)
sess := c.Locals("session").(*session.Session)

// ✅ v3 — Type-safe FromContext functions
reqID := requestid.FromContext(c)
sess := session.FromContext(c)
user := jwtware.FromContext(c)
```

**ข้อดี:**
- Type-safe (ไม่ต้อง type assertion)
- ไม่มี key collision
- IDE autocomplete ทำงานได้

### 4. Client Package (Rebuilt)

```go
// v3 — New HTTP Client
client := fiber.AcquireClient()
defer fiber.ReleaseClient(client)

// Base URL
client.SetBaseURL("https://api.example.com")

// Cookie Jar
client.SetCookieJar(jar)

// Hooks
client.AddRequestHook(func(c *fiber.Client, req *fiber.Request) error {
    req.Header("Authorization", "Bearer "+token)
    return nil
})

// Request
resp, err := client.Get("/users")
```

**ฟีเจอร์ใหม่:**
- Cookie Jar (auto-manage cookies)
- Request/Response Hooks
- Base URL configuration
- Improved error handling

### 5. Services

```go
// จัดการ external services (DB, Redis, etc.)
app := fiber.New()

// Register service — start/stop พร้อมกับ app
app.RegisterService(&fiber.ServiceConfig{
    Name: "database",
    Start: func() error {
        return db.Connect()
    },
    Stop: func() error {
        return db.Close()
    },
})

app.RegisterService(&fiber.ServiceConfig{
    Name: "redis",
    Start: func() error {
        return redis.Connect()
    },
    Stop: func() error {
        return redis.Close()
    },
})
```

### 6. Retry Addon

```go
import "github.com/gofiber/fiber/v3/addon/retry"

// Exponential backoff retry
result, err := retry.Do(func() error {
    resp, err := client.Get("/api/data")
    if err != nil {
        return err
    }
    if resp.StatusCode() >= 500 {
        return fmt.Errorf("server error: %d", resp.StatusCode())
    }
    return nil
}, retry.Config{
    MaxAttempts: 5,
    InitialDelay: 100 * time.Millisecond,
    MaxDelay: 5 * time.Second,
    Multiplier: 2.0,
})
```

### 7. Middleware Changes

#### Adaptor — 40-50% Faster

```go
// ใช้เหมือนเดิม แต่เร็วขึ้นมาก
app.Use(adaptor.HTTPMiddleware(httpMiddleware))
```

#### BasicAuth — Hash Required

```go
// ❌ v2 — plaintext password (ไม่ปลอดภัย)
app.Use(basicauth.New(basicauth.Config{
    Users: map[string]string{
        "admin": "password123",
    },
}))

// ✅ v3 — hashed password only
app.Use(basicauth.New(basicauth.Config{
    Users: map[string]string{
        "admin": "$2a$10$...", // bcrypt hash
    },
    Realm: "Restricted",
}))
```

#### Timeout — Abandon Mechanism

```go
// v3 — เมื่อ timeout, server คืนทรัพยากรทันที
app.Use(timeout.New(func(c fiber.Ctx) error {
    // Long-running operation
    result := heavyComputation()
    return c.JSON(result)
}, 5*time.Second))
// ถ้าเกิน 5s → response 408 ทันที ไม่รอ handler จบ
```

#### Session — Manual Release

```go
// v3 — ต้อง Release() เอง
func handler(c fiber.Ctx) error {
    sess := session.FromContext(c)
    defer sess.Release() // คืนทรัพยากรเข้า Pool

    sess.Set("user", "john")
    return c.SendString("OK")
}
```

## Migration Guide

### Step 1: Use CLI

```bash
fiber migrate --to v3
```

### Step 2: Fix Context (Most Common)

Find & replace ทั้ง project:
- `*fiber.Ctx` → `fiber.Ctx`
- `c.BodyParser(` → `c.Bind().Body(`
- `c.QueryParser(` → `c.Bind().Query(`
- `c.ParamsParser(` → `c.Bind().URI(`

### Step 3: Fix Middleware Access

```go
// Replace c.Locals("key") with FromContext
c.Locals("requestid") → requestid.FromContext(c)
c.Locals("session")   → session.FromContext(c)
```

### Step 4: Fix Session

เพิ่ม `defer sess.Release()` ทุกที่ที่ใช้ session

### Step 5: Fix BasicAuth

Hash passwords ด้วย bcrypt ก่อนใส่ config

## Quick Reference

| v2 | v3 |
|----|-----|
| `*fiber.Ctx` | `fiber.Ctx` (interface) |
| `c.BodyParser(&s)` | `c.Bind().Body(&s)` |
| `c.QueryParser(&s)` | `c.Bind().Query(&s)` |
| `c.ParamsParser(&s)` | `c.Bind().URI(&s)` |
| `c.Locals("requestid")` | `requestid.FromContext(c)` |
| `c.Locals("session")` | `session.FromContext(c)` |
| `app.Listen(":3000")` | `app.Listen(fiber.ListenConfig{Addr: ":3000"})` |
| Plaintext passwords | Hashed passwords only |
| Session auto-release | `sess.Release()` required |

## สรุป

1. **Go 1.25+** required — `fiber migrate --to v3` สำหรับ auto-migration
2. **Context = interface** — ลบ `*` ออกจาก `*fiber.Ctx`
3. **Binding ใหม่** — `c.Bind().Body()` / `.Query()` / `.URI()` แทน Parser
4. **FromContext** — type-safe middleware data access (ไม่ใช่ string keys)
5. **Route Chaining** — Express-style `.Get().Post().Put()`
6. **Domain Routing** — แยก routes ตาม hostname
7. **Client rebuilt** — Cookie Jar, Hooks, Base URL
8. **Services** — start/stop external services พร้อม app
9. **Retry Addon** — exponential backoff built-in
10. **BasicAuth** — hashed passwords only (ไม่รับ plaintext)
11. **Session** — ต้อง `Release()` เอง
12. **Timeout** — abandon mechanism (คืนทรัพยากรทันที)
