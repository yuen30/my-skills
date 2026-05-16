---
name: Next.js Debugging
description: Expert guidance on debugging Next.js applications — VS Code, Chrome DevTools, Firefox DevTools, server-side and client-side debugging with source maps.
---

# Next.js Debugging

Expert guidance on debugging Next.js applications — VS Code, Chrome DevTools, Firefox DevTools, server-side and client-side debugging with source maps.

@doc-version: 16.2.6

## Core Concepts

Next.js รองรับ debugging ด้วย full source maps สำหรับทั้ง frontend และ backend code ผ่าน:
- VS Code debugger
- Chrome DevTools
- Firefox DevTools
- Jetbrains WebStorm
- ทุก debugger ที่ attach to Node.js ได้

## Guidelines

### 1. VS Code — Full Configuration

สร้างไฟล์ `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Next.js: debug server-side",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run dev -- --inspect"
    },
    {
      "name": "Next.js: debug client-side",
      "type": "chrome",
      "request": "launch",
      "url": "http://localhost:3000"
    },
    {
      "name": "Next.js: debug client-side (Firefox)",
      "type": "firefox",
      "request": "launch",
      "url": "http://localhost:3000",
      "reAttach": true,
      "pathMappings": [
        {
          "url": "webpack://_N_E",
          "path": "${workspaceFolder}"
        }
      ]
    },
    {
      "name": "Next.js: debug full stack",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/node_modules/next/dist/bin/next",
      "runtimeArgs": ["--inspect"],
      "skipFiles": ["<node_internals>/**"],
      "serverReadyAction": {
        "action": "debugWithEdge",
        "killOnServerStop": true,
        "pattern": "- Local:.+(https?://.+)",
        "uriFormat": "%s",
        "webRoot": "${workspaceFolder}"
      }
    }
  ]
}
```

**Notes:**
- Firefox: ต้องติดตั้ง [Firefox Debugger extension](https://marketplace.visualstudio.com/items?itemName=firefox-devtools.vscode-firefox-debug)
- Full stack: เปลี่ยน `debugWithEdge` เป็น `debugWithChrome` ถ้าใช้ Chrome
- Turborepo: เพิ่ม `"cwd": "${workspaceFolder}/apps/web"`
- Custom port: เปลี่ยน `3000` เป็น port ที่ใช้

**วิธีใช้:**
1. เปิด Debug panel (`Ctrl+Shift+D` / `⇧+⌘+D`)
2. เลือก configuration
3. กด `F5` หรือ **Debug: Start Debugging**

### 2. Client-side Debugging (Browser DevTools)

```bash
npm run dev
```

เปิด `http://localhost:3000` แล้ว:

**Chrome:**
- `Ctrl+Shift+J` (Windows/Linux) / `⌥+⌘+I` (macOS)
- ไปที่ **Sources** tab
- ค้นหาไฟล์: `Ctrl+P` / `⌘+P`

**Firefox:**
- `Ctrl+Shift+I` (Windows/Linux) / `⌥+⌘+I` (macOS)
- ไปที่ **Debugger** tab
- ค้นหาไฟล์: `Ctrl+P` / `⌘+P`

**Source file paths:** `webpack://_N_E/./`

#### ใช้ `debugger` Statement

```tsx
export default function Page() {
  debugger // Execution จะหยุดตรงนี้
  return <div>Debug me</div>
}
```

#### React Developer Tools

ติดตั้ง [React Developer Tools](https://react.dev/learn/react-developer-tools) extension:
- Inspect React components
- Edit props and state
- Identify performance problems

### 3. Server-side Debugging

ใช้ `--inspect` flag:

```bash
npm run dev -- --inspect

# Output:
# Debugger listening on ws://127.0.0.1:9229/...
# ready - started server on 0.0.0.0:3000
```

**Chrome:**
1. เปิด tab ใหม่ → `chrome://inspect`
2. หา Next.js app ใน **Remote Target**
3. คลิก **inspect**
4. ไปที่ **Sources** tab

**Firefox:**
1. เปิด tab ใหม่ → `about:debugging`
2. คลิก **This Firefox**
3. หา Next.js app ใน **Remote Targets**
4. คลิก **Inspect**

**Source file paths:** `webpack://{app-name}/./`

#### Remote Debugging (Docker)

```bash
npm run dev -- --inspect=0.0.0.0
```

#### Break Before Code Runs

```bash
NODE_OPTIONS=--inspect-brk next dev
# หรือ
NODE_OPTIONS=--inspect-wait next dev
```

### 4. Inspect Server Errors

เมื่อเจอ error overlay:
1. หา Node.js icon ใต้ Next.js version indicator
2. คลิก → DevTools URL ถูก copy ไป clipboard
3. เปิด tab ใหม่ด้วย URL นั้น → inspect server process

### 5. Jetbrains WebStorm

1. คลิก dropdown runtime configuration → **Edit Configurations...**
2. สร้าง **JavaScript Debug** configuration
3. URL: `http://localhost:3000`
4. Run configuration → browser เปิดอัตโนมัติ
5. ได้ 2 debug sessions: Node.js app + browser

### 6. Debugging Tips

#### Set Breakpoints in Source Files

```tsx
// ใช้ debugger statement
function handleSubmit() {
  debugger
  // code ที่ต้องการ debug
}

// หรือ set breakpoint ใน DevTools/VS Code
// คลิกที่ line number ใน Sources/Debugger tab
```

#### Debug Server Actions

```ts
'use server'

export async function createPost(formData: FormData) {
  debugger // หยุดตรงนี้เมื่อ action ถูกเรียก
  const title = formData.get('title')
  // ...
}
```

#### Debug Proxy

```ts
// proxy.ts
export function proxy(request: NextRequest) {
  debugger // หยุดตรงนี้ทุก request
  // ...
}
```

### 7. Windows — Performance Tip

> **สำคัญ:** ปิด Windows Defender real-time scanning สำหรับ project folder — มันตรวจทุกไฟล์ที่อ่าน ทำให้ Fast Refresh ช้ามาก

## Quick Reference

| Debug Target | Method |
|-------------|--------|
| Client-side (browser) | Browser DevTools → Sources/Debugger tab |
| Server-side | `--inspect` flag + `chrome://inspect` |
| Full stack (VS Code) | launch.json "debug full stack" config |
| Server Actions | `debugger` statement + `--inspect` |
| Proxy | `debugger` statement + `--inspect` |
| React components | React Developer Tools extension |

| Shortcut | Action |
|----------|--------|
| `Ctrl+P` / `⌘+P` | Search files in DevTools |
| `Ctrl+Shift+J` / `⌥+⌘+I` | Open Chrome DevTools |
| `Ctrl+Shift+D` / `⇧+⌘+D` | VS Code Debug panel |
| `F5` | Start debugging (VS Code) |
| `F9` | Toggle breakpoint (VS Code) |
| `F10` | Step over |
| `F11` | Step into |

## สรุป

1. **VS Code:** สร้าง `.vscode/launch.json` — debug ได้ทั้ง server + client + full stack
2. **Client-side:** Browser DevTools → Sources tab + `debugger` statement
3. **Server-side:** `npm run dev -- --inspect` → `chrome://inspect`
4. **Source maps:** Full support — เห็น original source code
5. **React DevTools:** ติดตั้ง extension สำหรับ component inspection
6. **Windows:** ปิด Windows Defender สำหรับ project folder
