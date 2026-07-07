# Week 2 — What Was Built & Changed

## ⚠️ Critical fix applied (do this first)
Your `settings.py` had your real Neon DB password and Django SECRET_KEY hardcoded
directly in the file. This has been moved into `.env` (already created for you,
already in `.gitignore`). **If you already pushed the old settings.py to GitHub,
tell Claude — you should rotate your Neon password since it may be in your git history.**

## Auth changes (Milestone 2 patch)
Your frontend forms use `name` + `email` (no username field), so the backend was
adjusted to match instead of changing your UI:
- `accounts/models.py` — added a `name` field to `User`
- `accounts/serializers.py` — `RegisterSerializer` now takes `name`/`email` and
  auto-generates a unique `username` behind the scenes; `LoginSerializer` now
  authenticates with `email` instead of `username`
- Added `GET /api/auth/users/?role=investor` (or `entrepreneur`) so the frontend
  can list people to invite to a meeting

**You must run migrations again** since a field was added:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

## Milestone 3 — Meeting Scheduling (new `meetings` app)
- `Meeting` model: organizer, participant, title, description, start/end time,
  status (pending/accepted/rejected/cancelled/completed), auto-generated `room_name`
  (used later to join the video call)
- Conflict detection: you can't create *or accept* a meeting that overlaps
  another pending/accepted meeting for either person
- Endpoints:
  - `GET/POST /api/meetings/` — list mine, or schedule a new one
  - `GET/DELETE /api/meetings/<id>/`
  - `POST /api/meetings/<id>/accept/`
  - `POST /api/meetings/<id>/reject/`
  - `POST /api/meetings/<id>/cancel/`

## Milestone 4 — Video Calling (new `calls` app, Django Channels)
- WebSocket signaling server at `ws://.../ws/call/<room_name>/?token=<jwt>`
- Relays WebRTC offer/answer/ICE candidates between the two people in a meeting
- Uses Google's public STUN server (no TURN server — fine for same-network/basic
  calls per the task's "Basic" scope; a TURN server would be a Week 4+ upgrade)
- **New dependency**: `channels`, `daphne` — install with
  `pip install channels daphne`
- Runs automatically through `python manage.py runserver` once installed (Daphne
  takes over automatically since it's in `INSTALLED_APPS`)

## Milestone 5 — Document Processing Chamber (new `documents` app)
- `Document` model: title, file, version, status, optional link to a meeting,
  e-signature image + who signed + when
- File storage: local disk under `/media/` in dev (swap `MEDIA_ROOT` for an
  S3 storage backend later if you want cloud storage, per the task's "Multer/S3" note)
- Endpoints:
  - `GET/POST /api/documents/` — list mine, or upload a new one (multipart)
  - `GET/DELETE /api/documents/<id>/`
  - `POST /api/documents/<id>/sign/` — attach a signature image, marks it "signed"

## Frontend changes
- `src/api/` — new folder: `client.ts` (axios + JWT + auto-refresh), `auth.ts`,
  `meetings.ts`, `documents.ts`, `users.ts`
- `AuthContext.tsx` — rewritten to call the real Django backend instead of the
  mock `localStorage`/`users.ts` data
- `LoginPage.tsx` — small fix so it redirects based on the account's *real* role
  instead of blindly trusting the role toggle button
- New pages: `pages/meetings/MeetingsPage.tsx`, `pages/call/VideoCallPage.tsx`
- `pages/documents/DocumentsPage.tsx` — rewritten to actually upload/list/preview/
  sign documents against the backend, includes a small canvas-based signature pad
- `Sidebar.tsx` — added a "Meetings" nav link for both roles
- `App.tsx` — added `/meetings` and `/call/:roomName` routes
- New `.env` — `VITE_API_URL=http://127.0.0.1:8000/api`

## What to test (in order)
1. Re-run migrations (see Auth changes above), confirm register/login still work
   in Postman with the new `name`/`email` shape
2. `npm install` in the frontend (no new packages needed, just to be safe)
3. `pip install channels daphne` in the backend
4. Start backend: `python manage.py runserver`
5. Start frontend: `npm run dev`
6. Register two accounts (one investor, one entrepreneur) through the real UI
7. As one, schedule a meeting with the other
8. Log in as the other, accept it, click "Join Call" — open it in a second
   browser (or incognito window) logged in as the first person, confirm video connects
9. Upload a document, preview it, draw a signature, confirm it saves

## Known limitations (honest, so nothing surprises you in the demo)
- Video calling has no TURN server, so it may not connect across very
  restrictive networks/firewalls — works fine on the same Wi-Fi/network
- Channels uses `InMemoryChannelLayer` — fine for one dev server, would need
  `channels_redis` for a real multi-server production deployment
- 2FA, payments, and final deployment are still Week 3 — not part of this pass
