# SwissSpeak — implementation notes, decision log & manual TODO

This document accompanies the SwissSpeak expansion built against
`docs/specification/`. It records what was implemented, deliberate deviations,
and the manual follow-ups required before a real public launch.

## What was implemented (working, tested)

**Backend (`backend/app/`, FastAPI + MongoDB, PyMongo async + GridFS)**

- Config, structured logging, request IDs, typed error envelope, health
  (`/health/live`, `/health/ready`).
- Full MongoDB setup: 32 collections with JSON-Schema validators + 65 named
  indexes, encoded in `app/db/schema.py` and applied idempotently by
  `scripts/setup_database.py --apply|--check`.
- Deterministic, idempotent legacy migration (`scripts/import_legacy.py`):
  9 topics, 120 subtopics, 606 dialogues, 4,891 turns → immutable utterances +
  content items/revisions. Legacy Swiss text is `dialect_id = null` and
  explicitly **"dialect not verified"** (never auto-labelled Zürichdeutsch).
- Content/discovery API (`/api/v1/...`) with published-only projections, utterance
  resolution per support language, daily selection, search, dialects, home;
  plus legacy `/content/*` adapters so old deep links keep working.
- Magic-link authentication: hashed challenges, generic `202`, rate limits,
  rotating opaque sessions with replay detection + family revocation, CSRF +
  Origin checks, `/me` profile, bookmarks, export, deletion job.
- Learning engine: enrollments (release-pinned), server-side grading (answer keys
  never leave the server), idempotent completion transaction, reward ledger,
  objective spaced-repetition reviews, activity-day streaks, mountain-journey
  node state machine with prerequisite/checkpoint unlocking.
- Lazy audio: canonical fingerprint + `audio_key`, durable job queue with fenced
  leases, GridFS storage, range/HEAD/ETag streaming, per-user + global budget
  limits. Ships a **deterministic fake TTS** provider (valid WAV, zero cost).
- Admin API: content lifecycle (`draft→…→published`), publish gates, generation
  jobs, user roles/suspend (recent-auth gated), creators/reports moderation,
  audit log, jobs/usage, database-health manifest check.
- AI gateway behind an app-owned interface (LiteLLM text adapter + fake adapter).
- 30 automated tests against a real ephemeral Mongo replica set (auth, content,
  learning idempotency/grading, audio concurrency/streaming, migration,
  fingerprint hash fixture). Run: `cd backend && pytest`.

**Frontend (`frontend/src/`, React/Vite/Tailwind — identity preserved)**

- Typed API client (`lib/api.ts`) talking only to `/api/v1` with cookie auth +
  CSRF; legacy JSON Vite plugin removed.
- Magic-link auth (`AuthContext`, `Auth` page + `/auth/callback`), no passwords
  or progress in localStorage (legacy keys cleared on load).
- Mountain-journey `Learn` page (map + accessible list view) and a lesson runner
  (study → assessment → result) with server grading.
- Per-turn AI audio playback (`TurnAudioButton`) on dialogues and lessons,
  labelled AI-generated.
- Legacy `/conversations/:id` resolves via the dialogue mapping and redirects.

A full headless-browser run verified: home → topics → dialogue → magic-link
sign-in → mountain journey → lesson study (with 8 audio buttons) → graded result.

## Deliberate deviations (and why)

1. **Introductory curriculum is derived from legacy, dialect-unverified content.**
   The curriculum release, its lessons and auto-generated comprehension exercises
   carry `dialect_verified = false` and provenance `legacy_unverified_preview`,
   and the UI shows a banner saying the Swiss German is *not yet dialect-reviewed*.
   This keeps the learning engine fully functional/testable without fabricating
   verified native mastery. Replace with AI-authored, human-reviewed, published
   Zürich/Bern lessons before promoting it as real instruction (see TODO).
2. **Speech uses a deterministic fake provider.** No real Swiss-dialect TTS has
   been evaluated/approved, so `speech.*` routes stay disabled and only the dev
   fake voice profile is enabled. Audio is honestly labelled AI-generated and is
   never required to complete a lesson.
3. **AI text uses a fake adapter by default.** Real generation is one env switch
   (`AI_TEXT_PROVIDER=litellm` + a key) behind the same interface.
4. **Local MongoDB binary.** For dev/testing a MongoDB 7.0 binary runs a
   single-node replica set from `.tools/` (gitignored). Production must use a
   managed/standalone replica set.
5. **Focused dependency set.** `backend/pip/requirements-app.txt` lists only the
   runtime packages the app needs (no torch/transformers), separate from the
   large legacy `pip/requirements.txt`.
6. **No fabricated creators.** The creators directory ships empty — real,
   verified profile/source links must be curated via the admin API.

## Out of scope / future (per spec)

Google/Microsoft OIDC sign-in, native mobile + PKCE exchange, offline sync,
video generation, public leaderboards, speech-recognition grading, and automated
social scraping. Interfaces/flags are reserved but intentionally disabled.

---

## MANUAL TODO (what you need to do)

### Infrastructure & secrets
- [ ] Provision a **production MongoDB replica set** (TLS) with separate runtime,
      worker and migration credentials; set `MONGODB_URI` / `MONGODB_DATABASE`.
- [ ] Set production `PUBLIC_WEB_BASE_URL`, `PUBLIC_API_BASE_URL`,
      `ALLOWED_ORIGINS`, `COOKIE_SECURE=true` and (if cross-subdomain) `COOKIE_DOMAIN`.
- [ ] Configure a **transactional email provider** and implement its adapter in
      `backend/app/auth/email_adapter.py` (replace the console adapter); set
      `EMAIL_PROVIDER` / `EMAIL_FROM`. Test the provider's real link handling.
- [ ] Store all provider keys/signing material in deployment secrets (never in DB
      or the frontend bundle).
- [ ] Set up **daily encrypted backups including GridFS** and rehearse a restore
      (target RPO 24h / RTO 4h).

### Content & launch quality
- [ ] Decide whether to keep the preview curriculum or replace it: use the **AI
      workshop** to author real Zürichdeutsch/Berndeutsch lessons, run QA, and
      **publish via a publisher** so content becomes `dialect_verified`.
- [ ] Build the **Berndeutsch (`gsw-be`) release** (the builder only seeds `gsw-zh`).
- [ ] Review the imported translations for semantic completeness.

### Speech (launch gate)
- [ ] Evaluate ≥2 real speech providers on 20 turns/dialect with a proficient
      reviewer (rubric ≥4 on each criterion); only then enable `speech.gsw_zh` /
      `speech.gsw_be` routes and approve human-reviewed voice profiles. Until then,
      ship text learning with "Audio coming soon".

### AI
- [ ] Set `AI_TEXT_PROVIDER=litellm` + a provider key to enable real generation,
      and review the versioned route config in `app_config` (`ai_routes`).

### Admin & ops
- [ ] Create the first admin: `python -m scripts.bootstrap_admin --email you@…`,
      then remove bootstrap capability.
- [ ] Curate **real creators** (verified source URLs) via the admin API — the
      directory is intentionally empty.
- [ ] Run the standalone worker in production (`python -m scripts.worker`) instead
      of the in-process dev worker (`RUN_INPROCESS_WORKER=0`).
- [ ] Decide final retention policies and apply `expires_at` TTLs accordingly
      (audit/jobs/receipts); surface them in privacy copy.
- [ ] (Optional) Build the `/admin` UI screens — the admin **API** is complete,
      but no admin SPA pages were built in this pass.

### Frontend polish (optional)
- [ ] Wire `/review`, `/profile` and `/creators` pages (APIs exist) and a dialect
      switcher; add the daily-dialogue/creator sections to the homepage.
- [ ] Full WCAG pass (reduced motion, focus states, 360px) — base structure is in
      place but not formally audited.

### Deployment
- [ ] Frontend: `cd frontend && npm ci && npm run build` → serve `dist/` (current
      production base path is `/demo/learn-swiss-german/`; configurable in
      `vite.config.ts`). Create `.env` with the production `VITE_API_BASE`.
- [ ] Backend: `pip install -r pip/requirements-app.txt`, run DB migrations with
      the migration credential, start the API + a worker process.
