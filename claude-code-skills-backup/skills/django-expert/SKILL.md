---
name: Django Expert
description: Senior Django specialist — Django 5.0, Django REST Framework, models, serializers, viewsets, ORM optimization, authentication, testing, and production best practices.
---

# Django Expert

Senior Django specialist — Django 5.0, Django REST Framework, models, serializers, viewsets, ORM optimization, authentication, testing, and production best practices.

## Core Workflow

1. **Analyze requirements** — Identify models, relationships, API endpoints
2. **Design models** — Create models with proper fields, indexes, managers → `makemigrations` + `migrate`
3. **Implement views** — DRF viewsets or Django 5.0 async views
4. **Validate endpoints** — Confirm status codes with APITestCase before adding auth
5. **Add auth** — Permissions, JWT authentication
6. **Test** — Django TestCase, APITestCase

---

## ⚠️ Strict Rules (MUST DO)

| Rule | Why |
|------|-----|
| `select_related` / `prefetch_related` for related objects | Prevent N+1 queries |
| Database indexes for frequently queried fields | Query performance |
| Environment variables for secrets | Security |
| Proper permissions on ALL endpoints | Authorization |
| Write tests for models and API endpoints | Reliability |
| Django's built-in security (CSRF, etc.) | Protection |

## ❌ MUST NOT DO

| Anti-Pattern | Why |
|-------------|-----|
| Raw SQL without parameterization | SQL injection |
| Skip database migrations | Schema drift |
| Store secrets in `settings.py` | Security breach |
| `DEBUG=True` in production | Information leak |
| Trust user input without validation | XSS, injection |
| Ignore query optimization | Performance degradation |

---

## Models & ORM

```python
# models.py
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    author = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="articles"
    )
    published_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-published_at"]
        indexes = [
            models.Index(fields=["author", "published_at"]),
            models.Index(fields=["is_published", "-published_at"]),
        ]

    def __str__(self):
        return self.title
```

### ORM Optimization

```python
# ✅ CORRECT — select_related for ForeignKey (single query)
articles = Article.objects.select_related("author").filter(is_published=True)

# ✅ CORRECT — prefetch_related for ManyToMany/reverse FK
authors = User.objects.prefetch_related("articles").all()

# ✅ CORRECT — Only fetch needed fields
Article.objects.only("title", "slug", "published_at").filter(is_published=True)

# ✅ CORRECT — Aggregate without loading objects
from django.db.models import Count
User.objects.annotate(article_count=Count("articles")).filter(article_count__gt=5)

# ❌ WRONG — N+1 query (hits DB for each article.author)
for article in Article.objects.all():
    print(article.author.username)  # N+1!
```

### Custom Manager

```python
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)


class Article(models.Model):
    # ...
    objects = models.Manager()  # Default
    published = PublishedManager()  # Article.published.all()
```

---

## DRF Serializers

```python
# serializers.py
from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "slug", "content", "author_username", "published_at"]
        read_only_fields = ["slug", "published_at"]

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value.strip()

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["title"])
        return super().create(validated_data)


class ArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "slug", "author_username", "published_at"]
```

---

## ViewSets & Views

### ModelViewSet

```python
# views.py
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer, ArticleListSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """
    CRUD for articles.
    - List/Retrieve: public
    - Create/Update/Delete: authenticated only
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_published", "author"]
    search_fields = ["title", "content"]
    ordering_fields = ["published_at", "title"]
    lookup_field = "slug"

    def get_queryset(self):
        return Article.objects.select_related("author").all()

    def get_serializer_class(self):
        if self.action == "list":
            return ArticleListSerializer
        return ArticleSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

### Django 5.0 Async Views

```python
# views.py
from django.http import JsonResponse
from .models import Article


async def article_list(request):
    articles = [
        {"title": article.title, "slug": article.slug}
        async for article in Article.published.all()
    ]
    return JsonResponse({"articles": articles})
```

### URL Configuration

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet, basename="article")

urlpatterns = router.urls
```

---

## Authentication (SimpleJWT)

```bash
pip install djangorestframework-simplejwt
```

```python
# settings.py
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}
```

```python
# urls.py
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
]
```

### Custom Permissions

```python
from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.author == request.user
```

---

## Testing

```python
# tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Article


class ArticleAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass")
        self.article = Article.objects.create(
            title="Test Article",
            slug="test-article",
            content="Content here",
            author=self.user,
            is_published=True,
        )

    def test_list_public(self):
        res = self.client.get("/api/articles/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_create_requires_auth(self):
        res = self.client.post("/api/articles/", {"title": "New"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_authenticated(self):
        self.client.force_authenticate(self.user)
        res = self.client.post("/api/articles/", {
            "title": "Hello Django",
            "content": "Great content",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["author_username"], "alice")

    def test_update_only_author(self):
        other_user = User.objects.create_user("bob", password="pass")
        self.client.force_authenticate(other_user)
        res = self.client.patch(f"/api/articles/{self.article.slug}/", {"title": "Hacked"})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
```

### pytest-django

```python
# conftest.py
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    from django.contrib.auth.models import User
    return User.objects.create_user("testuser", password="testpass")


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client
```

---

## Production Settings

```python
# settings/production.py
import os

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ.get("DB_PORT", "5432"),
        "CONN_MAX_AGE": 600,
    }
}

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ["REDIS_URL"],
    }
}
```

---

## Project Structure

```
project/
├── config/                 # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── articles/
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

---

## Quick Reference

| Task | Command/Pattern |
|------|----------------|
| New project | `django-admin startproject config .` |
| New app | `python manage.py startapp articles` |
| Migrations | `makemigrations` → `migrate` |
| Create superuser | `createsuperuser` |
| Run tests | `python manage.py test` or `pytest` |
| Shell | `python manage.py shell_plus` (django-extensions) |
| Check deployment | `python manage.py check --deploy` |

| Package | Purpose |
|---------|---------|
| `djangorestframework` | REST API framework |
| `djangorestframework-simplejwt` | JWT authentication |
| `django-filter` | Queryset filtering |
| `drf-spectacular` | OpenAPI schema generation |
| `django-cors-headers` | CORS handling |
| `django-extensions` | shell_plus, etc. |
| `pytest-django` | Testing with pytest |
| `factory-boy` | Test data factories |

---

## สรุป

1. **Models** — indexes, `select_related`/`prefetch_related`, custom managers
2. **Serializers** — validation, read-only fields, separate list/detail serializers
3. **ViewSets** — permissions, filtering, search, ordering, `perform_create`
4. **Auth** — SimpleJWT, custom permissions, `IsAuthorOrReadOnly`
5. **Testing** — APITestCase, force_authenticate, status code assertions
6. **Production** — env vars, security headers, PostgreSQL, Redis cache
7. **Never** — raw SQL without params, DEBUG=True in prod, secrets in settings.py
