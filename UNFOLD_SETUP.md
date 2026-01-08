# Django Unfold Admin Theme Installation

## What Changed

Your Django admin panel has been upgraded with the modern **django-unfold** theme! 🎨

## Changes Made

### 1. **requirements.txt**

- Added `django-unfold==0.47.0`

### 2. **pet/settings.py**

- Added `"unfold"` and `"unfold.contrib.filters"` at the top of `INSTALLED_APPS` (must be before `django.contrib.admin`)
- Added extensive `UNFOLD` configuration with:
  - Custom site title: "Pet Expense Manager"
  - Site icon: 📊
  - Custom purple color scheme
  - Structured sidebar navigation with icons:
    - Dashboard
    - Expense Management (Expenses, Tags, Bank Accounts, Items, Currencies)
    - User Management (Users, Groups)
  - Environment badge (shows Development/Production)

### 3. **pet/utils.py** (new file)

- Created `environment_callback()` function to show environment badges:
  - Red "Development" badge when DEBUG=True
  - Green "Production" badge when DEBUG=False

### 4. **expense_manager/admin.py**

- Replaced simple registrations with full `ModelAdmin` classes using `unfold.admin.ModelAdmin`
- Added admin configurations for:
  - **TagAdmin**: List display, filters, search
  - **ExpenseAdmin**: List display, filters, search, date hierarchy, horizontal filter for tags
  - **BankAccountAdmin**: List display, search
  - **ItemAdmin**: List display, search, filters
  - **CurrencyAdmin**: List display, search
  - **ExpenseItemAdmin**: List display, search, filters

### 5. **pet/urls.py**

- Added custom admin site headers and titles

## Next Steps

### If using Docker:

```bash
# Rebuild the Docker image to include django-unfold
docker build -t pet:latest .

# Restart the container
docker-compose up -d

# Collect static files (if needed)
docker exec pet_django_app python manage.py collectstatic --noinput
```

### If running locally:

```bash
# Install the package
pip install django-unfold

# Or if using virtual environment
source /venv/bin/activate  # or your venv path
pip install django-unfold

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (if any)
python manage.py migrate

# Start the server
python manage.py runserver
```

## Access the New Admin

Navigate to: **http://localhost:8811/admin/**

You'll see:

- ✅ Modern, clean interface
- ✅ Sidebar navigation with icons
- ✅ Dark mode support
- ✅ Responsive design
- ✅ Better tables and forms
- ✅ Search functionality
- ✅ Environment badge (Dev/Prod)

## Customization

You can customize the theme further in `pet/settings.py` under the `UNFOLD` dictionary:

- **Colors**: Change the primary color scheme
- **Navigation**: Add/remove/reorder sidebar items
- **Icons**: Use Material Icons (https://fonts.google.com/icons)
- **Logo**: Add your site logo (`SITE_LOGO` and `SITE_ICON`)
- **Tabs**: Enable tabs for related models

## Documentation

Full documentation: https://unfoldadmin.com/docs/

Enjoy your new beautiful admin interface! 🚀
