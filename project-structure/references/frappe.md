Read when creating or laying out a Frappe / ERPNext app, module, or DocType.

# Frappe App Structure

```text
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

- `modules.txt` lists the app's module names; each corresponds to a folder holding that module's DocTypes, reports, and pages.
- Each DocType folder has `.json` (field schema, shown in Desk UI), `.py` (server-side controller), `.js` (client-side form script), and `test_*.py` (unit tests).
