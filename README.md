# Learn Swiss German — SwissSpeak

SwissSpeak is a dialogue-led platform for German speakers who want to understand and join everyday Swiss German conversations. It pairs a realistic dialogue in a chosen Swiss dialect with Standard German and a support language (English or Spanish), a winding "mountain journey" of lessons with server-graded checkpoints, spaced-repetition reviews, and lazily generated per-turn audio — all backed by MongoDB.

> The original specification lives in [`docs/specification/`](docs/specification/README.md). Implementation notes, deliberate deviations and the remaining **manual TODO** are in [`docs/IMPLEMENTATION-NOTES.md`](docs/IMPLEMENTATION-NOTES.md).

## What it does

It lets learners browse published Swiss German topics and dialogues, enroll in a dialect-specific learning path, complete short lessons with a real scored assessment, keep a streak, and hear AI-generated audio for individual turns. Editors and publishers manage content, and an administrator manages roles, AI routes and configuration.

## Why it exists

Swiss German resources are fragmented and rarely teach how conversations actually sound across dialects. SwissSpeak packages curated, versioned content into a browsable app with honest dialect labelling, server-owned progress, and a clear path from "I know some German" to confident participation in familiar situations.

## Features

- Dialogue-led lessons (Understand → Notice → Rehearse → Respond → Recall) with server-side grading
- Mountain journey: stages, nodes, summit checkpoints, prerequisite unlocking
- Magic-link sign-in (no passwords), rotating sessions, CSRF protection
- Spaced-repetition reviews, XP reward ledger and local-day streaks
- Lazy per-turn audio generated on first request, cached in GridFS and reused
- Dialect-aware content with explicit "dialect not verified" labelling for legacy text
- Topics, subtopics, dialogues, patterns, vocabulary, daily phrase/dialogue
- Admin API for content lifecycle, publishing gates, creators, users and audit
- Idempotent database setup, deterministic legacy migration, and automated tests

## How it works

1. All runtime content, user data, durable jobs and media live in **MongoDB** (audio bytes in **GridFS**). Local `data-json/` is only a migration input.
2. A **FastAPI** app exposes a versioned `/api/v1` contract; legacy `/content/*` routes keep old links working.
3. The **React** frontend talks only to the API, using Secure HttpOnly cookies for sessions.
4. Content is immutable once published (revisions + published pointer). Grading answer keys stay server-only.
5. Audio is generated lazily by a durable job worker, stored in GridFS, and streamed with range/ETag support.

## Tech stack

- React · TypeScript · Vite · Tailwind CSS · TanStack Query
- FastAPI · PyMongo (async) · GridFS · MongoDB replica set
- LiteLLM (text) behind an app-owned AI gateway; pluggable speech provider
- pytest (integration tests against a real ephemeral Mongo replica set)

## Project structure

```text
backend/
  app/
    config.py            environment + settings
    common/              ids, time, errors, security, serialization, tracing
    db/                  async client, schema (collections/validators/indexes), tx helper
    auth/                magic links, sessions, RBAC, rate limiting, email adapter
    content/             canonicalization, migration, discovery service, routers
    learning/            grading, enrollment/attempts/rewards/reviews, curriculum builder
    media/               audio fingerprint, lazy generation, GridFS streaming
    ai/                  capability gateway + fake/LiteLLM providers
    jobs/                durable queue + fenced-lease worker
    admin/               admin API + audit
    main.py              app factory (lifespan, routers, health)
  scripts/               setup_database, import_legacy, seed, build_curriculum,
                         bootstrap_admin, worker, setup_all.sh
  tests/                 auth, content, learning, audio, migration, canonical
frontend/
  src/
    lib/api.ts           typed API client (content, auth, learning, audio)
    contexts/            magic-link auth, light UI state
    pages/               Home, Topics, Conversation, Learn, LessonRunner, Auth, ...
    components/          Navigation, TurnAudioButton, shared UI
data-json/               legacy content (migration input only)
docs/specification/      the source specification
```

## Getting started

```bash
git clone <repo-url>
cd learn-swiss-german
```

### MongoDB (replica set required — transactions)

Any MongoDB replica set works (including a single-node one for local dev). Point
`MONGODB_URI` at it. A local single-node example:

```bash
mongod --dbpath /path/to/data --replSet rs0 --bind_ip 127.0.0.1
# then once: mongosh --eval 'rs.initiate()'
```

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r pip/requirements-app.txt
cp .env.example .env            # edit MONGODB_URI if needed

# create schema + indexes, migrate legacy content, seed, build curriculum
bash scripts/setup_all.sh
python -m scripts.setup_database --check    # should report OK

python main.py                  # API on :5206 (in-process audio worker)
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE=http://localhost:5206
npm run dev                     # app on :5306
```

Open:

- Frontend: `http://localhost:5306`
- API: `http://localhost:5206`
- API docs: `http://localhost:5206/docs`

Create an administrator (one-time), then sign in with a magic link:

```bash
cd backend && python -m scripts.bootstrap_admin --email you@example.com
```

## Configuration

Backend (`backend/.env`) — see `.env.example`:

```env
MONGODB_URI=mongodb://127.0.0.1:27017/?replicaSet=rs0
MONGODB_DATABASE=swissspeak
PUBLIC_WEB_BASE_URL=http://localhost:5306
PUBLIC_API_BASE_URL=http://localhost:5206
ALLOWED_ORIGINS=http://localhost:5306,http://127.0.0.1:5306
EMAIL_PROVIDER=console        # console logs the link in dev; wire a real provider for prod
SPEECH_PROVIDER=fake          # deterministic offline audio; approve a real voice before launch
AI_TEXT_PROVIDER=fake         # set to litellm + a key for real generation
```

Frontend (`frontend/.env`):

```env
VITE_API_BASE=http://localhost:5206
```

## Usage

1. Start MongoDB, the backend and the frontend.
2. Browse topics and open a dialogue; sign in to hear per-turn audio.
3. Open **Learn** to start the mountain journey, complete a lesson and pass its check.
4. Use the admin API (as a publisher/administrator) to author and publish content.

## Development

```bash
cd frontend && npm run dev          # dev server
cd frontend && npm run build        # production build
cd frontend && npm run lint         # eslint
cd backend  && source .venv/bin/activate && pytest   # integration tests (needs a Mongo replica set)
cd backend  && python -m scripts.setup_database --check   # verify schema/index manifest
```

Tests run against the database named in `MONGODB_DATABASE` suffixed `_test`
(rebuilt and dropped per session). See `docs/IMPLEMENTATION-NOTES.md` for the
acceptance-test mapping.

## Roadmap

- Human-reviewed Zürich/Bern lessons and an approved speech voice per dialect
- `/admin` UI, `/review`, `/profile`, `/creators` pages and a dialect switcher
- Google/Microsoft sign-in, native mobile (PKCE) and offline sync (interfaces reserved)

## Contributing

This project is public and open for collaboration. If you're interested in contributing, improving the project, or discussing ideas, feel free to reach out.

LinkedIn: https://linkedin.com/in/alexrada

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Open a pull request

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
