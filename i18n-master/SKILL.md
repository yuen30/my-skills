---
name: i18n-master
description: Manages internationalization (i18n) for the monorepo, supporting Thai (th), English (en), and Vietnamese (vi). Use for updating JSON translation files and ensuring consistent terminology.
---

# i18n Master Workflow

This skill ensures the application is correctly translated and culturally appropriate for all regions.

## Translation Files Location
- `webapp/messages/*.json`

## Procedures
1. **Sync Keys**: When adding a key to `th.json`, ensure it exists in `en.json` and `vi.json`.
2. **Contextual Translation**: Use professional terminology appropriate for an industrial paint ordering system.
3. **Next-intl Integration**: Ensure pages are within `[locale]` dynamic routes.
4. **Formatting**: Use `Intl` browser APIs for numbers, dates, and currency (THB, VND).

## Common Terms Reference
- **Order**: รายการสั่งซื้อ / Đơn hàng
- **Product**: สินค้า / Sản phẩm
- **Contract**: สัญญา / Hợp đồng
- **Dashboard**: แดชบอร์ด / Bảng điều khiển
