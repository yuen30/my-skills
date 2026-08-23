---
name: frappe-framework
description: Use when developing on Frappe Framework or ERPNext (built on Frappe) — DocTypes, hooks.py, ORM, whitelisted API methods, bench CLI. Detects the installed Frappe/ERPNext version first before giving version-specific guidance.
---

# Frappe Framework

Expert guidance for Frappe Framework and ERPNext (which is built on Frappe) app development. Frappe ships regular version updates with API and DocType schema changes — detect the installed version before asserting version-specific behavior.

**Precondition — do not skip:** Before making claims about version-specific Frappe/ERPNext behavior, detect the installed version.

## Step 0: Detect the installed Frappe/ERPNext version

Run one or more of these from the bench directory:

```shell
bench version
python3 -c "import frappe; print(frappe.__version__)"
cat apps/frappe/frappe/__init__.py | grep __version__
cat apps/erpnext/erpnext/__init__.py | grep __version__   # if ERPNext is installed
```

State the detected version explicitly before relying on version-specific API details.

## App/Module Structure

```
my_app/
├── my_app/
│   ├── hooks.py
│   ├── modules.txt
│   ├── my_module/
│   │   ├── doctype/
│   │   │   └── my_doctype/
│   │   │       ├── my_doctype.json
│   │   │       ├── my_doctype.py
│   │   │       ├── my_doctype.js
│   │   │       └── test_my_doctype.py
│   │   └── report/
│   ├── config/
│   ├── public/
│   │   ├── js/
│   │   └── css/
│   └── www/
├── setup.py
└── requirements.txt
```

- `modules.txt` lists the app's module names — each corresponds to a folder holding that module's DocTypes/reports/pages.
- Each DocType folder has: `.json` (field schema, shown in Desk UI), `.py` (server-side controller), `.js` (client-side form script), and `test_*.py` (unit tests).

## DocType Basics

Fields are defined in the DocType's `.json` (normally edited via the Desk UI, which regenerates the JSON — hand-editing is possible but keep field `fieldname`/`fieldtype` consistent with existing conventions).

Controller class:

```python
# my_doctype.py
import frappe
from frappe.model.document import Document


class MyDocType(Document):
    def validate(self):
        if not self.title:
            frappe.throw("Title is required")

    def before_save(self):
        self.status = self.status or "Draft"

    def on_submit(self):
        self.notify_stakeholders()

    def on_cancel(self):
        if self.linked_invoice:
            frappe.throw("Cannot cancel — linked invoice exists")

    def notify_stakeholders(self):
        frappe.sendmail(recipients=[self.owner], subject="Document submitted")
```

Common lifecycle hooks (in call order for a save): `validate` → `before_save` → (DB write) → `after_insert` (new docs only) → `on_update`; for submittable DocTypes: `before_submit` → `on_submit`, and `before_cancel` → `on_cancel`.

## Frappe ORM

```python
import frappe

# Get a single full document
doc = frappe.get_doc("Sales Order", "SO-0001")
doc.status = "Closed"
doc.save()

# Create a new document
new_doc = frappe.get_doc({
    "doctype": "Task",
    "subject": "Follow up",
    "status": "Open",
})
new_doc.insert()

# Lightweight list query — prefer this over frappe.get_doc in loops
tasks = frappe.get_all(
    "Task",
    filters={"status": "Open"},
    fields=["name", "subject", "status"],
    limit_page_length=0,
)

# frappe.get_list respects user permissions; frappe.get_all bypasses them by default
tasks_permission_checked = frappe.get_list(
    "Task", filters={"status": "Open"}, fields=["name", "subject"]
)

# Single-value reads/writes without loading the whole document
status = frappe.db.get_value("Task", "TASK-0001", "status")
frappe.db.set_value("Task", "TASK-0001", "status", "Closed")

# Query builder for complex joins/aggregates
from frappe.query_builder import DocType

Task = DocType("Task")
query = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject)
    .where(Task.status == "Open")
)
results = query.run(as_dict=True)

# Permission check
if frappe.has_permission("Task", "write", doc=task_name):
    ...
```

- `frappe.get_all` — fast, does **not** enforce row-level/user permissions by default (`ignore_permissions` implicit) — fine for system-level/background logic, but not for exposing arbitrary data straight to a user-facing whitelisted method without an explicit permission check.
- `frappe.get_list` — same shape as `get_all` but applies the current user's permission rules — prefer this in request-context code that surfaces list data to the current user.
- `frappe.db.get_value`/`set_value` — cheap single-field access, skips document controller hooks (`validate`, etc.) — do not use when you need `validate`/`on_update` side effects to run.

## `hooks.py` Patterns

```python
# hooks.py

doc_events = {
    "Sales Order": {
        "on_submit": "my_app.my_module.events.sales_order.on_submit",
        "on_cancel": "my_app.my_module.events.sales_order.on_cancel",
    },
    "*": {
        "on_update": "my_app.my_module.events.audit.log_update",
    },
}

scheduler_events = {
    "daily": [
        "my_app.my_module.tasks.send_daily_digest",
    ],
    "cron": {
        "0 */4 * * *": [
            "my_app.my_module.tasks.sync_external_orders",
        ],
    },
}
```

```python
# my_module/api.py
import frappe


@frappe.whitelist()
def get_dashboard_summary(customer=None):
    if not frappe.has_permission("Customer", "read", doc=customer):
        frappe.throw("Not permitted", frappe.PermissionError)
    return frappe.get_all("Sales Order", filters={"customer": customer}, fields=["name", "grand_total"])
```

- `doc_events` wires controller-style hooks onto DocTypes without editing their base `.py` file — useful for app-level customization of core/other-app DocTypes. `"*"` applies to every DocType.
- `scheduler_events` supports `all`, `hourly`, `daily`, `weekly`, `monthly`, and `cron` (dict of cron expression → list of methods).
- `@frappe.whitelist()` exposes a Python function as an API endpoint (`/api/method/<dotted.path>`) callable from JS/REST. Always validate permissions explicitly inside — whitelisting alone does not enforce DocType-level permissions unless you call `frappe.has_permission` or use `frappe.get_list`/document methods that already check it.

## `bench` CLI Basics

```shell
bench new-app my_app                 # scaffold a new app
bench get-app <app-name> <git-url>   # fetch an existing app into the bench
bench --site <site> install-app my_app
bench --site <site> migrate          # run pending patches + sync DocType schema changes
bench build                          # build JS/CSS assets
bench restart                        # restart bench-managed processes (workers, web)
bench --site <site> console          # interactive Python console with frappe context loaded
```

## Common Pitfalls

- **Bypassing permissions with `ignore_permissions=True` without justification** — `doc.insert(ignore_permissions=True)` / `doc.save(ignore_permissions=True)` skip the permission system entirely. Only use it in trusted system/background contexts (migrations, scheduled jobs acting as system user) with a clear reason in a comment — never as a default way to silence a `PermissionError` in user-facing code.
- **N+1 queries via `frappe.get_doc` in loops** — loading a full document per row is expensive (loads child tables, runs `get_doc` overhead per call):

```python
# ❌ WRONG — one full document load per row
for name in task_names:
    doc = frappe.get_doc("Task", name)
    print(doc.status)

# ✅ CORRECT — one query for exactly the fields needed
tasks = frappe.get_all("Task", filters={"name": ["in", task_names]}, fields=["name", "status"])
```

- **`frappe.db.commit()` misuse** — within a normal web request, Frappe auto-commits at the end of the request (and auto-rolls-back on unhandled exception); do not sprinkle manual `frappe.db.commit()` calls in request-handling code, as it breaks the request-level transaction boundary and can commit partial state before a later error. In long-running/background contexts (scheduled jobs, background workers processing large batches, data migration scripts run outside a request), you must commit explicitly at safe checkpoints (e.g. after each batch) since there is no implicit end-of-request commit — and consider `frappe.db.rollback()` in the except branch to keep the session consistent.
