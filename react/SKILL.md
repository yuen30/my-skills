---
name: react
description: Use for plain (non-Next.js) React development — client-rendered SPA component patterns, hooks rules, state management decisions (local state vs Context vs external store), and common hook anti-patterns. For Next.js-specific concerns (Server Components, App Router, routing, data fetching conventions), use the nextjs-* skills instead.
---

# React

Guidance for plain, client-side React (Vite SPA, CRA-style, or any non-framework React app). Server Components, streaming SSR, and the App Router are Next.js/Remix framework features, not plain React APIs — they do not apply here. If the project uses Next.js, defer to the `nextjs-*` skills in this library for anything routing/data-fetching/RSC-related; use this skill only for generic component/hook patterns.

**Precondition:** Before asserting a hook or API is available (`use()`, `useOptimistic`, `useActionState`, `useFormStatus`), verify the installed React version — these are React 19+ only.

```shell
grep '"react"' package.json
npm ls react react-dom
```

Canonical source for anything not covered below: `https://react.dev`. Training data on React APIs may be stale — verify against the docs rather than inventing hook signatures.

## Core Patterns

### Function components + hooks (the only current pattern)

Class components are legacy; do not write new ones. Only touch existing class components if already in scope for other reasons.

```tsx
function UserCard({ userId }: { userId: string }) {
  const [user, setUser] = useState<User | null>(null);
  // ...
  return <div>{user?.name}</div>;
}
```

### Rules of Hooks

- Call hooks only at the top level of a component or custom hook — never inside conditionals, loops, or nested functions.
- Custom hooks must start with `use` and may call other hooks.
- Enforce with `eslint-plugin-react-hooks` (`react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps`) — do not silence `exhaustive-deps` without understanding the missing dependency first.

### `use()` hook (React 19+)

Reads a promise or context inside render, integrates with Suspense — replaces some `useEffect` + `useState` data-loading boilerplate for values sourced from a promise passed down (e.g. from a framework loader). Confirm React 19+ before suggesting it; on 18, fall back to `useEffect`-based fetching or a data-fetching library.

```tsx
function Comments({ commentsPromise }: { commentsPromise: Promise<Comment[]> }) {
  const comments = use(commentsPromise); // suspends until resolved
  return <ul>{comments.map((c) => <li key={c.id}>{c.text}</li>)}</ul>;
}
```

### `useOptimistic` / `useActionState` / `useFormStatus` (React 19+)

Form-submission and optimistic-UI primitives. Only suggest these on confirmed React 19+; they do not exist on 18.

```tsx
function LikeButton({ initialLikes, onLike }: Props) {
  const [optimisticLikes, addOptimistic] = useOptimistic(initialLikes, (state, delta: number) => state + delta);
  return (
    <button onClick={() => { addOptimistic(1); onLike(); }}>
      {optimisticLikes} likes
    </button>
  );
}
```

## State Management Decisions

| Need | Reach for |
|---|---|
| State used by one component/subtree | `useState` / `useReducer` locally |
| State shared by a few nearby components | Lift state to the nearest common ancestor, pass as props |
| State needed by many components across the tree, changes infrequently (theme, auth user, locale) | `Context` + `useContext` |
| State needed widely, changes frequently, or needs selectors/middleware/devtools | External store (Zustand, Jotai, Redux Toolkit) — pick based on existing project convention |
| Server/remote data (fetch, cache, revalidate) | A data-fetching library (TanStack Query, SWR) rather than hand-rolled `useEffect` + `useState` |

Do not reach for Context as a default global-state solution — it re-renders every consumer on any value change and has no built-in selector mechanism. Split contexts by concern (e.g. separate `AuthContext` and `ThemeContext`) rather than one large app-wide context.

## Common Anti-Patterns to Flag

- **Unnecessary `useEffect`**: deriving state from props/state, resetting state on prop change, or event-handling logic that belongs in the event handler itself. See react.dev's "You Might Not Need an Effect." Prefer computing values directly during render (`const doubled = count * 2`), or using `key` to reset component state on prop change instead of an effect + `setState`.
- **Prop drilling** through 3+ layers of components that don't otherwise use the prop — use `Context` for cross-cutting values, or component composition (passing JSX as children/props) to avoid threading props through intermediate components that don't need them.
- **Missing/incorrect `key` props** in lists — never use array index as `key` when the list can reorder, filter, or have items inserted/removed.
- **Object/array/function literals in JSX props** without memoization causing unnecessary re-renders of memoized children — use `useMemo`/`useCallback` only when profiling shows it matters, not preemptively everywhere.
- **Mutating state directly** (`state.push(...)`, `state.foo = x`) instead of creating new references — breaks React's change detection.
- **Fetching in `useEffect` without cleanup/abort** — race conditions on fast prop changes; use a data-fetching library or an `AbortController` + ignore-flag pattern.

## Verification

```shell
npm ls react react-dom
npx eslint . --ext .tsx,.ts   # confirm react-hooks/rules-of-hooks passes
```
