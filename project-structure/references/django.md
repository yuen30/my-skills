Read when placing code or apps in a Django / Django REST Framework project.

# Django Project Structure

```text
project/
├── config/                 # Project settings (composition root)
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── articles/           # One Django app per domain area
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── filters.py
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_serializers.py
│   │   └── admin.py
│   └── users/
│       ├── models.py
│       └── ...
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── docker-compose.yml
```

- Settings split per environment under `config/settings/`; `base.py` holds shared settings.
- Each app under `apps/` owns its models, serializers, views, URLs, permissions, filters, admin, and tests.
- Tests live in the app's `tests/` package, one `test_<module>.py` per module under test.
- Requirements split per environment under `requirements/`.
