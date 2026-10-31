## Dark Mode

### Vite (next-themes)

```bash
npm install next-themes
```

```tsx
// src/components/theme-provider.tsx
import { ThemeProvider as NextThemesProvider } from "next-themes"

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="system" enableSystem>
      {children}
    </NextThemesProvider>
  )
}
```

```tsx
// src/main.tsx
import { ThemeProvider } from "@/components/theme-provider"

<ThemeProvider>
  <App />
</ThemeProvider>
```
