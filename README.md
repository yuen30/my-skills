# My Skills

ชุด Skills สำหรับ OpenCode AI Agent — พร้อมใช้งานข้ามเครื่องได้ทันที

## 📦 มีอะไรบ้าง

รวมกว่า **60 skills** สำหรับงานด้าน:
- **Azure** — Deploy, Diagnose, Compute, Kubernetes, Messaging, AI, Cost, Compliance, RBAC, และอื่นๆ
- **AWS** — Lambda, CDK, ECS, EC2, S3, CloudFront, Serverless
- **Frontend** — shadcn/ui, Tailwind v4, Nuxt UI, React, Next.js, View Transitions
- **Mobile** — React Native, Expo
- **DevOps** — Docker, Docker Compose, Terraform, Vercel CLI
- **Framework** — Fiber (Go), Laravel Filament, Ruby on Rails
- **Tools** — Firebase, Entra ID, TDD, Web Design Guidelines, xlsx, docx

ดูรายชื่อทั้งหมดได้ที่ [`skills/`](./skills/)

## 🚀 วิธีติดตั้ง

มี 2 วิธีให้เลือก:

### วิธีที่ 1: Clone แล้ว symlink (แนะนำ)

```bash
# 1. Clone ไปที่เครื่องใหม่
git clone <repo-url> ~/my-skills

# 2. ลบ skills เดิม (ถ้ามี) แล้วสร้าง symlink
rm -rf ~/.agents/skills
ln -s ~/my-skills/skills ~/.agents/skills

# หรือถ้าต้องการเก็บ skills เดิมไว้
mv ~/.agents/skills ~/.agents/skills.bak
ln -s ~/my-skills/skills ~/.agents/skills
```

### วิธีที่ 2: คัดลอกตรง ๆ

```bash
# 1. Clone
git clone <repo-url> ~/my-skills

# 2. คัดลอกทับ
cp -R ~/my-skills/skills/* ~/.agents/skills/
```

## 🔄 วิธีอัพเดท

```bash
# ถ้าใช้ symlink (วิธีที่ 1) — แค่ git pull
cd ~/my-skills
git pull

# ถ้าใช้ copy (วิธีที่ 2) — pull แล้ว copy ใหม่
cd ~/my-skills
git pull
cp -R ~/my-skills/skills/* ~/.agents/skills/
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

1. เพิ่ม文件夹ใน `skills/` พร้อม `SKILL.md`
2. Commit และ push
3. ที่เครื่องอื่น `git pull` (หรือ copy ใหม่)

## ⚠️ หมายเหตุ

- Skills ทั้งหมดถูก export จาก OpenCode Agent (`~/.agents/skills/`)
- ถ้ามีการติดตั้ง skill เพิ่มเติมบนเครื่องใดเครื่องหนึ่ง อย่าลืม copy มาใส่ repo นี้ด้วย
