---
name: angular
description: Use when developing Angular applications — standalone components, signals, new control-flow syntax, dependency injection with inject(), and deciding old (NgModule/RxJS-heavy/*ngIf) vs new (standalone/signals/@if) patterns across versions. Detect the installed version before asserting API availability.
---

# Angular

Angular ships a new major roughly every 6 months and has changed its idiomatic component/state/DI patterns significantly since v14. Training-data knowledge of Angular is likely stale — always verify against the installed version and `https://angular.dev` (the canonical, current doc source) before asserting a pattern is available or "current."

**Precondition — do not skip:** Before giving version-specific guidance (e.g. "use signals," "use `@if`"), detect the installed version first.

## Detect Version & Derive Guidance

### Step 1: Detect the installed Angular version

```shell
ng version                              # CLI + all @angular/* package versions
grep '"@angular/core"' package.json     # version constraint, not necessarily what's resolved
npm ls @angular/core                    # actually resolved version
```

Note the detected **major version**. Signals became stable in v17 (Angular Signals) with further stabilization (`linkedSignal`, `resource`) in v19; standalone-by-default is v19+; zoneless change detection is developer-preview from v18, more stable in v19/v20.

### Step 2: Verify against canonical docs

Canonical source: `https://angular.dev` (this replaced `angular.io` as the primary docs site). For anything not covered below, or if a pattern seems unavailable in the detected version, read the docs there rather than inventing an API from memory — do not guess signal/control-flow API shapes.

## Idiomatic Patterns (current as of Angular 18/19-era — verify before relying on)

### Standalone components (default since v19, available since v14)

No `NgModule` needed. Import dependencies directly on the component:

```ts
@Component({
  selector: 'app-user-card',
  standalone: true, // implicit default in v19+, explicit flag harmless on older versions
  imports: [CommonModule, RouterLink],
  templateUrl: './user-card.component.html',
})
export class UserCardComponent {}
```

If the project still has `NgModule`-declared components and `bootstrapModule`, treat it as a legacy pattern — do not force a migration mid-task unless asked; follow existing project convention.

### Signals for state (stable since v17)

Prefer signals over plain class fields + manual `ChangeDetectorRef` calls, and over RxJS `BehaviorSubject` for simple synchronous component state:

```ts
export class CounterComponent {
  count = signal(0);
  doubled = computed(() => this.count() * 2);

  increment() {
    this.count.update((v) => v + 1);
  }
}
```

```html
<p>{{ count() }} / doubled: {{ doubled() }}</p>
```

- `signal()` / `computed()` / `effect()` — core primitives.
- `input()` / `output()` — signal-based component I/O (v17.1+), replacing `@Input()`/`@Output()` decorators for new code.
- `model()` — two-way-bindable signal input (v17.2+), replacing manual `@Input()` + `@Output() xChange`.
- `linkedSignal()` / `resource()` — newer additions (v19+) for derived writable state and async data fetching; confirm availability before use.

Keep RxJS where it genuinely fits (event streams, debouncing, HTTP composition via `HttpClient` + operators) — signals are not a wholesale RxJS replacement.

### New control-flow syntax (stable since v17)

`@if` / `@for` / `@switch` replace the structural directives `*ngIf` / `*ngFor` / `*ngSwitch` in templates:

```html
@if (user(); as u) {
  <p>Hello {{ u.name }}</p>
} @else {
  <p>Loading…</p>
}

@for (item of items(); track item.id) {
  <li>{{ item.name }}</li>
} @empty {
  <li>No items</li>
}
```

`@for` requires an explicit `track` expression (no implicit `trackBy` fallback). For new templates prefer `@if`/`@for`/`@switch`; only touch existing `*ngIf`/`*ngFor` templates if already in scope for other reasons (avoid drive-by rewrites).

### `inject()` function vs constructor DI

`inject()` (stable since v14) is now generally preferred over constructor-parameter injection for readability and composability (usable in field initializers, functional guards/interceptors, and outside constructors):

```ts
export class UserService {
  private http = inject(HttpClient);
  private router = inject(Router);
}
```

Constructor injection still works and is not deprecated — treat this as a style preference; follow existing project convention rather than mixing both styles within the same class.

### Functional guards/resolvers/interceptors

Class-based `CanActivate`/`HttpInterceptor` are legacy; functional forms are current:

```ts
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isLoggedIn() || inject(Router).createUrlTree(['/login']);
};
```

```ts
provideHttpClient(withInterceptors([authInterceptor]));
```

### Zoneless change detection (developer preview v18+, maturing in v19/v20)

`provideZonelessChangeDetection()` removes `zone.js` dependency, relying on signals to know when to re-render. Do not assume this is production-stable or default without checking the detected version and the app's `app.config.ts` — this is the area most likely to have changed since this skill was written.

## Decision Guidance

- **New component, new project** — standalone, signals for local state, `@if`/`@for` in templates, `inject()`, functional guards/interceptors.
- **Existing NgModule-based app** — do not force a migration; new components can still go standalone (interop is supported), but respect existing conventions for anything you're not explicitly asked to modernize.
- **Global/shared app state** — signals + a plain injectable service is often sufficient; reach for NgRx/NgXs only when the app already uses it or genuinely needs time-travel/devtools-level state management.

## Verification

```shell
ng version
npm ls @angular/core
```

If the detected version predates a pattern mentioned above (e.g. pre-v17 for signals/control-flow, pre-v14 for standalone/`inject()`), do not suggest it — fall back to the version-appropriate pattern and confirm against `https://angular.dev` for that version's docs.
