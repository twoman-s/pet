# Copilot Instructions for Pet Project

## Architecture Overview

This is a **Django 5.2 REST API** for expense management with user authentication. Key architectural decision: data is user-scoped (each expense belongs to a user via FK).

**Core Structure:**

- **`pet/`** – Django project settings & configuration
- **`authentication/`** – Email/password login via `allauth`; no models (uses Django auth)
- **`expense_manager/`** – Two models: `Expense` (per-user transactions) and `Tag` (global, reusable)
- **`utils/`** – Shared utilities (e.g., `DynamicFieldsModelSerializer` for field filtering)

**Why this layout:** Separation of concerns allows the authentication module to be swapped or extended independently. Expense manager is self-contained with its own serializers/views.

## Critical Data Flows

### User Authentication

- **Entry:** `POST /api/v1/auth/login/` (email + password)
- **Handler:** `authentication.views.EmailLoginView` → `EmailPasswordLoginSerializer`
- **Auth Strategy:** Django session auth + optional JWT (configured but not exposed by default)
- **Key File:** `authentication/serializers/email_login.py`

### Expense CRUD & Tag Handling

- **Routes:** `GET/POST /api/v1/expenses/` and `GET/POST /api/v1/tags/`
- **ViewSets:** `ExpenseViewSet` & `TagViewSet` use DRF's `DefaultRouter`
- **Permission Pattern:** Custom `IsOwner` in `expense_manager/views/expense.py` ensures users only access their own expenses
- **Tag Workflow:** Tags are global; `write_tags` field accepts list of tag names → serializer auto-creates or fetches via `_get_or_create_tags()`
- **Bulk Create:** Special `@action` method at `/api/v1/expenses/bulk_create/` handles atomic M2M setup

### Serializer Pattern

`ExpenseSerializer` demonstrates a non-standard but effective pattern:

- **Read field:** `tags` (SerializerMethodField) returns list of tag names
- **Write field:** `write_tags` (ListField) accepts tag names and creates/links them
- This separates input/output concerns while sharing one serializer

## Project-Specific Conventions

### Serializer Organization

- Serializers live in `{app}/serializers/` with module-level imports via `__init__.py`
- Custom base: `DynamicFieldsModelSerializer` in `utils/common_serializer.py` supports `?fields=id,name` query params to dynamically limit response fields
- Usage: Pass `override_fields` kwarg to add required fields; query params filter further

### View Organization

- Views live in `{app}/views/` with module-level imports
- Use DRF's `DefaultRouter` for automatic URL generation (see `expense_manager/urls.py`)
- Custom permissions inherit `permissions.BasePermission` and implement `has_object_permission()`

### Database & ORM Patterns

- `Expense` uses `user_id` FK directly in `get_queryset()` for filtering
- M2M tags use `.set()` for bulk assignment (not `.add()` in a loop)
- Use `transaction.atomic()` for operations that manipulate both foreign keys and M2M in one request (e.g., bulk_create)

### API Response Format

- Controlled by DRF `drf_spectacular` + custom `REST_FRAMEWORK` settings in `pet/drf_settings.py`
- Schema available at `/api/v1/schema/`; Swagger UI at `/api/v1/docs/`
- Default pagination: 20 items per page (configurable)

## Development & Deployment

### Running Locally

```bash
python manage.py migrate           # Apply DB migrations
python manage.py runserver 8000   # Dev server (default port)
```

### Docker

- **Image:** Python 3.12 slim base
- **Port:** 8811 (matches `docker-compose.yml`)
- **Entry:** Runs migrations + collectstatic + development server
- **Production:** Commented gunicorn command ready (uses Uvicorn workers for async support)

### Dependencies to Know

- `djangorestframework` – REST API framework
- `django-allauth` – OAuth/session auth (Google SSO configured but email/password used in current auth flow)
- `drf-spectacular` – OpenAPI schema generation
- `psycopg2-binary` – PostgreSQL adapter
- `djangorestframework_simplejwt` – JWT auth (installed but not actively exposed)

### Common Commands

```bash
python manage.py makemigrations   # Create new migrations
python manage.py migrate           # Apply migrations
python manage.py createsuperuser  # Admin user
python manage.py shell            # Django shell
```

## Environment & Security

- Settings read from environment variables (`.env` file or Docker env)
- Key vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`
- CORS enabled; reverse-proxy headers supported (`USE_X_FORWARDED_HOST`, `SECURE_PROXY_SSL_HEADER`)

## Cross-App Integration Points

1. **`settings.py`** – Central config; INSTALLED_APPS order matters (middleware auth depends on app order)
2. **`urls.py`** – Routes to both apps; future endpoints go here
3. **`utils/common_serializer.py`** – Shared across apps; modify carefully to test impact on both serializers

## Testing & Debugging Tips

- Admin interface at `/admin/` for quick model inspection
- Use DRF's browsable API (`/api/v1/expenses/`) for manual testing
- Expense objects must be tied to a user; test with authenticated requests
- Tag creation is lazy (happens during Expense.save with M2M), so inspect migration files if M2M changes

## Future Considerations

- JWT endpoints are configured but commented; uncomment to expose token endpoints
- Google OAuth configured but not currently wired into login flow
- Database defaults to SQLite; use PostgreSQL in production (psycopg2 already installed)
