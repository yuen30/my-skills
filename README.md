# Skills Collection

คอลเลกชัน skills ส่วนตัวของ taweechai_y

## โครงสร้าง

```
skills/
├── <skill-name>/
│   ├── SKILL.md          # คำอธิบายและคำสั่งหลักของ skill
│   ├── references/       # เอกสารอ้างอิงเพิ่มเติม
│   ├── examples/         # ตัวอย่างการใช้งาน
│   ├── scripts/          # สคริปต์ที่เกี่ยวข้อง
│   └── templates/        # เทมเพลตสำหรับใช้งาน
└── README.md
```

## การสร้าง Skill ใหม่

1. สร้างโฟลเดอร์ใหม่ด้วยชื่อ skill (ใช้ kebab-case)
2. สร้างไฟล์ `SKILL.md` ที่อธิบายว่า skill ทำอะไร และมีคำสั่งอะไรบ้าง
3. เพิ่ม references, examples, scripts ตามต้องการ

## Installation

```bash
npx skills add yuen30/my-skills
```

## รายการ Skills

| Skill | Description |
|-------|-------------|
| [docker](./docker/) | Docker & Docker Compose best practices, templates, and troubleshooting |
| [react-three-fiber](./react-three-fiber/) | React Three Fiber (R3F), Three.js, and Drei helpers |
| [tailwind-v4-shadcn](./tailwind-v4-shadcn/) | Tailwind CSS v4 + shadcn/ui components |
| [nextjs-core-system](./nextjs-core-system/) | Next.js 16 App Router — Server Components, caching, data fetching, deployment |
| [nextjs-pages-router](./nextjs-pages-router/) | Next.js Pages Router — SSR, SSG, ISR, API Routes, getStaticProps/getServerSideProps |
| [nextjs-layouts-and-pages](./nextjs-layouts-and-pages/) | Next.js Layouts and Pages — file-system routing, nested layouts, dynamic segments, navigation |
| [nextjs-linking-and-navigating](./nextjs-linking-and-navigating/) | Next.js Linking and Navigating — prefetching, streaming, client-side transitions, optimization |
| [nextjs-server-and-client-components](./nextjs-server-and-client-components/) | Next.js Server and Client Components — rendering boundaries, interleaving patterns, hydration |
| [nextjs-fetching-data](./nextjs-fetching-data/) | Next.js Fetching Data — Server Components, Streaming, Suspense, parallel/sequential patterns |
| [nextjs-mutating-data](./nextjs-mutating-data/) | Next.js Mutating Data — Server Actions, forms, revalidation, security best practices |
| [nextjs-caching](./nextjs-caching/) | Next.js Caching — Cache Components, "use cache" directive, Streaming, PPR |
| [nextjs-revalidating](./nextjs-revalidating/) | Next.js Revalidating — cacheLife, cacheTag, revalidateTag, updateTag, revalidatePath |
| [nextjs-error-handling](./nextjs-error-handling/) | Next.js Error Handling — error boundaries, notFound, useActionState, catchError |
