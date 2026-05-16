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
