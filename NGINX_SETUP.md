# Django + Nginx + Gunicorn Setup

## What Changed

This setup now uses:

- **Nginx** as a reverse proxy to serve static/media files and proxy requests to Django
- **Gunicorn** as the WSGI server (instead of runserver) for production-ready serving
- Proper static file collection and serving

## Architecture

```
Client Request (port 8811)
    ↓
Nginx (listens on 8811)
    ├─→ /static/* → Serves from /app/staticfiles/
    ├─→ /media/*  → Serves from /app/media/
    └─→ /*        → Proxies to Gunicorn (port 8000)
                        ↓
                    Django App
```

## Files Created/Modified

1. **nginx.conf** - Nginx configuration

   - Listens on port 8811
   - Serves static files from `/app/staticfiles/`
   - Serves media files from `/app/media/`
   - Proxies application requests to Gunicorn on port 8000

2. **entrypoint.sh** - Container startup script

   - Runs migrations
   - Collects static files to `/app/staticfiles/`
   - Starts nginx
   - Starts gunicorn with 3 workers

3. **Dockerfile** - Updated to:

   - Install nginx
   - Install gunicorn
   - Copy nginx config
   - Make entrypoint executable
   - Create static/media directories

4. **docker-compose.yml** - Updated to:
   - Add volumes for static and media files (persistence)

## Build and Run

```bash
# Build the image
docker build -t pet:latest .

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f
```

## Accessing the Application

- Application: http://localhost:8811/
- Admin panel: http://localhost:8811/admin/ (with CSS working!)
- API: http://localhost:8811/api/v1/
- Health check: http://localhost:8811/health

## Static Files

Static files are collected to `/app/staticfiles/` and served by nginx at `/static/`.
The Django admin CSS/JS will now load properly.

## Environment Variables

Make sure your `.env` file has:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
STATIC_URL=/static/
STATIC_ROOT=/app/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/app/media
```
