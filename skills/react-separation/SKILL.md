---
name: "react-separation"
description: "แยก Component, Data Type และ Logic (Custom Hooks) ให้เป็นระเบียบตามแพทเทิร์นเดียว. ใช้เมื่อรีแฟคเตอร์หน้า/คอมโพเนนท์เริ่มรก, props/state/effects เยอะ."
---

# React Separation (Component / Types / Hooks)

## เป้าหมาย
- แยกความรับผิดชอบออกเป็น 3 ชั้น: UI Components, Types/Interfaces, Custom Hooks (Logic)
- ลดความยาวไฟล์และลดการปะปนของ business logic ใน JSX
- ทำให้ reuse logic และทดสอบ/ดูแลต่อได้ง่าย

## เมื่อไหร่ควรใช้
- ไฟล์ component เริ่มยาว/อ่านยาก (เช่น > 200-300 บรรทัด)
- มี state/effect/callback เยอะและกระจายทั่ว JSX
- มี type/interface/union ซ้ำซ้อนหรือกระจัดกระจายหลายไฟล์
- ต้องใช้ logic เดิมซ้ำในหลายหน้า/หลายคอมโพเนนท์

## โครงสร้างไฟล์ที่แนะนำ (Next.js App Router) — Centralized

types, helpers, hooks เก็บที่ root level ของ webapp:

```
webapp/
├── types/
│   ├── products.ts         ← types ทั้งหมดของ feature products
│   └── cart.ts             ← types ที่ใช้ข้าม component (เช่น CartLine)
├── helpers/
│   ├── products.ts         ← pure functions ของ feature products
│   ├── utils.ts            ← utility ทั่วไปที่ใช้หลายแห่ง (cn, etc.)
│   └── order-status.ts     ← shared domain helpers
├── hooks/
│   ├── use-product-detail.ts ← logic hook เฉพาะ feature
│   └── use-cart.ts         ← logic hook ที่ใช้ข้าม component
└── components/products/
    ├── product-detail.tsx      ← ประกอบร่าง + wiring (เรียก hook → ส่ง props เข้า view)
    └── product-detail.view.tsx ← UI view ล้วน

กติกา:
- `types/*.ts` — รวม type/interface/union (feature-specific หรือ shared ข้าม component)
- `helpers/*.ts` — ฟังก์ชัน pure: mapping, format, clamp, key generation, cn utility (ไม่พึ่ง React)
- `hooks/use-*.ts` — จัดการ state, derived values, side effects, orchestration คืนค่าเป็น `{ values..., actions... }`
- `.view.tsx` — เน้น UI ล้วน รับ props ที่ "พร้อมแสดงผล" และส่ง event handler ผ่าน props
- component root file (ไม่มี suffix) — เล็กที่สุด แค่เรียก hook → ส่ง props เข้า view
- import paths: `@/types/*`, `@/helpers/*`, `@/hooks/use-*`

## ขั้นตอนการรีแฟคเตอร์ (Workflow)
1) แยก Types/Interfaces → `types/<feature>.ts`
- ย้าย type, interface, union ทั้งหมดของหน้านั้นไป `types/<feature>.ts`
- import path: `@/types/<feature>`
- ห้าม declare type/interface ไว้ในไฟล์ component หรือ hook

2) แยก Helpers → `helpers/<feature>.ts`
- ย้ายฟังก์ชันที่ไม่พึ่ง React ไป `helpers/<feature>.ts`
- import path: `@/helpers/<feature>`
- ให้ helper pure และทดสอบได้ด้วย unit test ในอนาคต

3) แยก Logic เป็น Hook → `hooks/use-<feature>.ts`
- สร้าง `hooks/use-<feature>.ts` เพื่อรวบ state, effects, callbacks, derived state
- import path: `@/hooks/use-<feature>`
- คืนค่าเป็น object: `{ values..., actions... }`

4) สร้าง View Component → `<feature>.view.tsx`
- สร้าง `<feature>.view.tsx` เก็บ JSX หลักทั้งหมด ใน `components/<feature>/`
- ไฟล์หลักทำหน้าที่แค่เรียก hook แล้วส่ง props เข้า view

5) ตรวจพฤติกรรม
- ตรวจ flow หลัก: เลือกตัวเลือก, validate, add to cart, disabled state, empty state

## รูปแบบ return ของ Hook (ตัวอย่าง)
- values: `selectedSize`, `selectedColor`, `qty`, `canAddToCart`, `status`
- actions: `setSelectedSize`, `setSelectedColor`, `incQty`, `decQty`, `addToCart`

## Definition of Done
- ไฟล์ view ไม่มี business logic หนัก ๆ
- logic อยู่ใน custom hook (`hooks/use-*.ts`) และมี dependency ที่ถูกต้อง
- types/interface รวมศูนย์ที่ `types/*.ts` ไม่กระจายใน view, hook, หรือ component
- helpers เป็น pure functions อยู่ที่ `helpers/*.ts`
- import paths: `@/types/*`, `@/helpers/*`, `@/hooks/use-*`
