Read when installing shadcn/ui in a new framework project (Next.js, Vite, TanStack Router).

## Installation

### Vite + React + TypeScript (Recommended)

```bash
# 1. Create project
npm create vite@latest my-app -- --template react-ts

# 2. Add Tailwind CSS
npm install tailwindcss @tailwindcss/vite

# 3. Configure vite.config.ts
```

```ts
// vite.config.ts
import path from "path"
import tailwindcss from "@tailwindcss/vite"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

```json
// tsconfig.json — add paths
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

```bash
# 4. Initialize shadcn/ui
npx shadcn@latest init

# 5. Add components
npx shadcn@latest add button card
```

### Next.js (App Router)

```bash
npx shadcn@latest init
# Select: New York style, Neutral base color, CSS variables: Yes
```

### TanStack Router

```bash
npx create-tsrouter-app@latest my-app --template file-router --tailwind --add-ons shadcn
```
