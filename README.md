# Nexus Platform — Backend

Django REST Framework backend for **Nexus**, an Investor & Entrepreneur collaboration
platform. Built as part of a Full Stack Development Internship (Developers Hub).

**Live API:** https://web-production-f80ee.up.railway.app/api/
**Live app (frontend):** https://nexus-five-tau.vercel.app

## Tech Stack
- Django + Django REST Framework
- PostgreSQL (hosted on Neon)
- JWT authentication (djangorestframework-simplejwt)
- Django Channels + Daphne (WebSocket signaling for video calls)
- Deployed on Railway

## Features (Week 1 + 2)

**Authentication & Profiles**
- JWT-based register/login (email + password)
- Role-based accounts: investor vs entrepreneur
- Profile with bio, preferences, startup/investment history

**Meeting Scheduling**
- Schedule, accept, reject, cancel meetings
- Automatic conflict detection (no double-booking)

**Video Calling (Basic)**
- WebRTC signaling over WebSocket (Django Channels)
- Join a call tied to an accepted meeting
- Mute/camera toggle, end call

**Document Processing Chamber**
- Upload, preview, and delete documents
- E-signature: draw and attach a signature image, marks document as signed

## API Overview

| Endpoint | Method | Description |
|---|---|---|
| `/api/auth/register/` | POST | Create account (name, email, password, role) |
| `/api/auth/login/` | POST | Login (email, password) → JWT tokens |
| `/api/auth/refresh/` | POST | Refresh an expired access token |
| `/api/auth/profile/me/` | GET/PUT | View/update own profile |
| `/api/auth/profile/<id>/` | GET | View another user's public profile |
| `/api/auth/users/?role=` | GET | List users by role (for picking meeting participants) |
| `/api/meetings/` | GET/POST | List my meetings / schedule a new one |
| `/api/meetings/<id>/` | GET/DELETE | View or delete a meeting |
| `/api/meetings/<id>/accept/` | POST | Accept a meeting request |
| `/api/meetings/<id>/reject/` | POST | Reject a meeting request |
| `/api/meetings/<id>/cancel/` | POST | Cancel a meeting |
| `/api/documents/` | GET/POST | List / upload documents |
| `/api/documents/<id>/` | GET/DELETE | View or delete a document |
| `/api/documents/<id>/sign/` | POST | Attach an e-signature |
| `ws://.../ws/call/<room_name>/` | WebSocket | Video call signaling (WebRTC offer/answer/ICE) |

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host
DB_PORT=5432
```

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Deployment
- **Backend:** Railway (auto-deploys on push to `main`)
- **Database:** Neon PostgreSQL
- **Frontend:** Vercel

## Known Limitations
- Video calling uses a STUN server only (no TURN server) — works on most networks, may fail on very restrictive/corporate networks
- Uploaded documents are stored on local disk; on Railway's free tier this is not guaranteed to persist across redeploys (would need AWS S3 for permanent production storage)
- Channels uses an in-memory layer, suitable for a single dev/demo instance (would need Redis for a multi-server production setup)

## Documentation
- `CHANGES_WEEK2.md` — detailed technical log of everything built in Week 2

