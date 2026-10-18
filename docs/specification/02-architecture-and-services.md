# Architecture, authentication, AI, and audio

## 1. Deployment and boundaries

Keep a modular Python/FastAPI application, not a collection of microservices. Run three process types from the same backend package: HTTP API, durable job worker, and lightweight scheduled maintenance worker. React talks only to the versioned API. Workers use the same repositories and model adapters.

```text
React web / future mobile
          |
      FastAPI /api/v1
          |
  authentication · content/publishing · learning · media · administration
          |                                |
    MongoDB replica set              AI and email adapters
  records + jobs + GridFS            external providers
          |
     Python job workers
```

Use MongoDB as the only application persistence engine. Deploy a replica set (including a single-node replica set for local development) because completion, publishing, and authentication require multi-document transactions. Keep API stateless except connection pools. Store audio bytes in GridFS, not the API container filesystem; this meets both “saved on the server” and “everything in the database.” First-party uploaded imagery and downloadable assets also use GridFS. Existing source-code assets may be imported once and referenced from MongoDB; CSS/icons and application code remain ordinary build assets.

Use a tested, pinned PyMongo release with its supported Async API for async repositories and GridFS, or explicitly isolate supported synchronous GridFS operations in bounded worker threads. Do not call blocking Mongo/provider operations directly inside async HTTP handlers. The existing `VTPermStorage` can supply migration ideas but must not force unsupported concurrency or hide transaction sessions. No new Motor dependency. [MongoDB's migration guidance](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) describes the supported PyMongo Async direction.

Suggested backend modules:

```text
backend/
  main.py                    # lifespan, routers, middleware
  app/
    config.py                # environment + DB settings, secret references
    db/                      # client, repositories, validators, migrations
    auth/                    # magic links, sessions, identities, RBAC
    content/                 # immutable revisions and publishing
    learning/                # enrollment, attempts, grading, reviews, rewards
    media/                   # cache keys, GridFS, delivery, moderation
    ai/                      # text/speech adapters, routes, schemas, evaluation
    admin/                   # admin API, QA and audit
    jobs/                    # lease queue, handlers, scheduler
    common/                  # IDs, errors, tracing, time helpers
  scripts/                   # import, DB setup/indexes, smoke checks
  tests/
```

Preserve existing entry points during transition; extract services incrementally. Dependency locks must be reviewed against currently supported patched packages. The existing `litellm<=1.82.5` constraint is an observed repository constraint, not an instruction to keep that version forever.

## 2. Identity, magic links, and sessions

Implement authentication in Python using maintained cryptographic/OIDC libraries; email sending behind a transactional email adapter. MongoDB contains internal users, provider identities, magic-link challenge hashes, and sessions. Provider API keys and signing/encryption keys live in deployment secrets, not plaintext DB settings or frontend bundles.

### Magic-link flow

1. `POST /auth/magic-links` accepts email, allowlisted relative return path, and registered client type. Normalize email consistently; do not apply Gmail dot/plus rewrites. Return generic `202` regardless of whether the email already exists. Rate-limit email/IP/client combinations without exposing account existence.
2. Generate at least 32 random bytes, URL-safe encoded. Store only a SHA-256 token hash in the challenge document with purpose, normalized email, expiry (15 minutes), pending state, client intent, and permitted return path. Use separate challenge purposes for login, linking, email change, and account deletion.
3. Send an HTTPS link to an allowlisted frontend callback. Prefer the token in a URL fragment, immediately remove it from history, and exchange via POST. This avoids routine server/access-log and referrer leakage. Callback has no social scripts or analytics; use `Referrer-Policy: no-referrer`, `Cache-Control: no-store`, and a restrictive CSP. Test the email provider's actual link handling.
4. Opening the page does not consume the challenge. Show a “Continue as [masked email]” action; consume only after explicit POST so email scanners/prefetch cannot sign a user in. The receiving browser may differ from the requesting browser. Do not authenticate the original browser by polling a request ID.
5. On confirmation, atomically consume the still-pending, unexpired challenge, upsert/find the internal user and verified email identity, and create a session in one transaction. Expired/used tokens fail even if MongoDB TTL cleanup has not happened. New users receive no elevated roles.
6. Failures return a safe retry/new-link action. Resend has a 60-second UI cooldown and backend limits; do not invalidate an already issued usable link merely because an unauthenticated actor requests another one. Never log/email tokens outside the intended email delivery.

Default throttles to validate under load: 5 requests/email/hour, 20/IP/hour, burst 3/IP/minute. Persist counters in bounded time buckets in MongoDB, with TTL and server-side enforcement. Email provider responses and delivery identifiers may be retained briefly without raw token-bearing message bodies. Avoid putting unencrypted magic links in a job payload; login email delivery occurs through the adapter during the request with a short timeout and safe retry by requesting a new link.

### Web sessions

Use random opaque access/session credentials resolved to MongoDB hashes. For web, send a Secure, HttpOnly, SameSite=Lax cookie (path `/` so future root/subpath deployments work). Use a short access lifetime of 15 minutes and a rotating refresh credential with 30-day absolute family lifetime. A refresh family has a unique session ID; store only hashes of bearer values, plus bounded used-refresh hashes until family expiry. Reject replay of a used refresh value and revoke that family. Serialize refresh calls in the frontend to avoid innocent parallel refresh races; document the expected retry behavior.

Cookie-based state-changing requests require an anti-CSRF token bound to the session plus validated Origin/Referer. Use HTTPS and exact origin allowlists. Logout revokes server records and clears cookies; “log out all devices” revokes every family. Suspended/deleting users fail authorization immediately. Admin permissions come from current server data, not client state or stale claims. Require fresh authentication within 10 minutes for role changes, linking/unlinking identities, changing verified email, and deletion.

Never persist access/refresh credentials or passwords in localStorage. Remove the prototype password form and clean legacy `users`, `currentUser`, `progress_*`, `quizResults_*` keys only after explaining local progress import/reset. Legacy plaintext passwords must be discarded and must never be uploaded.

### Future mobile and social login

Mobile uses the same identity, learning and media services. When native apps are built, add registered iOS/Android client IDs, associated HTTPS universal/app links, OS secure credential storage, and a public-client authorization-code exchange bound to PKCE. Browser-based authentication returns a short-lived, single-use code to the registered app, never long-lived tokens in a deep link. Store only hashes of native exchange codes with a 60-second expiry. Do not implement embedded password forms or a WebView-only login dependency.

Reserve OIDC provider adapters now, feature-flagged off. Later Google/Microsoft sign-in uses authorization code + PKCE, `state`, `nonce`, exact redirect URIs, issuer/audience/signature/expiry validation, maintained discovery/JWKS handling, and minimal `openid profile email` scopes. Use `(provider, issuer, subject)` as identity uniqueness; email is contact data, not provider identity. [Google documents stable `sub` identity](https://developers.google.com/identity/openid-connect/reference); [Microsoft documents its OIDC flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc).

Never merge accounts solely because two provider emails match. Ask an already authenticated user to link, with fresh proof of both identities. If a returning social identity has no usable email, collect and verify one without changing its provider subject. Support personal and organizational Microsoft accounts only after explicit application registration/testing. Unlinking cannot remove the user's final usable sign-in method.

## 3. Content identity and publishing

Distinguish these concepts:

- **Scenario:** language-independent situation/intent, such as ordering bread.
- **Content item:** stable public identity (dialogue, lesson, pattern, etc.).
- **Revision:** immutable exact version with language/dialect, payload, references, provenance, and QA status.
- **Utterance:** immutable exact speakable text in one language/dialect; reused across dialogue turns, key phrases, vocabulary examples, and audio.
- **Curriculum release:** immutable graph that pins exact lesson/checkpoint revisions and reward/grading configuration versions.

A dialogue revision stores ordered turns, speaker IDs, exact utterance references for the dialect/German/translations, scene, register, notes, key chunks, and objective IDs. Bound arrays to 50 turns per dialogue; reject oversized payloads and split long content. A lesson revision pins dialogue revision(s), activity definitions, objective IDs, required acknowledgements, and assessment configuration. Keep server-only grading keys in private revision fields projected out of learner responses.

No published content is edited in place. A publisher action atomically sets the item's published revision pointer, writes publication state and audit. Curriculum publication validates the full graph, all references, dialect coverage, and approved dependencies before making a release available. A change to a shared utterance creates a new utterance and downstream content revision, not an update to text behind old audio.

Immutability applies to approved payloads, grading keys, references and provenance. Workflow status and publication/withdrawal metadata may change through audited transitions without modifying that payload. Keep administrative revision lifecycle metadata separate from the immutable payload checksum.

Version references are `{item_id, revision}` pairs. Dialogues may share `scenario_id`; dialect variants remain distinct content items. Draft revisions can evolve under optimistic concurrency; once approved/published they are immutable. Deprecation/withdrawal controls current visibility and generation authorization; historical records remain accessible only as appropriate to the learner's own attempt history.

## 4. AI capability gateway

Reuse LiteLLM through a small application-owned interface, initially its Python SDK. Do not require LiteLLM Proxy's separate persistence stack. [LiteLLM exposes text and speech capabilities](https://docs.litellm.ai/docs/supported_endpoints), but a provider's “German” support is not proof of Zürich/Bern pronunciation quality.

Interfaces:

```python
generate_structured(route_alias, messages, schema, limits) -> GenerationResult
synthesize_speech(resolved_voice_profile, text, pronunciation) -> SpeechResult
# Reserved extension; no launch implementation:
generate_video(route_alias, brief, assets) -> MediaJobResult
```

Route aliases such as `lesson.author`, `lesson.qa`, `translation.en`, `translation.es`, `speech.gsw_zh`, `speech.gsw_be` reference versioned MongoDB configuration. Config includes capability, allowed provider/model, deployment/model revision where available, secret reference, timeout, retries, maximum tokens/characters, cost estimate, approved fallback candidates, and evaluation status. Keep provider-specific options behind adapters. Use a dedicated speech provider adapter if LiteLLM cannot express required voice/dialect features.

Resolve the concrete provider/model/voice/settings before computing an audio key. Fallback to a different resolved synthesis configuration creates a different key. Do not change dialect, voice, or text invisibly during fallback. Global model upgrades affect future generation; cached audio and historical provenance remain stable. Where a vendor offers only a floating model name, pin an internal synthesis version and record generation timestamp; byte-for-byte reproducibility is not guaranteed.

Generation pipeline: structured brief → versioned prompt/schema → reserved budget → durable job → provider output → Pydantic validation → bounded repair (maximum 2 attempts) → duplicate/translation/dialect/answer-key QA → draft revisions → review. Batch generation is bounded (initial maximum 20 lessons/job), resumable per child item, cancelable between calls, and never auto-publishes. Preserve prompt/template version, route snapshot, model, parameters, output references, costs and review findings. Sanitize generated HTML/Markdown; generated output is data and cannot execute tools or alter roles/settings.

AI QA checks schema completeness, aligned turns, consistent speaker/formality, suitable German prerequisite, translation faithfulness, dialect consistency, objective coverage, answer ambiguity, source licensing, and unsafe/inaccurate cultural claims. It must flag emergency/health/legal scenarios for careful wording and avoid converting sample dialogue into authoritative real-world advice.

### Audio provider selection is a launch gate

Do not invent a provider guarantee. Evaluate at least two eligible speech routes using 20 representative turns/dialect (40 total), including questions, vowel contrasts, numbers, Swiss place names and polite forms. Keep audio and ratings in MongoDB. A proficient target-dialect reviewer rates dialect fidelity, intelligibility, naturalness, and text adherence on 1–5. Release a voice profile only with each criterion averaging at least 4 and no critical meaning/dialect errors in the sample; record reviewer and rubric version. If unavailable, ship text learning with explicit “Audio coming soon” for that dialect rather than relabeling Standard German speech.

Runtime first-demand audio may use a validated voice profile after automated technical checks; label it “AI-generated” and allow reports. It is not individually native-reviewed unless a review record exists. Administrator previews are explicit playback requests and use the same cache pipeline. No automatic full-corpus pre-generation.

## 5. Exact phrase/audio association

Use stable IDs for product identity and hashes for deduplication, not interchangeable random phrase codes.

### Utterance identity

An utterance stores `id`, `language_tag`, `dialect_id` (null for Standard German/translations), `text`, `canonical_text`, `text_sha256`, and editorial context where pronunciation needs disambiguation. Canonicalization version 1: Unicode NFC, CRLF→LF, trim leading/trailing whitespace, collapse repeated horizontal whitespace. Preserve case, punctuation, apostrophe distinctions, umlauts, and all spoken lexical content. Hash canonical UTF-8 text. Do not strip punctuation or lowercase for audio identity. The phrase's stable code is its utterance ID; its text hash is also exposed for technical traceability.

Same spelling in different dialects must remain separate utterances. Same text with different pronunciation context uses a distinct `pronunciation_context_id`; this enters both utterance uniqueness and synthesis input. German/support-language audio is optional and uses separate language-specific voice profiles.

### Audio fingerprint

```json
{
  "key_schema": 1,
  "text_sha256": "…",
  "language_tag": "gsw-CH",
  "dialect_id": "gsw-zh",
  "pronunciation_context_id": "default",
  "spoken_text_sha256": "…",
  "provider": "resolved-provider",
  "model": "resolved-model",
  "model_revision": "vendor-or-internal-pin",
  "voice_id": "approved-voice",
  "voice_profile_version": 1,
  "synthesis_version": 1,
  "pronunciation_lexicon_version": 1,
  "style": "conversational-neutral",
  "speed": "1.00",
  "format": "mp3",
  "sample_rate_hz": 24000,
  "generation_variant": 0
}
```

The above is the required canonical fingerprint shape; values shown are placeholders, not a selected provider. Serialize sorted keys, UTF-8, compact JSON, explicit nulls and normalized value types; speed uses a fixed-decimal string. `audio_key = sha256(canonical_fingerprint_json)`. Include any additional synthesis-affecting provider parameter in a versioned `provider_options` object. `spoken_text_sha256` covers actual SSML/phonetic instructions if these differ from displayed text. A test fixture must specify the exact serialization and expected hash.

Changing a translation does not invalidate unchanged Swiss audio. Changing dialect, exact spoken content, pronunciation lexicon, voice, model pin, or synthesis version does. A human-requested regeneration of rejected audio increments `generation_variant` and creates a new asset while preserving the old audit record. Cache keys are identifiers, not access credentials.

## 6. Lazy audio generation and durable jobs

1. Client requests audio by **published revision + turn/utterance ID + approved voice profile**. The server resolves exact text and voice; clients cannot submit arbitrary TTS text, provider names, or SSML.
2. Verify that the utterance belongs to content the caller can access. Visitors can play ready assets; the first uncached generation requires a logged-in learner (or admin preview). This is an initial free-project cost-control default.
3. Resolve fingerprint. If approved/usable `ready` metadata exists, return the asset ID and relative stream URL immediately. Never regenerate merely because a model default changed; published voice bindings remain pinned until explicitly upgraded.
4. In a transaction upsert one `media_assets` entry by unique `audio_key` and one durable job by stable dedupe key. Return `202`, job/status URL and recommended poll interval (start at 2s, back off to 10s). Limit polling to 2 minutes before offering a later retry without scheduling duplicate work.
5. A worker claims queued work atomically using `findOneAndUpdate`; set lease owner, random fencing token, `lease_until`, attempts. Renew the lease while calling providers. Finish only if the lease token still matches. Expired workers cannot overwrite newer results.
6. Synthesize with a hard timeout; validate MIME/container, nonzero duration, maximum bytes/duration, valid decode, and absence of provider error payloads. Save bytes to GridFS under a new file ID. Publish `ready` metadata only after upload completion and a compare-and-set against the active lease. Orphan uploads from crashes are reconciled later.
7. Retry transient network/429/5xx failures up to 3 calls with exponential jitter/backoff; do not retry invalid text/unauthorized voice indefinitely. A provider timeout may have completed remotely: reuse provider idempotency IDs where supported. Database deduplication guarantees one visible cache entry, not exactly one billed external call across crashes.
8. On failure show a retryable state and keep text learning available. Failed jobs preserve failure category and next retry time; they never create an apparently playable empty asset. An admin can retry or disable a route.

Default generation limits: 30 uncached turns/user/day, 5 new requests/user/minute, text maximum 600 characters/turn, speech maximum 60 seconds/asset. Ready cached playback does not spend generation quota, but ordinary traffic abuse limits apply. Configure a global daily provider spend cap; reserve estimated cost atomically before calls, reconcile actual cost, release stale reservations only after determining no active call remains. If the budget is exhausted, existing audio continues to work and new audio displays “Generation temporarily unavailable.” Values are DB configuration and operational defaults, not paywalls.

Store `media_assets` metadata (fingerprint, utterance, GridFS ID, checksum, duration, byte size, provider result, QA, generation provenance), `jobs` execution state, and `ai_runs` usage separately. No audio TTL and no routine cache eviction. Retain reusable first-party lesson audio after a learner deletes their account; delete/quarantine specific media only for moderation, correction, rights issues or an explicit administrator action. Back up files/chunks plus metadata consistently.

Serving: `GET /media/{id}/stream` supports HEAD, range requests, Content-Type, length, ETag and immutable caching for publicly available immutable assets. Stream incrementally; do not load large files entirely into RAM. Private draft media requires authorization and `private, no-store`; withdrawn/quarantined assets fail delivery authorization. Public cached assets cannot be recalled from a user's already cached device; use new asset IDs for corrections and disable old URLs at origin. Full-dialogue “play” queues turn-level assets sequentially, requests missing turns on explicit playback, and supports stop, repeat, playback speed, and role playback. Playback speed changes in the browser do not generate new files.

## 7. Progress consistency

An attempt pins user, dialect, curriculum release/node when applicable, lesson revision, grading configuration, exercise selection, random seed, and start time. The server selects exercises and excludes answer keys. Save partial answers with optimistic version checks. Submission validates item IDs, allowed answer types, attempt ownership, and unfinished status.

Completion transaction: finalize attempt/score → upsert node completion for the pinned enrollment → update objective review records → insert deterministic reward entries → update progress projection and qualifying day → audit relevant action. Retry the entire transaction on transient conflicts; return the previously committed result on duplicate idempotency key. Completed attempts cannot be rescored under newer content. Projections can be rebuilt from attempts/reward ledger; use reconciliation jobs to detect drift.

Current launch is online-first. Future mobile can cache published bundles/media with release checksums and submit answers after reconnection. Do not grant offline rewards locally. Any future sync API must enforce event IDs, ownership, immutable revision IDs, server grading, and withdrawal/retirement rules. Reserve a schema version in exported bundles now; full offline synchronization is not required in the web launch.

## 8. Operations and reliability

- `/health/live` verifies the process; `/health/ready` checks database connectivity, required migrations and queue readiness without exposing credentials. Provider outages do not make cached learning unavailable.
- Structured logs have request/job IDs, durations, safe error codes, and no raw auth tokens, provider secrets or unnecessary personal data. Capture AI costs and audio cache hit ratio in MongoDB summaries; avoid a third-party analytics dependency at launch.
- Initial targets: cached content API p95 <500ms at 50 concurrent learners on agreed staging hardware; first audio byte <1s for ready assets on the same test network; page LCP <2.5s in an agreed mobile test. First-time AI generation is asynchronous, with latency measured and displayed, never a guaranteed instantaneous response.
- Database writes use appropriate acknowledged/majority concerns for auth/publication/rewards; indexes are migrations, not expensive work on every request. A separate migration role owns schema/index changes.
- Daily encrypted DB backups include GridFS; initial recovery targets RPO 24h/RTO 4h. Perform a real restore rehearsal before launch and periodically thereafter. MongoDB is not “permanent storage” without backups and tested recovery.
- Suggested retention defaults: unconsumed challenges 15 minutes; sessions ≤30 days; idempotency receipts 7 days; failed/completed job details 90 days; raw operational/request metrics 30 days; AI provenance tied to published content and audio as long as those exist; minimal admin audit 1 year. Configure final policies explicitly and surface them in account/privacy copy.
- Account deletion revokes sessions immediately and enqueues deletion of profile, identities, attempts, bookmarks, enrollments, reviews, rewards, activity and user-linked request records. Keep shared published content/media, remove or pseudonymize actor references according to the documented audit policy, and explain backup aging. Export includes user profile and learning records, not private grading keys/provider credentials. Do not promise deletion from immutable backups instantly.
- Implement `dry-run` and restartable jobs for destructive/account maintenance operations. All admin write actions emit audit records. No new tracking SDK or public user profile is required.

Configuration variables: `MONGODB_URI`, `MONGODB_DATABASE`, `PUBLIC_WEB_BASE_URL`, `PUBLIC_API_BASE_URL`, `ALLOWED_ORIGINS`, email sender/adapter secret reference, auth token/cookie configuration, and provider secret references. Keep production HTTPS URLs and demo basename configurable; do not hard-code localhost or domain roots in email links.
