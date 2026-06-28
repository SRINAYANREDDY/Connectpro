# ConnectPro 🔗

A professional social media platform built with Django — like LinkedIn but open-source.

## Features

- **Accounts** — Email login, custom profiles, follow/unfollow, follow requests for private accounts, block users, education history, skills, projects with AI rating via Claude API, dark/light mode
- **Posts** — Text + image + video posts, threaded comments, likes, bookmarks, hashtag extraction, hide post from specific users
- **Stories** — 24-hour auto-expiring stories, view tracking, image/video support
- **Notifications** — Real-time WebSocket notifications (like, comment, follow, follow request, accepted), unread badge
- **Search & Explore** — Search users/posts/hashtags, trending topics, suggested users

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python Django 4.2, DRF, Django Channels |
| Frontend | Plain HTML, CSS (no frameworks), Vanilla JS |
| Database | PostgreSQL (SQLite fallback for dev) |
| Real-time | WebSockets via Django Channels + Redis |
| AI | Anthropic Claude API (project rating) |
| Deployment | Render.com |

## Quick Start (Local)

```bash
# 1. Clone & enter project
cd connectpro

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your values (see below)

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. (Optional) Load sample data
python manage.py create_sample_data

# 8. Start server
python manage.py runserver
```

Or just run `bash start.sh` which does everything automatically.

## Environment Variables (.env)

```env
SECRET_KEY=your-long-random-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (optional for dev, SQLite used if not set)
DATABASE_URL=postgresql://user:password@localhost:5432/connectpro

# Redis (required for WebSocket notifications)
REDIS_URL=redis://localhost:6379

# Anthropic AI (required for project rating feature)
ANTHROPIC_API_KEY=sk-ant-...
```

## Deploy to Render.com

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo — Render will auto-detect `render.yaml`
4. Add your `ANTHROPIC_API_KEY` in the Render dashboard environment variables
5. Deploy — database and Redis are auto-provisioned

## Project Structure

```
connectpro/
├── manage.py
├── requirements.txt
├── .env.example
├── render.yaml          ← Render deployment config
├── start.sh             ← Local dev startup script
├── connectpro/
│   ├── settings/
│   │   ├── base.py      ← All settings
│   │   └── production.py← Production overrides
│   ├── urls.py
│   ├── asgi.py          ← WebSocket routing
│   ├── templates/
│   │   ├── base.html    ← Main layout (sidebar, navbar, dark mode)
│   │   └── partials/
│   │       ├── navbar.html
│   │       ├── sidebar.html
│   │       └── post_card.html
│   └── static/
│       ├── css/main.css ← Full CSS with dark mode
│       └── js/main.js   ← Likes, bookmarks, comments, WebSocket
└── apps/
    ├── accounts/        ← Users, follows, blocks, projects, skills
    ├── posts/           ← Posts, comments, likes, bookmarks, hashtags
    ├── stories/         ← 24hr stories with view tracking
    ├── notifications/   ← Real-time WebSocket notifications
    └── search/          ← Search + Explore page
```

## AI Project Rating

The project rating feature calls the Claude API and returns:
- Rating out of 10
- Detailed feedback paragraph
- List of strengths
- List of improvement suggestions

Requires `ANTHROPIC_API_KEY` to be set. Works on each project on your profile page.

## WebSocket Notifications

Notifications are sent in real-time via WebSockets when:
- Someone likes your post
- Someone comments on your post
- Someone follows you
- Someone sends a follow request
- Someone accepts your follow request

Redis must be running locally for this to work (`redis-server`). On Render, Redis is auto-provisioned.

## Admin Panel

Visit `/admin` with your superuser credentials to manage all models.

## Sample Accounts (after running `create_sample_data`)

| Email | Password |
|---|---|
| alice@example.com | password123 |
| bob@example.com | password123 |
| carol@example.com | password123 |
