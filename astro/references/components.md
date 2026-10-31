# Component Development


### Astro Component (Static)

```astro
---
// src/components/Card.astro
interface Props {
  title: string
  description: string
  href: string
  image?: ImageMetadata
}

const { title, description, href, image } = Astro.props
---

<a href={href} class="group block rounded-lg border p-4 hover:border-primary transition">
  {image && (
    <Image src={image} alt={title} class="rounded-md mb-4" width={400} height={200} />
  )}
  <h3 class="text-lg font-semibold group-hover:text-primary">{title}</h3>
  <p class="text-muted-foreground mt-1">{description}</p>
</a>
```

### Island Component (Interactive)

```tsx
// src/components/islands/SearchBar.tsx
import { useState } from 'react'

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  async function handleSearch(value: string) {
    setQuery(value)
    if (value.length < 2) return setResults([])
    const res = await fetch(`/api/search?q=${encodeURIComponent(value)}`)
    setResults(await res.json())
  }

  return (
    <div>
      <input
        type="search"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search..."
        className="w-full rounded-md border px-4 py-2"
      />
      {results.length > 0 && (
        <ul className="mt-2 rounded-md border divide-y">
          {results.map((r) => (
            <li key={r.id} className="p-2">
              <a href={r.url}>{r.title}</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
```

Usage in `.astro`:
```astro
---
import SearchBar from '../components/islands/SearchBar'
---
<SearchBar client:idle />
```

---
