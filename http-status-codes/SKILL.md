---
name: HTTP Status Codes
description: HTTP status code reference covering 1xx-5xx categories, REST API design conventions (which code for which operation), and frontend/backend error-handling patterns. Use when designing API responses, choosing status codes for endpoints, or handling fetch/axios errors in a frontend client.
---

# HTTP Status Codes

Reference สำหรับ HTTP status codes ทั้ง 5 หมวด (1xx-5xx) พร้อมแนวทางใช้งานจริงตอนออกแบบ REST API และตอนจัดการ error ฝั่ง frontend

## Why Status Codes Exist

HTTP status code คือ machine-readable, standardized signal ที่บอกผลลัพธ์ของ request โดยไม่ต้อง parse response body ก่อน — client (browser, fetch, axios, load balancer, monitoring tool) เช็คแค่ตัวเลข 3 หลักก็รู้ทันทีว่า request สำเร็จ, ต้อง redirect, client ทำผิด, หรือ server พัง

ถ้าไม่มี status code มาตรฐาน แต่ละ server จะสื่อผลลัพธ์ผ่านข้อความใน body เอง เช่น `"success"`, `"done"`, `"ok"`, `"error"` — ซึ่งไม่สอดคล้องกันข้าม service, ข้าม team, ข้าม framework ทำให้ client ต้อง parse string เดาความหมายแทนที่จะเช็ค convention ที่ตกลงร่วมกันทั้งอุตสาหกรรม การมี status code มาตรฐานยังทำให้ tooling ทั่วไป (caching layer, retry logic, monitoring/alerting, API gateway) ทำงานได้ถูกต้องโดยไม่ต้องรู้ business logic ของแต่ละ endpoint

## 1xx Informational

| Code | Name | Meaning | When to use |
|------|------|---------|-------------|
| 100 | Continue | Server ได้รับ request headers แล้ว client ส่ง body ต่อได้ | Server ตอบอัตโนมัติเมื่อ client ส่ง header `Expect: 100-continue` ก่อน upload body ก้อนใหญ่ |
| 101 | Switching Protocols | Server ยอมรับ request เปลี่ยน protocol ตาม header `Upgrade` | WebSocket handshake (`Upgrade: websocket`), HTTP/2 upgrade |
| 102 | Processing | Server รับ request แล้วและกำลังประมวลผล แต่ยังไม่มี response พร้อม | WebDAV เท่านั้น — ใช้กันไม่ได้แล้วป้องกัน client timeout ระหว่างรอ operation ที่ใช้เวลานาน |

## 2xx Successful

| Code | Name | Meaning | When to use |
|------|------|---------|-------------|
| 200 | OK | Request สำเร็จ มี response body | Default สำหรับ GET, PUT/PATCH ที่คืนข้อมูลที่อัปเดตแล้ว, POST ที่ไม่ใช่การสร้าง resource (เช่น login, search, calculate) |
| 201 | Created | สร้าง resource ใหม่สำเร็จ | POST ที่สร้าง resource — ควรส่ง header `Location` ชี้ไป resource ใหม่ และ body คืนข้อมูล resource ที่สร้าง |
| 202 | Accepted | รับ request แล้วแต่ยังประมวลผลไม่เสร็จ (async) | Endpoint ที่ trigger background job/queue เช่น export report, batch process |
| 203 | Non-Authoritative Information | สำเร็จ แต่ข้อมูลผ่านการแปลง/proxy มาแล้ว ไม่ใช่จาก origin server โดยตรง | ใช้น้อยมาก — proxy/gateway ที่ modify response ก่อนส่งต่อ |
| 204 | No Content | สำเร็จ ไม่มี response body | DELETE ที่สำเร็จ, PUT/PATCH ที่ไม่ต้องคืนข้อมูลกลับ |
| 205 | Reset Content | สำเร็จ ให้ client reset form/view | หลัง submit form แล้วต้องการให้ client เคลียร์ input เอง (ใช้น้อย) |
| 206 | Partial Content | คืนข้อมูลบางส่วนตาม `Range` header | Video/audio streaming, resumable file download |

## 3xx Redirection

| Code | Name | Meaning | When to use |
|------|------|---------|-------------|
| 300 | Multiple Choices | มีหลาย representation ให้เลือก | ใช้น้อยมากในทางปฏิบัติ |
| 301 | Moved Permanently | Resource ย้ายไปถาวร | URL เปลี่ยนถาวร (SEO redirect), เปลี่ยน domain — cache ได้และ browser จะเปลี่ยน method เป็น GET |
| 302 | Found | Resource ย้ายชั่วคราว | Redirect ชั่วคราว legacy behavior เปลี่ยน method เป็น GET เหมือนกัน — มักสร้างความสับสน ใช้ 303/307 แทนถ้าต้องการความชัดเจน |
| 303 | See Other | ให้ client ไป GET resource อื่นแทน | Post-Redirect-Get pattern — หลัง POST/PUT สำเร็จ redirect ไปหน้าแสดงผลด้วย GET เสมอ |
| 304 | Not Modified | Resource ไม่เปลี่ยนตั้งแต่ครั้งก่อน | Response ต่อ conditional request (`If-None-Match`/`If-Modified-Since`) — client ใช้ cache เดิมได้ ไม่มี body |
| 307 | Temporary Redirect | เหมือน 302 แต่รับประกันว่า method และ body เดิมจะถูกใช้ซ้ำ | Redirect ชั่วคราวที่ต้อง preserve POST body (302 ไม่รับประกันเรื่องนี้) |
| 308 | Permanent Redirect | เหมือน 301 แต่รับประกัน method/body เดิม | Redirect ถาวรที่ต้อง preserve POST/PUT body |

## 4xx Client Error

| Code | Name | Meaning | When to use |
|------|------|---------|-------------|
| 400 | Bad Request | Request ผิด syntax หรือ malformed | JSON parse ไม่ผ่าน, query param ผิดรูปแบบ, request ที่ server อ่านไม่ออกเลย (ไม่ใช่ validation ตาม business rule) |
| 401 | Unauthorized | ไม่มีหรือ invalid credentials | ไม่ได้ login, token หมดอายุ/invalid — จริง ๆ ควรชื่อ "Unauthenticated" แต่ spec เรียกแบบนี้ |
| 402 | Payment Required | สงวนไว้สำหรับระบบชำระเงิน | ยังไม่ใช้แพร่หลายตาม spec เดิม แต่บาง API (เช่น billing/metering) เอามาใช้บอกว่าบัญชีค้างชำระ/เกิน quota |
| 403 | Forbidden | Authenticated แล้วแต่ไม่มีสิทธิ์เข้าถึง resource นี้ | User login อยู่แต่ role/permission ไม่พอ (ต่างจาก 401 ที่ยังไม่รู้ตัวตนเลย) |
| 404 | Not Found | ไม่พบ resource | Route ไม่มีจริง, id ที่ query ไม่มีใน database |
| 405 | Method Not Allowed | Route มีจริงแต่ไม่รองรับ HTTP method นี้ | เช่น endpoint รองรับแค่ GET/POST แต่ client ยิง DELETE มา |
| 406 | Not Acceptable | Server ให้ response ตาม `Accept` header ที่ client ขอไม่ได้ | Content negotiation ล้มเหลว (client ขอ `Accept: application/xml` แต่ server มีแต่ JSON) |
| 409 | Conflict | Request ขัดแย้งกับ state ปัจจุบันของ resource | สร้าง resource ที่ unique field ซ้ำ (เช่น email ซ้ำ), version conflict ตอน concurrent update (optimistic locking) |
| 413 | Payload Too Large | Request body ใหญ่เกิน limit | Upload ไฟล์เกิน max size ที่ server/proxy กำหนด |
| 414 | URI Too Long | URL ยาวเกิน limit | Query string ยาวเกินไป — มักแก้โดยเปลี่ยนไปใช้ POST body แทน |
| 415 | Unsupported Media Type | `Content-Type` ของ request ไม่รองรับ | Client ส่ง `Content-Type: text/plain` แต่ endpoint รับเฉพาะ `application/json` |
| 422 | Unprocessable Entity | Syntax ถูกต้อง (parse ผ่าน) แต่ข้อมูลไม่ผ่าน validation ตาม business rule | Validation error ใน REST API เช่น field required หายไป, email format ผิด, ค่าติด negative — แยกจาก 400 ที่หมายถึง malformed request |
| 429 | Too Many Requests | Client ยิง request เกิน rate limit | Rate limiting — ควรแนบ header `Retry-After` บอกว่ารอกี่วินาทีค่อยลองใหม่ |

## 5xx Server Error

| Code | Name | Meaning | When to use |
|------|------|---------|-------------|
| 500 | Internal Server Error | Server เจอ error ที่ไม่คาดคิด/ไม่ได้ handle | Unhandled exception, bug ใน application code — ไม่ใช่ error ที่ client ทำให้เกิด |
| 501 | Not Implemented | Server ไม่รองรับ method/feature นี้เลย | Endpoint ที่ยังไม่ implement หรือ method ที่ server ไม่รองรับตาม design |
| 502 | Bad Gateway | Server ที่ทำหน้าที่ gateway/proxy ได้ response ที่ invalid จาก upstream | Reverse proxy (nginx, load balancer) ต่อ upstream service ไม่ติดหรือ upstream ตอบผิดรูปแบบ |
| 503 | Service Unavailable | Server ไม่พร้อมให้บริการชั่วคราว | Maintenance mode, overload, deploy ระหว่าง rolling update — ควรแนบ `Retry-After` เช่นกัน |
| 504 | Gateway Timeout | Server ที่ทำหน้าที่ gateway รอ upstream นานเกินไปจนหมดเวลา | Upstream service ตอบช้าเกิน timeout ที่ proxy/gateway กำหนด |

## REST API Design Conventions

แนวทางเลือก status code ตาม HTTP method และสถานการณ์ทั่วไป:

- **GET** — `200` เมื่อพบ resource, `404` เมื่อไม่พบ, `400`/`422` เมื่อ query param ผิด
- **POST (สร้าง resource)** — `201 Created` พร้อม header `Location` และ body คืนข้อมูลที่สร้างแล้ว — อย่าใช้ `200` เพราะไม่สื่อว่ามีการสร้างจริง
- **POST (action ที่ไม่สร้าง resource)** — เช่น `/login`, `/search`, `/calculate` ใช้ `200` ปกติ
- **PUT (replace ทั้ง resource)** — `200` พร้อม body ที่อัปเดตแล้ว หรือ `204` ถ้าไม่ต้องคืน body
- **PATCH (แก้บางส่วน)** — เหมือน PUT, `200` หรือ `204`
- **DELETE** — `204 No Content` เมื่อลบสำเร็จและไม่มีอะไรต้องคืน (ปกติที่สุด), หรือ `200` ถ้าต้องคืนข้อมูล resource ที่ถูกลบ
- **201 vs 200 สำหรับการสร้าง** — ใช้ `201` เสมอเมื่อ endpoint สร้าง resource ใหม่จริง ๆ (มี id ใหม่เกิดขึ้น) ส่วน `200` ใช้กับ action ที่ประมวลผลแล้วคืนผลลัพธ์โดยไม่ได้สร้าง entity ใหม่
- **422 vs 400 สำหรับ validation** — `400` คือ request ที่ parse/read ไม่ได้เลย (malformed JSON, wrong content-type) ส่วน `422` คือ request ที่ parse ได้ปกติแต่ข้อมูลไม่ผ่าน business validation (required field ว่าง, format ผิด, ค่าที่ส่งมาไม่สมเหตุสมผล) — แยกสองอันนี้ให้ frontend รู้ว่าเป็น bug ของ client-side code (400) หรือ user ต้องแก้ input เอง (422)
- **409 Conflict** — ใช้เมื่อ request valid ในตัวเองแต่ขัดกับ state ปัจจุบันของระบบ เช่น สมัคร email ที่มีอยู่แล้ว, อัปเดต resource ที่ version ไม่ตรง (optimistic concurrency), ลบ resource ที่ยังมี dependency ผูกอยู่

## Frontend Error Handling

`fetch` ไม่ throw error เมื่อได้ status 4xx/5xx — ต้องเช็ค `response.ok` เอง:

```ts
async function apiRequest<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init);

  if (res.ok) {
    return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
  }

  const body = await res.json().catch(() => null);

  switch (res.status) {
    case 401:
      // redirect ไป login, clear token
      throw new AuthError("Unauthorized");
    case 422:
      // แสดง field-level validation error จาก body
      throw new ValidationError(body?.errors ?? {});
    case 429: {
      const retryAfter = res.headers.get("Retry-After");
      throw new RateLimitError(retryAfter ? Number(retryAfter) : undefined);
    }
    case 503:
      // service ปิดปรับปรุงชั่วคราว — อาจ retry อัตโนมัติ
      throw new ServiceUnavailableError();
    default:
      throw new ApiError(res.status, body?.message ?? "Unexpected error");
  }
}
```

- `axios` throw error อัตโนมัติสำหรับ status นอกช่วง 2xx — เข้าถึง status ผ่าน `error.response?.status`
- **Retry logic** ควรทำเฉพาะ status ที่ transient/แก้ได้ด้วยการรอ — `429` (เคารพ `Retry-After` header), `502`/`503`/`504` (exponential backoff) — อย่า retry `4xx` อื่น ๆ เพราะ request จะพังซ้ำเหมือนเดิมทุกครั้ง
- แยก error type ตามหมวด (`AuthError`, `ValidationError`, `RateLimitError`, `ServerError`) แทนที่จะเช็ค status number กระจายทั่วโค้ด เพื่อให้ UI layer จัดการแต่ละ case ได้ชัดเจน

## Common Mistakes

- **ใช้ `200` กับทุก response แล้วซ่อน error ไว้ใน body** (เช่น `{ "success": false, "error": "..." }`) — ทำให้ HTTP-level tooling (cache, monitoring, retry, API gateway) มองไม่เห็นว่า request ล้มเหลว และ client ต้อง parse body ทุกครั้งเพื่อเช็ค error แทนที่จะเช็ค status code
- **ใช้ `500` กับ client error** เช่น validation ผิดหรือ resource ไม่พบ — ทำให้ frontend และ monitoring/alerting แยกไม่ออกระหว่าง "user ทำผิด" กับ "server พังจริง" (alert fatigue จาก false positive)
- **ไม่ตอบ `404` สำหรับ REST route ที่ id ไม่พบ** — บาง API ตอบ `200` พร้อม body ว่างหรือ `null` แทน ทำให้ client ต้องเช็ค body content แทนที่จะเช็ค status
- **ปนกันระหว่าง `401` กับ `403`** — ใช้ `401` ผิดตอนที่ user login อยู่แล้วแต่ไม่มีสิทธิ์ (ควรเป็น `403`) หรือใช้ `403` ตอนที่ยังไม่ได้ login เลย (ควรเป็น `401`)
- **ไม่แนบ `Retry-After` กับ `429`/`503`** — ทำให้ client ไม่รู้ว่าควรรอนานแค่ไหนก่อน retry

## สรุป

เลือก status code ตามความหมายจริงของผลลัพธ์ ไม่ใช่ความสะดวกของฝั่ง backend — แยก `400` (request อ่านไม่ได้) กับ `422` (validation ตาม business rule), แยก `401` (ยังไม่รู้ตัวตน) กับ `403` (รู้ตัวตนแต่ไม่มีสิทธิ์), ใช้ `201`/`204` ให้ตรงกับ operation จริง และฝั่ง frontend ต้องเช็ค `response.ok`/status เสมอแทนการเชื่อ body เพียงอย่างเดียว เพื่อให้ tooling มาตรฐาน (cache, retry, monitoring) ทำงานถูกต้องโดยไม่ต้องรู้ business logic ของแต่ละ endpoint
