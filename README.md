# my-skills

ชุด Skills สำหรับ OpenCode AI Agent — พร้อมใช้งานข้ามเครื่องได้ทันที

Repo: `git@github.com:yuen30/my-skills.git`

## 📦 มีอะไรบ้าง

รวมกว่า **60 skills** สำหรับงานด้าน:
- **Azure** — Deploy, Diagnose, Compute, Kubernetes, Messaging, AI, Cost, Compliance, RBAC, และอื่นๆ
- **AWS** — Lambda, CDK, ECS, EC2, S3, CloudFront, Serverless
- **Frontend** — shadcn/ui, Tailwind v4, Nuxt UI, React, Next.js, View Transitions
- **Mobile** — React Native, Expo
- **DevOps** — Docker, Docker Compose, Terraform, Vercel CLI
- **Framework** — Fiber (Go), Laravel Filament, Ruby on Rails
- **Tools** — Firebase, Entra ID, TDD, Web Design Guidelines, xlsx, docx

ดูรายชื่อทั้งหมดได้ที่ [`skills/_index.md`](./skills/_index.md)

## 🚀 วิธีติดตั้ง

```bash
npx skills add yuen30/my-skills
```

เท่านี้ก็เรียบร้อย — ระบบจะติดตั้ง skills ทั้งหมดให้อัตโนมัติ

### ถ้าต้องการติดตั้งทีละตัว

```bash
npx skills add yuen30/my-skills/skills/<skill-name>
```

เช่น:

```bash
npx skills add yuen30/my-skills/skills/azure-diagnostics
npx skills add yuen30/my-skills/skills/shadcn
```

## 🔄 วิธีอัพเดท

```bash
npx skills update yuen30/my-skills
```

หรืออัพเดททั้งหมดพร้อมกัน:

```bash
npx skills update --all
```

## 📁 โครงสร้าง

```
my-skills/
├── skills/                  # ตัว Skill ทั้งหมด
│   ├── azure-diagnostics/   # แต่ละ skill มี SKILL.md + references/
│   ├── aws-cdk/
│   ├── shadcn/
│   ├── ...
│   └── _index.md            # รายชื่อทั้งหมด
├── README.md
└── .gitignore
```

## 🧰 การเพิ่ม skill ใหม่

1. เพิ่ม directory ใน `skills/` พร้อม `SKILL.md`
2. Commit และ push
3. ที่เครื่องอื่น: `npx skills update yuen30/my-skills`

## ⚠️ หมายเหตุ

- Skills ทั้งหมดถูก export จาก OpenCode Agent (`~/.agents/skills/`)
- ถ้ามีการติดตั้ง skill เพิ่มเติมบนเครื่องใดเครื่องหนึ่ง อย่าลืม copy มาใส่ repo นี้ด้วย
