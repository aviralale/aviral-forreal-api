# Aviral, for real — API

The Django REST backend for the [_Aviral, for real_](../aviral-unfiltered) blog.
A single-author publishing API: posts (Markdown body), categories, and tags. The
public API returns **published posts only**; writing and publishing happen in the
Django admin.

## Stack

- **Django** + **Django REST Framework**
- **django-filter** — category / tag / search filtering
- **django-cors-headers** — CORS for the Next.js frontend
- **Pillow** — cover image uploads
- SQLite by default; Postgres via `DATABASE_URL` (`dj-database-url`)

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

| Variable               | Default                       | Notes                                   |
| ---------------------- | ----------------------------- | --------------------------------------- |
| `SECRET_KEY`           | _(required)_                  | Django secret key                       |
| `DEBUG`                | `False`                       | `True` for local development            |
| `DATABASE_URL`         | `sqlite:///db.sqlite3`        | Any `dj-database-url` URL               |
| `ALLOWED_HOSTS`        | `localhost,127.0.0.1`         | Comma-separated                         |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000`       | Comma-separated frontend origins        |

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
- In development, media (cover images) is served from `/media/`.

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
