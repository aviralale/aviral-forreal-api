# Aviral, for real — API

The Django REST backend for the [_Aviral, for real_](../aviral-unfiltered) blog.
A single-author publishing API: posts (Markdown body), categories, and tags. The
public API returns **published posts only**; writing and publishing happen in the
Django admin.

## Stack

- **Django** + **Django REST Framework**
- **django-filter** — category / tag / search filtering
- **django-cors-headers** — CORS for the Next.js frontend
- **Pillow** — cover uploads, re-encoded to **WebP/AVIF** before storage
- **django-storages + boto3** — media on **Cloudflare R2** in production
- **whitenoise** — static files under cPanel/Passenger
- SQLite in dev; **MySQL/MariaDB** in production via `DATABASE_URL` (`dj-database-url`, PyMySQL driver)

## Getting started

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env          # then set a real SECRET_KEY
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver    # http://localhost:8000
```

Write and publish posts at <http://localhost:8000/admin/>.

## Environment

`.env` ships with a **PRODUCTION** block active and a **DEVELOPMENT** block
commented at the bottom — to work locally, comment the four production lines
(`DEBUG`/`DATABASE_URL`/`ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS`) and uncomment the
dev block.

| Variable               | Default                 | Notes                                                       |
| ---------------------- | ----------------------- | ----------------------------------------------------------- |
| `SECRET_KEY`           | _(required)_            | Django secret key                                           |
| `DEBUG`                | `False`                 | `True` for local development                                |
| `DATABASE_URL`         | `sqlite:///db.sqlite3`  | `mysql://user:pass@host:3306/db?charset=utf8mb4` in prod    |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`   | Comma-separated (a leading `.` matches subdomains)          |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated frontend origins                            |
| `IMAGE_UPLOAD_FORMAT`  | `webp`                  | `webp` or `avif` — uploads re-encoded before storage        |
| `IMAGE_UPLOAD_QUALITY` | `80`                    | 1–100                                                       |
| `R2_*`                 | _(unset)_               | Cloudflare R2 media bucket; used only when `DEBUG=False`    |

Media: in dev, cover images convert to WebP and serve from `/media/`. In
production they convert and upload to **Cloudflare R2**, served from
`R2_PUBLIC_DOMAIN`.

## Deploying to cPanel

1. **MySQL** — in cPanel ▸ *MySQL® Databases*, create a database and user and
   grant the user all privileges. Use **utf8mb4** so emoji store correctly; if
   the DB isn't already utf8mb4, run in *phpMyAdmin*:
   ```sql
   ALTER DATABASE `cpaneluser_dbname`
     CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. **Python app** — cPanel ▸ *Setup Python App* ▸ Create: pick the Python
   version, set the application root to this folder, and the application URL.
   cPanel makes a virtualenv and detects `passenger_wsgi.py`.
3. **Env vars** — set them in the app's *Environment variables* UI, or edit the
   project-root `.env` (the production block is active by default; fill in your
   `DATABASE_URL`, `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`).
4. **Install + migrate** — from the app's virtualenv (cPanel shows the
   `source …/activate` command, or use its terminal):
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```
5. **Restart** the app from the Setup Python App page after any change.

Static files (admin, DRF browsable API) are served by WhiteNoise — no extra
web-server config needed. `PyMySQL` is the DB driver (pure-Python, so it
installs without build tools).

## API

Base path: `/api/`

### Public (read-only, no auth)

| Method | Endpoint                | Description                                  |
| ------ | ----------------------- | -------------------------------------------- |
| GET    | `/api/posts/`           | Published posts (paginated, 10/page)         |
| GET    | `/api/posts/{slug}/`    | Single post (includes `body`; bumps `views`) |
| GET    | `/api/categories/`      | All categories                               |
| GET    | `/api/tags/`            | All tags                                     |

**Query params** on `/api/posts/`: `?category=<slug>`, `?tag=<slug>`,
`?search=<text>`, `?page=<n>`, `?ordering=published_at|views`.

### Admin (token auth, staff only)

Powers the Next.js dashboard. `POST /api/auth/login/` returns a DRF token for a
**staff** user; send it as `Authorization: Token <token>` on the rest.

| Method            | Endpoint                     | Description                       |
| ----------------- | ---------------------------- | --------------------------------- |
| POST              | `/api/auth/login/`           | Staff login → `{ token }`         |
| POST              | `/api/auth/logout/`          | Invalidate the caller's token     |
| GET/POST          | `/api/admin/posts/`          | List (incl. drafts) / create      |
| GET/PATCH/DELETE  | `/api/admin/posts/{id}/`     | Retrieve / update / delete        |
| GET/POST          | `/api/admin/categories/`     | List / create                     |
| DELETE            | `/api/admin/categories/{id}/`| Delete                            |
| GET/POST          | `/api/admin/tags/`           | List / create                     |
| DELETE            | `/api/admin/tags/{id}/`      | Delete                            |

Post create/update accepts JSON or `multipart/form-data` (cover upload).
`category` is a primary key (nullable); `tags` is a list of primary keys;
setting `status` to `published` is what publishes a post.

### Behavior

- Only `status='published'` posts are ever returned.
- `reading_time` is computed on save (~200 wpm).
- `published_at` is set automatically the first time a post is published.
- `views` is incremented atomically with an `F()` expression (race-safe).
- `TIME_ZONE` is `Asia/Kathmandu`.
- Cover uploads are re-encoded to WebP/AVIF on save; dev serves them from
  `/media/`, production stores them on Cloudflare R2.

## Project layout

```
config/        settings, urls, wsgi/asgi
blog/
  models.py            Category, Tag, Post
  serializers.py       public list vs. detail (detail adds `body`)
  filters.py           category / tag / search
  views.py             read-only viewsets, F() view counter
  admin_serializers.py writable post/category/tag serializers
  admin_api.py         staff-only ModelViewSets (drafts + uploads)
  auth.py              staff token login / logout
  urls.py              public + /admin/ routers, /auth/ endpoints
  admin.py             Django admin (write + bulk "Publish" action)
```
# aviral-forreal-api
