# API contract, implementation plan, and acceptance criteria

## 1. Contract rules

Base API: `/api/v1`. Serve a committed OpenAPI contract and generate/check TypeScript client types from it. Use additive changes within v1; breaking semantics require a new version or an explicit versioned content schema. UI routing basename and API base URL are independent.

IDs are opaque strings, times ISO-8601 UTC, enums explicit. Single resources use `{data: {...}}`; lists use `{data: [...], page: {next_cursor, has_more}}`. Default page size 20, maximum 100. Use opaque cursor pagination with a stable sort/tiebreaker; filter fields and sort modes are allowlisted. Do not pass raw MongoDB query operators from a client. Public payloads explicitly expose translation availability and dialect, never invent fallback content.

Error shape:

```json
{"error":{"code":"AUDIO_BUDGET_EXHAUSTED","message":"New audio is temporarily unavailable.","request_id":"request-uuid","retry_after_seconds":3600}}
```

Use 400 invalid request, 401 unauthenticated, 403 insufficient capability, 404 missing/inaccessible resource, 409 state/idempotency/version conflict, 410 retired resource when safe to reveal, 422 field validation, 429 rate limited, 503 temporary provider/unavailable generation. Include `Retry-After` where appropriate. Internal/provider errors and stack traces never leak to users.

Require `Idempotency-Key` for attempt submission, audio generation requests, enrollment changes, admin generation/publish and account job requests. Persist user+scope+key+request hash in MongoDB. Same key/body returns the original result; same key/different body returns 409. Unique business constraints protect effects beyond the receipt's 7-day retention.

Use ETags/`If-Match` for draft/profile/attempt-answer saves; return 409 with current version when edits race. Published immutable responses use revision-based ETags. Private profile/progress/auth/admin responses are not publicly cached.

## 2. Endpoint inventory

`Public` means published projections only. `Learner` means authenticated owner only; roles and ownership are checked on every resource fetch/write. Admin endpoints require the specified server capability.

### Authentication and profile

| Method and route | Access | Behavior |
|---|---|---|
| `POST /auth/magic-links` | Public, throttled | Request login email; generic 202 |
| `POST /auth/magic-links/consume` | Token possession + explicit UI action | Validate/consume once; set web cookies or initiate registered-client code flow |
| `POST /auth/refresh` | Refresh credential, CSRF for web | Rotate credentials; revoke family on replay |
| `POST /auth/logout` | Learner/refresh credential | Revoke current family and clear cookies |
| `POST /auth/logout-all` | Learner + recent auth | Revoke all families |
| `GET /auth/methods` | Public | Available methods only; hide disabled OIDC/native routes |
| `GET /me`, `PATCH /me` | Learner | Read/update allowlisted preferences; optimistic version |
| `GET /me/sessions`, `DELETE /me/sessions/{id}` | Learner | List safe device/session data and revoke owned family |
| `POST /me/email-change` | Learner + recent auth | Send purpose-bound verification; old email remains until completion |
| `POST /me/exports` | Learner + recent auth | Export job with expiring authenticated download |
| `POST /me/deletion` | Learner + recent auth and purpose-bound confirmation | Queue deletion and revoke sessions |

Future-only contract boundaries: `/auth/oidc/{provider}/start`, `/callback`, `/me/identities`, `/me/identities/{id}`, and `/auth/native/exchange`. Do not display nonfunctional Google/Microsoft buttons. All linking requires authenticated confirmation; the callback alone never merges accounts.

### Content, discovery, and media

| Method and route | Access | Behavior |
|---|---|---|
| `GET /home?dialect_id=&support_language=` | Public | DB-managed sections, current daily refs, creator features; no personal data |
| `GET /dialects` | Public | Enabled and optional coming-soon dialect metadata |
| `GET /topics`, `GET /topics/{id_or_slug}` | Public | Published counts, metadata, bounded children |
| `GET /subtopics/{id_or_slug}` | Public | Dialogue summaries, availability and topic metadata |
| `GET /dialogues/{id}?dialect_id=&support_language=` | Public | Exact published revision and language-aligned turns |
| `GET /dialogues/{id}/revisions/{n}` | Public/owned history/editor rules | Published revision only if still permitted; drafts require explicit preview capability |
| `GET /patterns`, `GET /vocabulary` | Public | Dialect/topic filter, bounded results |
| `GET /search?q=&dialect_id=&kind=` | Public | Published metadata search only, limits and normalization |
| `GET /daily?dialect_id=` | Public | Editorial date and selected published phrase/dialogue |
| `GET /creators`, `GET /creators/{slug}` | Public | Real published profiles and attributed resources |
| `GET /creator-resources` | Public | Filtered published posts; canonical links, embed descriptors |
| `POST /reports` | Learner; public removal contact may use separate challenge | Bounded feedback/suggestion, no automatic publication |
| `POST /audio/requests` | Ready assets public; misses learner/editor | Resolve approved text and voice; 200 ready, 202 pending, clear generation limits |
| `GET /audio/requests/{id}` | Request owner or same accessible published media | Safe status/result, no prompt/provider credentials |
| `GET/HEAD /media/{id}/stream` | Public media or explicit draft/export authorization | Range streaming, checksum/ETag, appropriate cache policy |

Do not let public job status IDs expose an admin generation prompt or another learner's export. Worker job IDs and public audio request/status handles may be distinct. Hiding a creator/resource immediately excludes it from home/list/detail responses.

Audio request example:

```json
{
  "content_ref":{"item_id":"dialogue-uuid","revision":3},
  "turn_id":"turn-uuid",
  "language_tag":"gsw-CH"
}
```

Server chooses the turn's pinned approved voice; optional allowed voice choices must resolve through server configuration. Never accept a raw model/text override. Pending response:

```json
{"data":{"request_id":"request-uuid","status":"queued","status_url":"/api/v1/audio/requests/request-uuid","poll_after_seconds":2}}
```

Ready response includes `media_id`, `audio_key`, `utterance_id`, `stream_url`, `duration_ms`, `ai_generated: true`, and whether this individual asset has a human dialect review. A media hash does not authorize access to private drafts.

### Learning

| Method and route | Access | Behavior |
|---|---|---|
| `GET /curricula?dialect_id=` | Public | Published releases and available/coming-soon stage metadata |
| `POST /me/enrollments` | Learner | Choose dialect/curriculum and pin current published release |
| `GET /me/enrollments` | Learner | Per-dialect enrollment summaries |
| `GET /me/enrollments/{id}/path` | Owner | Node state/outcome, required totals, lock reasons and current node |
| `POST /me/enrollments/{id}/migration-preview` | Owner | Show old/new equivalences, retained credits, new requirements |
| `POST /me/enrollments/{id}/migrate` | Owner | Apply approved mapping transactionally; preserve historical attempts |
| `GET /lessons/{id}?revision=` | Public/owner/editor policy | Study payload only; no answer keys or hidden grading variants |
| `POST /attempts` | Learner | Server creates assessment/review/placement attempt and pins content/selection |
| `PATCH /attempts/{id}` | Owner | Save allowed answers/acknowledgements with version check |
| `POST /attempts/{id}/submit` | Owner | Idempotent server grading, progress/rewards transaction |
| `GET /attempts/{id}` | Owner | Resume or view immutable result; post-submit feedback only |
| `GET /me/reviews?dialect_id=` | Learner | Due objectives and eligible contextual tasks |
| `GET /me/progress?dialect_id=` | Learner | Accuracy, mastery, streak, XP and summit summary |
| `GET/POST /me/bookmarks`, `DELETE /me/bookmarks/{id}` | Owner | Idempotent bookmarked content |

Path attempt creation requires the node available; a library practice attempt may target the same dialogue without unlocking/rewarding a locked path. Keep `mode=path|practice|review|placement` explicit. Review and placement use versioned server-selected exercise pools, not arbitrary client item IDs.

Submission request and response:

```json
{"attempt_version":2,"answers":[{"exercise_id":"exercise-uuid","choice_id":"choice-b"}],"acknowledged_steps":["scene","study","rehearse"]}
```

```json
{"data":{"attempt_id":"attempt-uuid","score":{"correct":4,"total":5},"passed":true,"completed_node_id":"node-uuid","awarded_xp":20,"next_node_id":"next-node-uuid","feedback":[],"progress_version":7}}
```

The short example omits four other submitted answers; a real 5-item attempt requires all required answers or scores missing ones as incorrect according to its pinned grading policy. Explicitly return that policy to clients. A self-reported rehearsal acknowledgement is never represented as verified speaking proficiency.

### Administration

| Route group | Capability and behavior |
|---|---|
| `/admin/content`, `/admin/content/{id}/revisions` | Editor: list/create/edit drafts with typed payloads, diff/preview and batch metadata |
| `/admin/content/{id}/qa` | Editor: schema/reference/dialect/translation checks and AI QA job |
| `/admin/content/{id}/submit-review`, `/approve` | Editor/publisher respectively; record findings and actor |
| `/admin/content/{id}/publish`, `/withdraw` | Publisher: atomic pointers, authorization/QA gates, audit |
| `/admin/generations`, `/admin/generations/{id}/cancel` | Editor: bounded job, route/prompt version, estimate, status/result refs |
| `/admin/curricula`, `/admin/curricula/{id}/validate`, `/publish` | Editor/publisher: graph and release validation plus publication |
| `/admin/media`, `/admin/media/{id}/quarantine`, `/regenerate` | Editor; publisher for changing public serving binding; immutable versioning |
| `/admin/creators`, `/admin/creator-resources`, `/admin/reports` | Editor drafts/moderation; publisher publishing/removal visibility |
| `/admin/config/{key}/revisions`, `/publish` | Administrator for routes/budget/auth/roles, publisher for homepage/editorial copy |
| `/admin/users`, `/admin/users/{id}/roles`, `/suspend` | Administrator, recent authentication for privilege changes |
| `/admin/jobs`, `/admin/usage`, `/admin/audit`, `/admin/database-health` | Permission-scoped read access; no raw secret/token/query console |

Route/action schemas and precise capability rules must be committed to OpenAPI before UI implementation. Do not implement a generic unrestricted collection CRUD endpoint as an admin shortcut.

## 3. Legacy migration

Implement a deterministic migration command with `--dry-run`, `--apply`, source checksum, migration version, resumable batches, validation report and repeat-run safety.

1. Inventory JSON and Python constant sources, topic/subtopic references, dialogue IDs, empty translations, malformed objects and line counts. Baseline JSON inventory: 9 topics, 120 subtopics, 606 dialogues, 4,891 turns. Verify again at execution time, rather than assuming these counts can never change.
2. Choose JSON as initial canonical migration input because it powers most current frontend reads. Compare the Python constants and deployed daily sources; report conflicts rather than blindly importing both as duplicate content.
3. Preserve topic/subtopic slugs, dialogue legacy IDs, and all speaker/scene/translation/difference/key-phrase fields. Generate stable UUID mappings. A turn with no source ID gets a deterministic source-scoped ID from subtopic/dialogue/position plus migration namespace; future editorial insertion does not renumber existing saved turn IDs.
4. Create immutable utterances per language; legacy Swiss text gets `dialect_id=null` and unverified status, not an inferred Zurich label. Deduplicate identical canonical text within the language/dialect/context key. Preserve actual turn order and reuse source key phrases only where the text actually matches.
5. Import legacy topic/subtopic/dialogue/pattern/vocabulary revisions with provenance. Separate compatibility publication from path eligibility: a previously visible unverified dialogue can remain explicitly labeled in the free library; it cannot be used in dialect-specific instruction until validated and revised.
6. Admin AI adaptation creates Zürich/Bern variants linked to shared scenarios, with editable pronunciation/style guides, QA and publishing. Never overwrite legacy content to create dialect coverage.
7. Build lessons/objectives/exercises around validated dialogues; create and validate curriculum release(s). Empty later stages remain honest coming-soon placeholders.
8. Reconcile source→DB counts and field-level checksums, reference integrity, no missing turns/translations, uniqueness and deterministic second-run behavior. Export a machine-readable and readable exception report; unexpected conflicts fail release.
9. Replace frontend JSON fetches with typed API client calls and remove the Vite content-serving plugin from the production path. Retain source files as archival migration inputs. Add temporary `/content/*` adapters backed by MongoDB if old clients need them.
10. Preserve old `/topics/*` and `/subtopics/*` links. Fix `/conversations/:conversationId` by looking up its legacy mapping and redirecting to the canonical dialogue/subtopic route. Test deep links directly under both root and current demo basename.

LocalStorage accounts are untrusted prototypes. Require a new verified magic-link account. Optionally offer one-time import of bookmarks and practice history after sign-in, marking it `legacy_unverified`; do not import passwords, admin roles, scores as verified passes, or mountain rewards. Remove known prototype password keys locally and clear user-scoped caches during the transition. Do not inspect/upload unrelated localStorage entries.

## 4. Delivery sequence and concrete outputs

Each phase must leave a runnable application. Do not rewrite the frontend before preserving current content access.

### Phase 1 — baseline and database

- Capture current homepage/dialogue visual references and existing route behavior.
- Introduce configuration, Mongo repositories, lifespan connection handling, replica-set dev setup and health endpoints.
- Implement collections, full validators, named index manifest and idempotent setup/check CLI; render this database guide as a linked admin help page.
- Implement dry-run/import/reconciliation and route compatibility.
- Switch published content reads to MongoDB while keeping the current UI intact.

Exit: existing library works with JSON directory unavailable; migration is repeatable and counts reconcile.

### Phase 2 — identity and user data

- Magic links, email adapter, hashed/rotating sessions, CSRF, rate limits, identity model and RBAC.
- Real profile/preferences, bookmarks and server-owned history; remove fake password/auth storage.
- Admin bootstrap, authenticated shell, audit foundation and account export/deletion job boundaries.

Exit: two browsers/devices share one learner's saved profile; another learner cannot read it; expiry/replay/logout behavior is tested.

### Phase 3 — content operations and AI workshop

- Typed versioned content editor, revision diff, dialect/spelling guides and translation availability.
- Durable Mongo queue, fenced leases, budget reservations, LiteLLM text adapter and structured generation/QA.
- Publishing gates, curriculum editor/validator, homepage and real creator curation.

Exit: an editor generates a dialogue/lesson draft, reviews it, and a publisher releases it without exposing draft/private fields.

### Phase 4 — dialogue lessons and mountain journey

- Implement the learning cycle, server grading, objective reviews, enrollment/version pinning, node state and accessible path/list modes.
- Add idempotent completion/reward transactions and local-day activity calculations.
- Produce a coherent introductory release in both dialects, with later content either published or explicitly coming soon.

Exit: learner completes a real lesson, unlocks the correct next node, resumes across devices and cannot award duplicate XP.

### Phase 5 — AI audio

- Evaluate target-dialect speech routes and approve voice profiles.
- Immutable hash fixtures, lazy generation, GridFS storage, retry/concurrency/lease handling and range streaming.
- Per-turn/full-dialogue playback, honest AI labeling, reports, moderation and quota/budget UI.

Exit: first miss generates one visible reusable asset; later users receive the same ready asset; wrong dialect/edited text cannot reuse its key. Unsupported speech quality does not block text learning.

### Phase 6 — launch polish and readiness

- Homepage with sample dialogue, journey preview, daily selection and creator spotlight; creators directory with real links and optional consent-based embeds.
- Accessibility, responsive/basename/deep-link checks; security and concurrency integration tests; dependency review.
- Backups/restore rehearsal, production secrets, email delivery configuration, cost/queue monitoring, deployment/rollback runbook.

Exit: all release acceptance criteria below pass. Google/Microsoft, mobile-native/offline and video remain future phases with documented interfaces.

## 5. Acceptance test matrix

These are required behavioral tests, not instructions to test implementation trivia. Automated integration tests should run against a real ephemeral MongoDB replica set. Provider/email fakes exercise failure paths without paid generation; optional provider smoke checks are separate.

| ID | Scenario and expected result |
|---|---|
| AUTH-01 | Existing and unknown emails receive indistinguishable request responses; throttle works without revealing existence |
| AUTH-02 | Link GET/prefetch does not consume token; explicit POST does; two concurrent consumers produce one session transaction |
| AUTH-03 | Used/expired token fails immediately even before TTL deletion; token never appears in normal logs/analytics |
| AUTH-04 | Refresh rotates; old refresh replay revokes family; logout and suspension block further authorized calls |
| AUTH-05 | CSRF/origin failure rejects cookie-auth writes; learner cannot self-assign roles or inspect another user's data |
| AUTH-06 | Cross-browser link use signs in the receiving browser only; malicious return URL cannot redirect externally |
| CONTENT-01 | Draft revision and answer keys are absent from public APIs, search, preview links and client caches |
| CONTENT-02 | Publishing a new dialogue leaves prior pinned attempts stable; invalid references/cyclic curricula fail publication |
| CONTENT-03 | Missing Bern variant shows explicit absence, never unmarked Zurich fallback; switch preserves both enrollments |
| LEARN-01 | Score 4/5 passes 80%; 3/5 fails; client-supplied score/reward values are rejected or ignored safely |
| LEARN-02 | Same submission retried ten times gives one result/reward; changed body with same key yields 409 |
| LEARN-03 | Two devices pass the same node concurrently: both attempts persist, exactly one first-completion reward |
| LEARN-04 | Locked path nodes cannot be completed by a practice-mode attempt; prerequisite and checkpoint rules hold |
| LEARN-05 | Same-day repeated retrieval cannot advance mastery repeatedly; due dates/review caps match pinned rules |
| LEARN-06 | Duplicate sessions on a local day count once; missed days, DST changes and timezone changes produce correct streaks |
| LEARN-07 | New curriculum release does not silently change old enrollment totals; explicit equivalence migration preserves earned credits |
| AUDIO-01 | Two different users concurrently request the same approved turn: one visible media key/job, consistent pending/ready responses |
| AUDIO-02 | Same canonical text/settings reuses audio; changed dialect/voice/model/pronunciation/text produces a distinct key |
| AUDIO-03 | Editing English translation alone preserves Swiss audio key; browser playback-speed adjustment makes no generation call |
| AUDIO-04 | Worker crashes after GridFS upload: orphan cleanup works; expired worker cannot publish over new lease owner |
| AUDIO-05 | Provider timeout/429 and budget exhaustion show recoverable states; ready audio and text learning still work |
| AUDIO-06 | Private/quarantined media cannot stream publicly; valid public audio supports HEAD/Range/ETag |
| AUDIO-07 | Malformed/empty provider bytes never become ready; no TTL removes reusable lesson audio |
| ADMIN-01 | Editor can generate/edit but cannot publish without capability; admin role changes require fresh auth and emit audit |
| ADMIN-02 | Concurrent draft edits get an explicit version conflict; publishing records exact prompt/model/revision provenance |
| CREATOR-01 | Only real verified URLs publish; Instagram/TikTok/Facebook cards all work without an embed or provider token |
| CREATOR-02 | Removed/private/blocked post and denied embed consent produce a usable attributed link; hidden creator vanishes from featured sections |
| DATA-01 | Import twice produces unchanged counts/IDs; source conflicts fail with a readable report, never silent loss |
| DATA-02 | Setup/check verifies validators and full index options; ready app runs without data-json/Python constants |
| DATA-03 | Restore reproduces published lessons, accounts/progress and actual playable audio bytes |
| UX-01 | 360px and desktop views preserve identity, fit all controls, allow keyboard learning and offer list view/reduced motion |
| UX-02 | Direct navigation/reload works under current demo basename and root config; legacy dialogue links resolve correctly |
| ACCOUNT-01 | Export contains only the requesting learner's data; deletion revokes sessions and removes user-owned data while retaining shared lesson audio |

## 6. Definition of done for the coding agent

Provide working backend/frontend, migration/setup scripts, validated schema/index manifest, generated OpenAPI/client types, content seed/migration report, original/authorized map assets, completed automated checks, and deployment/rollback documentation. Document exact software versions and provider route evaluations actually used. Never present placeholder content, disabled buttons, mocked authentication or hard-coded progress as finished.

Do not add native apps, payments, a Redis/SQL dependency, video generation or a large framework migration to this scope. Choose routine implementation details autonomously within these requirements. Record any necessary deviation and its user-visible consequence in a decision log before handing off.
