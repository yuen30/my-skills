---
name: odoo-addons
description: Use when developing or reviewing Odoo addon/module code — models, views, security, wizards, controllers. Detects the installed Odoo version first, since Odoo ships a new major version yearly with meaningful API differences (e.g. attrs/states deprecated in favor of direct Python expressions in Odoo 17+).
---

# Odoo Addons

Expert guidance for building and reviewing Odoo addon (module) code. Odoo ships a new major version every year with real breaking changes across the ORM, view syntax, and JS framework — do not assume a version from memory.

**Precondition — do not skip:** Before asserting any version-specific API behavior (especially view `attrs`/`states` vs direct Python expressions), detect the installed Odoo version.

## Step 0: Detect the installed Odoo version

Run one or more of these:

```shell
odoo-bin --version
python3 -c "import odoo; print(odoo.release.version)"
grep -i odoo requirements.txt
```

Or check the addon's own `__manifest__.py` — the `version` key conventionally starts with the target Odoo series, e.g. `"version": "17.0.1.0.0"` means built for Odoo 17.0.

State the detected major version explicitly before giving version-specific guidance (e.g. attrs/states migration only applies from Odoo 17 onward).

## Step 2: Fetch docs for the detected major version

Canonical source: `https://github.com/odoo/documentation` repository, with a separate branch per major version (`19.0`, `18.0`, `17.0`, etc.) — this repo covers addon/module development docs (ORM, views, etc.).

Choose one approach:

**Option A: Use an existing local clone (if you have one)**
```shell
cd <path-to-your-local-odoo-documentation-clone>
git fetch origin
git diff origin/<major-1>.0 origin/<major>.0 -- <file>    # to see breaking changes
```

**Option B: Clone on demand**
```shell
# Clone just the detected major version branch to a temporary location:
git clone --branch <major>.0 --depth 1 https://github.com/odoo/documentation.git /tmp/odoo-docs-<major>

# Then diff against the previous major version:
git -C /tmp/odoo-docs-<major> fetch origin <major-1>.0:<major-1>.0
git -C /tmp/odoo-docs-<major> diff <major-1>.0 origin/<major>.0 -- <file>
```

## Addon/Module Structure

```
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

- `depends` must list every module whose models/views/security this addon relies on — missing deps cause load-order errors.
- Files in `data` load in the listed order; security CSV/XML must load before views that reference the groups/rules.

## ORM Patterns

### Extending vs creating models

```python
from odoo import models, fields, api


# Create a brand-new model
class MyModel(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    line_ids = fields.One2many("my.model.line", "model_id", string="Lines")
    active = fields.Boolean(default=True)


# Extend an existing model (adds fields/methods to it, does not create a new table)
class SaleOrder(models.Model):
    _inherit = "sale.order"

    my_custom_field = fields.Char(string="Custom Field")
```

- `_name` — defines a new model/table.
- `_inherit` alone (no `_name`) — extends an existing model in place (classic inheritance); adds fields/methods to `sale.order` itself.
- `_inherit` + a different `_name` — delegation inheritance (new model that also behaves like the base, via `_inherits` dict) — rare; prefer classic `_inherit` unless you specifically need a separate table with delegated fields.

### Computed / related fields

```python
class MyModel(models.Model):
    _name = "my.model"

    price_unit = fields.Float()
    quantity = fields.Float()
    subtotal = fields.Float(compute="_compute_subtotal", store=True)
    partner_id = fields.Many2one("res.partner")
    partner_country_id = fields.Many2one(related="partner_id.country_id", store=False)

    @api.depends("price_unit", "quantity")
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.price_unit * record.quantity
```

- `@api.depends(...)` must list every field the compute method reads — Odoo uses this to know when to recompute.
- `store=True` persists the computed value to the DB (needed for searching/grouping/reporting on it); `store=False` (default) computes on read only.
- `related` fields are a shortcut for a compute that just follows a relation chain — no method body needed.

### Constraints

```python
from odoo.exceptions import ValidationError


class MyModel(models.Model):
    _name = "my.model"

    start_date = fields.Date()
    end_date = fields.Date()

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError("Start date must be before end date.")
```

### `@api.model` vs recordset methods

```python
class MyModel(models.Model):
    _name = "my.model"

    @api.model
    def default_get(self, fields_list):
        # @api.model: no `self` recordset context needed (e.g. defaults, class-level helpers)
        res = super().default_get(fields_list)
        res["name"] = "Default Name"
        return res

    def action_confirm(self):
        # regular method: operates on `self` as a recordset — iterate for multi-record safety
        for record in self:
            record.write({"state": "confirmed"})
```

## View XML Conventions

### Form / tree / kanban / search views

```xml
<record id="view_my_model_form" model="ir.ui.view">
    <field name="name">my.model.form</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="name"/>
                    <field name="partner_id"/>
                </group>
                <notebook>
                    <page string="Lines">
                        <field name="line_ids"/>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>

<record id="view_my_model_tree" model="ir.ui.view">
    <field name="name">my.model.list</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <list>
            <field name="name"/>
            <field name="partner_id"/>
        </list>
    </field>
</record>

<record id="view_my_model_search" model="ir.ui.view">
    <field name="name">my.model.search</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <search>
            <field name="name"/>
            <filter string="Active" name="active" domain="[('active', '=', True)]"/>
            <group expand="0" string="Group By">
                <filter string="Partner" name="group_partner" context="{'group_by': 'partner_id'}"/>
            </group>
        </search>
    </field>
</record>
```

Note: newer Odoo versions renamed the `<tree>` root tag to `<list>` for list views — check the detected version's view arch conventions rather than assuming which tag is current.

### Inheritance via `xpath`

```xml
<record id="view_sale_order_form_inherit" model="ir.ui.view">
    <field name="name">sale.order.form.inherit.my.module</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="my_custom_field"/>
        </xpath>
    </field>
</record>
```

- `position`: `after`, `before`, `inside`, `replace`, `attributes`.
- Prefer `xpath` with a stable `expr` (field name, `//group[@name='...']`) over fragile positional XPath.

### `attrs`/`states` deprecated in Odoo 17+

Odoo 16 and earlier used `attrs`/`states` attributes for conditional visibility/readonly/required:

```xml
<!-- Odoo <= 16 style -->
<field name="my_custom_field" attrs="{'invisible': [('state', '!=', 'draft')]}"/>
```

Odoo 17+ replaced this with direct Python-like expressions evaluated against the record:

```xml
<!-- Odoo 17+ style -->
<field name="my_custom_field" invisible="state != 'draft'"/>
<field name="my_custom_field" readonly="state == 'done'"/>
<field name="my_custom_field" required="partner_id and not company_id"/>
```

If the detected version is 17+, do not write new `attrs`/`states` — use the direct expression form. If maintaining an addon still targeting <= 16, `attrs`/`states` remains correct; do not migrate it opportunistically outside the scope of the actual task.

## Security

### `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
access_my_model_manager,my.model.manager,model_my_model,my_module.group_my_module_manager,1,1,1,1
```

- `model_id:id` references the model's auto-generated external ID: `model_<model_name_with_underscores>`.
- Every model needs at least one access rule or all non-superuser access is denied by default.

### Record rules (row-level security)

```xml
<record id="my_model_rule_own_records" model="ir.rule">
    <field name="name">My Model: own records only</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('create_uid', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Groups

```xml
<record id="group_my_module_manager" model="res.groups">
    <field name="name">My Module / Manager</field>
    <field name="category_id" ref="base.module_category_operations"/>
</record>
```

## Common Pitfalls

- **SQL injection via raw `self.env.cr.execute`** — never string-format user input into SQL. Use parameterized queries: `self.env.cr.execute("SELECT id FROM my_table WHERE name = %s", (name,))`. Prefer the ORM (`search`, `read_group`) over raw SQL unless there's a proven performance need.
- **Multi-company field access** — respect `company_id` fields and the `allowed_company_ids` context; don't assume a single-company deployment. Add explicit company domains to `Many2one`/`search` calls where cross-company leakage is possible, and check `_check_company_auto`/`check_company` on relational fields.
- **Performance: looped `.write()` calls** — never call `.write()` per record inside a loop; batch instead:

```python
# ❌ WRONG — N writes, N transactions worth of overhead
for record in records:
    record.write({"state": "done"})

# ✅ CORRECT — one write across the whole recordset
records.write({"state": "done"})
```

Similarly, avoid `search()` calls inside a loop — fetch once outside and filter/iterate over the recordset in memory, or use `read_group`/`search_read` for aggregate needs.

## Local Development Environment Setup

### Multi-version setup for cross-version testing

Clone multiple Odoo major versions side by side to test an addon across versions:

```shell
git clone https://github.com/odoo/odoo.git -b 16.0 --depth 1 --origin upstream odoo16.0
git clone https://github.com/odoo/odoo.git -b 17.0 --depth 1 --origin upstream odoo17.0
git clone https://github.com/odoo/odoo.git -b 18.0 --depth 1 --origin upstream odoo18.0
git clone https://github.com/odoo/odoo.git -b 19.0 --depth 1 --origin upstream odoo19.0
```

The database manager is available at `http://localhost:<xmlrpc_port>/web/database/manager` (default `8069`; the port must match `xmlrpc_port` in `odoo.conf`).

### System dependencies

```shell
# Debian/Ubuntu — derive package list from Odoo's own debian/control file
sed -n -e '/^Depends:/,/^Pre/ s/ python3-\(.*\),/python3-\1/p' debian/control | sudo xargs apt-get install -y

# Fedora/RHEL
sudo dnf install postgresql-devel python-ldap python-devel openldap-devel

# Common extra deps + build tools (Debian/Ubuntu) when Python package builds fail
sudo apt-get install -y python-dev-is-python3 python3-dev libldap2-dev libsasl2-dev libssl-dev \
  build-essential wget git python3-pip python3-venv python3-wheel libfreetype6-dev libxml2-dev \
  libzip-dev python3-setuptools libjpeg-dev zlib1g-dev libpq-dev libxslt1-dev libtiff5-dev \
  libopenjp2-7-dev wkhtmltopdf
```

### Configuration (`odoo.conf`)

Copy the template from `odoo/debian/odoo.conf` to the project root, then edit:

```ini
[options]
; This is the password that allows database operations:
admin_passwd = <admin_passwd>
db_host = localhost
db_port = 5432
db_user = <db_user>
db_password = <db_password>
db_name = <database_name>
addons_path = addons,odoo/addons
default_productivity_apps = True
xmlrpc_port = 8069
```

Never commit a real `admin_passwd`/`db_password` — keep `odoo.conf` out of version control (or use placeholders and load real secrets via environment-specific, untracked config).

### Common odoo-bin commands

```shell
# init a new database with the base module
python odoo-bin -i base -d <db_name> -c odoo.conf

# run, pointing addons_path at both custom addons/ and the Odoo core addons/
python odoo-bin -c odoo.conf --addons-path addons,odoo/addons

# alternate form specifying db user/password/addons-path directly instead of via conf
python odoo-bin -r <db_user> -w <db_password> --addons-path=addons -d <db_name>

# scaffold a new module
python odoo-bin scaffold <module_name> <addons_dir>

# dev mode (auto-reload, useful QoL flags), without demo data
python odoo-bin -i base -c odoo.conf --without-demo=True
python odoo-bin -c odoo.conf --dev=all --without-demo=True

# update (upgrade) a specific module after code changes
python odoo-bin -c odoo.conf -u <module_name>
```

### Running as a systemd service

```ini
[Unit]
Description=Odoo Web Service
After=network.target

[Service]
Type=simple
User=<service_user>
WorkingDirectory=/home/<service_user>/odoo
ExecStart=/home/<service_user>/<python-env-path>/bin/python /home/<service_user>/odoo/odoo-bin -c /home/<service_user>/odoo.conf
Restart=always

[Install]
WantedBy=multi-user.target
```

If using a conda/virtualenv-managed Python (not system `python3`), point `ExecStart` at that environment's `python` binary explicitly — systemd does not source shell profiles or activation scripts.

### Module icon

`static/description/icon.png` (128x128px recommended) is the module's listing icon shown in the Apps grid.

### Manifest fields reference

- `author`, `website` — attribution shown in the Apps list; use placeholders like `<your-name>` / `<your-org-website>` rather than hardcoding real personal info in shared/example code.
- `license` — must be one of Odoo's recognized OSI/proprietary license keys: `GPL-2`, `GPL-2 or any later version`, `GPL-3`, `GPL-3 or any later version`, `AGPL-3`, `LGPL-3`, `Other OSI approved licence`, `OEEL-1` (Odoo Enterprise Edition License), `OPL-1` (Odoo Proprietary License), `Other proprietary`.
- `application: True` marks it as a top-level "App" (shows in the Apps main list); `False` for a supporting/technical module.
- `auto_install: False` — if `True`, the module installs automatically as soon as all its `depends` are installed (used for "glue" modules bridging two other modules); most addons should leave this `False`.
- `category` — freeform string, but check `odoo/addons/base/data/ir_module_category_data.xml` in the detected version's source for the standard category list before inventing a new one.
