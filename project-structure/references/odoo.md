Read when creating or laying out an Odoo addon/module.

# Odoo Addon Structure

```text
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── my_model_security.xml   # record rules, groups
├── data/
│   └── my_model_data.xml
├── static/
│   ├── description/icon.png
│   └── src/
├── controllers/
│   ├── __init__.py
│   └── main.py
└── wizards/
    ├── __init__.py
    └── my_wizard.py
```

`__manifest__.py`:

```python
{
    "name": "My Module",
    "version": "17.0.1.0.0",
    "summary": "Short description",
    "category": "Sales",
    "depends": ["base", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "security/my_model_security.xml",
        "views/my_model_views.xml",
        "data/my_model_data.xml",
    ],
    "installable": True,
    "application": False,
}
```

- `depends` must list every module whose models/views/security this addon relies on; missing deps cause load-order errors.
- Files in `data` load in the listed order; security CSV/XML must load before views that reference the groups/rules.
