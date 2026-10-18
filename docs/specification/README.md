# SwissSpeak: implementation specification

Version: 1.0 · 18 October 2026 · Status: proposed implementation baseline.

This package specifies the expansion of the existing `learn-swiss-german` project. It is a coding-agent handoff, not an assertion that the described features already exist. Build within this repository; preserve its Python backend and existing visual identity.

## Read in this order

1. [Product, learning method, and interface](01-product-and-learning.md)
2. [Architecture, authentication, AI, and audio](02-architecture-and-services.md)
3. [MongoDB collections and index setup](03-mongodb-setup-and-indexes.md)
4. [API, delivery plan, and acceptance criteria](04-api-and-delivery.md)
5. [Research and source notes](05-research-and-decisions.md)

`MUST` means a release requirement; `SHOULD` means the default unless a documented implementation constraint justifies a change. Numbers below are proposed product defaults and must be editable through versioned configuration where specified.

## Coding-agent handoff

Use this instruction with the repository and the complete specification folder:

> Implement the SwissSpeak expansion specified in `docs/specification/README.md` and its linked documents. Inspect applicable repository instructions first. Preserve the existing FastAPI backend, React frontend, routes and visual identity. Execute the delivery phases in order, keeping the app runnable; implement the MongoDB setup/import tools and real authentication before replacing progress. Use the specification's acceptance matrix to verify behavior. Keep all runtime product data and media in MongoDB/GridFS. Do not fabricate credentials, creators, dialect validation, published coverage or voice quality. Record justified deviations and provide working changes, migration reports, test results and deployment instructions. Google/Microsoft sign-in, native apps and video generation remain future scope unless separately authorized.

## Decisions to carry into implementation

- Free web application now; one FastAPI API for web and future mobile clients.
- Dialogue-led learning for people who already understand basic Standard German.
- Zürichdeutsch and Berndeutsch at launch; Walliserdeutsch and St. Gallerdeutsch later. These are launch priorities, not a claim of a proven popularity ranking.
- English and Spanish support translations at launch; Standard German remains the learning bridge. Additional languages use the same data model.
- Magic email links at launch. Google and Microsoft are designed into identity storage and API boundaries, but remain disabled until implemented and tested.
- MongoDB holds all runtime product data, publishing state, user data, durable jobs, settings, and media. GridFS stores generated audio and first-party media bytes. No Redis, SQL database, or local content files are required in production.
- React/Vite/TypeScript/Tailwind and existing shared components remain. Retain the SwissSpeak name and current palette, alpine hero, cards, and conversational presentation.
- AI creates lesson drafts, translations, exercises, and audio. Publishing has explicit quality gates and an administrator action. Creator profiles describe real people and require verified source links; AI must never invent creators or testimonials.
- Generated audio is created on first playback request, then retained and reused without TTL. Corrected text, different dialects, voice changes, or synthesis changes produce distinct versions.
- Content and progress are versioned. Server-side grading determines unlocks and rewards.

## Existing project audit

Inspected local source and the deployed homepage on 18 October 2026.

| Area | Observed state | Required direction |
|---|---|---|
| Backend | FastAPI in `backend/main.py`; `/content/*` uses Python constants | Keep FastAPI; query MongoDB through services/repositories |
| Frontend | React 19, Vite, Tailwind 4, Radix UI, TanStack Query | Extend these components; avoid an unrelated rewrite |
| Content | Local JSON inventory: 9 topics, 120 subtopics, 606 dialogues, 4,891 dialogue lines | Idempotent MongoDB import and editorial/dialect validation |
| Translations | All 4,891 imported lines contain Spanish; English and German fields also exist | Preserve fields and validate semantic completeness |
| Deployed homepage | Six visible topic groups, alpine photo, red buttons, daily phrase/dialogue | Preserve visual language; reconcile local/deployed inventory during migration |
| Authentication | `AuthContext.tsx` stores users and plaintext passwords in localStorage | Remove prototype login and stored passwords; real email authentication |
| Progress | `ProgressContext.tsx` uses localStorage, fixed totals, client-derived unlocks | Server-owned attempts, mastery, and curriculum-derived totals |
| Content transport | `frontend/src/lib/api.ts` loads most content from static JSON; daily items from API | One versioned backend contract |
| Existing AI helper | `backend/vtlib/generative_llm.py` uses LiteLLM for text | Reuse useful logic behind capability-specific adapters |
| Existing Mongo helpers | `backend/vtstorage/*` exists; `api_shared.py` leaves storage disabled | Enable tested Mongo repositories; do not assume helpers satisfy transaction/async needs |
| Creator discovery | `Resources.tsx` and `CreatorCard.tsx` exist with placeholder records, but Resources is not mounted in `App.tsx` | Reuse layout with real Mongo-backed records and Instagram support |
| Routing | `/subtopics/:subtopicId` works; `/conversations/:conversationId` mounts a component expecting `subtopicId` | Preserve old links and explicitly repair parameter/redirect behavior |
| Tests | README reports no automated suite | Add meaningful authentication, progression, publication, audio concurrency, and migration tests |

Counts describe the checked-in JSON, not a linguistic quality assessment. Duplicate dialogue IDs were not found in this inventory. Existing content lacks a reliable dialect label and MUST NOT automatically be relabeled Zürichdeutsch.

## Scope boundary

Deliver the database, backend services, learning web experience, admin panel, and migration described here. Native apps, paid plans, public leaderboards, live AI conversation, speech recognition grading, video generation, and automatic social feed scraping are future work. Provide extension points without implementing unused systems.

The attached image is visual inspiration for a winding learning route with milestones. It is not an instruction document and is not licensed production artwork. Use original Swiss-themed artwork; do not copy another app's illustrations, characters, or game economy.

![Learning path reference](assets/mountain-path-reference.png)
