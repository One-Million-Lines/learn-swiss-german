# MongoDB collections, validation, and index setup

This is the required database setup page for implementers and operators. All application runtime content comes from MongoDB after migration. Files in `data-json/` become migration inputs, not production fallbacks.

## 1. Conventions

- Database name: configurable; default `swissspeak`. Replica set required. Separate credentials and databases for development, staging and production; never share learner records between them.
- Application `_id` values are UUID strings. Stable imported IDs may use a deterministic UUID namespace; keep legacy string IDs in a mapping collection. GridFS file IDs use driver-native ObjectIds and never double as public media IDs.
- Fields use `snake_case`, BSON UTC dates, integer revision numbers, and explicit `schema_version`. Public JSON uses ISO-8601 UTC strings and never exposes MongoDB implementation fields or secrets.
- Mutable documents have `created_at`, `updated_at`, `version`. Immutable records have `created_at`; approved revisions are immutable. Monetary amounts use integer micro-units with a currency code, never floating point. Store user time zones separately from timestamps.
- Do not embed unbounded attempt histories, review events, users or generated files. Bound turn arrays, exercise arrays and small locale maps. Store large media in GridFS. No collection should grow an individual document toward MongoDB's 16 MiB ceiling.
- Explicit repository projections separate public content from private answer keys, audit, credentials and AI prompts. Never serialize entire DB documents directly to learners.
- Application-level foreign-reference validation is mandatory; MongoDB does not supply SQL-style foreign keys. Publishing validates references in a transaction; deletions use archival/withdrawal and explicit cleanup policies.

## 2. Collection catalog

`U(...)` denotes a unique compound index; complete commands appear below. Every application collection also has MongoDB's `_id` index.

### Identity and administration

| Collection | Required fields and relationships | Key queries |
|---|---|---|
| `users` | `_id`, `email_normalized`, `email_verified_at`, optional display name, roles[], status (`active/suspended/deleting`), onboarding state, preferences {support_language, ui_language, active_dialect_id, timezone, daily_goal_minutes, goal}, timestamps/version | U(email_normalized); user lookup |
| `auth_identities` | user_id, provider (`email/google/microsoft`), issuer, subject, email snapshot, verified flag, linked_at | U(provider,issuer,subject); user_id |
| `auth_challenges` | token_hash, purpose, email_normalized, state, client_type, return_path, expires_at, consumed_at; optional user_id for linking/deletion | U(token_hash); TTL(expires_at) |
| `sessions` | user_id, access_hash, access_expires_at, refresh_hash, refresh_expires_at, used_refresh_hashes[] (bounded), family_id, client_type, created_at, last_seen_at, revoked_at, expires_at | U(access_hash), U(refresh_hash), U(family_id); user_id; TTL(expires_at) |
| `native_auth_codes` | code_hash, user_id, client_id, PKCE challenge/method, redirect_uri, consumed_at, expires_at | U(code_hash); TTL(expires_at); create only when native flow implemented |
| `rate_limit_buckets` | bucket_key, window_start, count, expires_at | U(bucket_key,window_start); TTL(expires_at) |
| `audit_log` | actor_user_id or system actor, action, target_type/id, before/after revision refs, reason, request_id, created_at, optional configured expires_at | target/time, actor/time; TTL(expires_at) only after retention policy applied |

Email identity: issuer `swissspeak`, subject = normalized verified email. Provider subjects and emails never appear in public user URLs. Current design uses one verified contact email/user; account email changes update the corresponding identity atomically after fresh verification.

### Content and publishing

| Collection | Required fields and relationships | Key queries |
|---|---|---|
| `dialects` | code, labels, description, regional variety, language_tag, status, spelling_guide_ref, voice_profile_ref, sources | U(code), status |
| `content_items` | kind, slug, optional dialect_id, scenario_id, legacy_id, lifecycle state, published_revision (nullable), draft_revision, title summary, tags[], topic_id/subtopic_id as applicable, timestamps/version | U(kind,slug); kind/dialect/status; topic_id |
| `content_revisions` | item_id, revision, kind, dialect_id, status, payload, private_grading (where applicable), reference list, provenance/QA, created_by, timestamps/version until immutable | U(item_id,revision); status/kind/dialect |
| `utterances` | language_tag, dialect_id, pronunciation_context_id (`default` when absent), canonicalization_version, text, canonical_text, text_sha256, created_at | U(language_tag,dialect_id,pronunciation_context_id,canonicalization_version,text_sha256) |
| `curriculum_releases` | curriculum_key, dialect_id, release_number, status, node array, stage array, graph_hash, grading_config_ref, reward_config_ref, equivalence mapping to prior release, published_at | U(curriculum_key,dialect_id,release_number); dialect/status |
| `app_config` | key, revision, status, payload, created_by/at; includes homepage, daily schedule, grading/rewards, UI copy, budgets, prompts, AI routes, voice profiles | U(key,revision); key/status |
| `config_heads` | `_id` = setting key, published_revision, updated_at/version | direct key lookup |
| `legacy_mappings` | source (`json/python`), entity_type, legacy_id, new_item_id, source_checksum, migration_version, status | U(source,entity_type,legacy_id) |

Content kinds and payload schemas:

- `topic`: localized title/description, icon token/color token, sort order.
- `subtopic`: topic ref, localized title/description, ordered dialogue item IDs.
- `scenario`: situation, communicative goal, speaker roles, register; dialect-neutral.
- `dialogue`: scenario_id, turn array, scene, dialect_id, learning difficulty, key chunks, comparison notes, source/provenance.
- `objective`: outcome, chunk/utterance references, category, dialect_id, review prompts.
- `lesson`: dialogue revision refs, objective IDs, step definitions, selected exercise IDs, estimated duration, completion configuration ref.
- `exercise`: kind, prompt, contextual dialogue/turn ref, public choices/chunks, objective IDs; answer and accepted variants live in `private_grading`, not public payload.
- `checkpoint`: revision-pinned exercise pool, required objective coverage and grading configuration.
- `pattern`: explanatory rule with scope/exceptions, dialect, utterance examples, source notes.
- `vocabulary_group`: topic and bounded entries of utterance refs, notes/objectives.

`content_items` contains stable discovery metadata only. Actual learning text, translated metadata and lesson structures live in revisions/utterances. A published item's discovery projection must update atomically with its published pointer so search never advertises another revision's dialect/title. A daily selection config stores exact dialogue/utterance refs per dialect/date or a deterministic rotation of approved IDs, with fallback if withdrawn. No new daily lesson generation is needed.

Example dialogue revision (IDs are illustrative):

```json
{
  "_id": "revision-uuid",
  "schema_version": 1,
  "item_id": "dialogue-uuid",
  "revision": 1,
  "kind": "dialogue",
  "dialect_id": "gsw-zh",
  "status": "approved",
  "payload": {
    "scenario_id": "scenario-uuid",
    "title": {"en": "Ordering breakfast", "es": "Pedir el desayuno"},
    "situation": {"en": "At a bakery counter"},
    "register": "polite",
    "speakers": [{"id": "customer", "label": "You"}, {"id": "staff", "label": "Staff"}],
    "turns": [{
      "id": "turn-uuid",
      "speaker_id": "customer",
      "utterance_id": "swiss-utterance-uuid",
      "german_utterance_id": "german-utterance-uuid",
      "translation_utterance_ids": {"en": "english-uuid", "es": "spanish-uuid"},
      "objective_ids": ["objective-uuid"],
      "voice_profile_ref": {"key": "voice.gsw_zh.customer", "revision": 1}
    }],
    "comparison_notes": [],
    "key_objective_ids": ["objective-uuid"]
  },
  "references": [{"item_id": "scenario-uuid", "revision": 1}],
  "provenance": {"source": "ai", "ai_run_id": "run-uuid"}
}
```

Require complete scene and translation fields for production; shortened examples here illustrate relationships, not complete publishable records. Dialect ID is the stable code, not a foreign Mongo ObjectId.

Curriculum `nodes[]`: id, stage_id, kind, title, exact lesson/checkpoint revision ref, prerequisite_node_ids[], required flag, layout {x,y,segment}, reward_rule_ref. `stages[]`: id, sequence, summit/landmark name, artwork_media_id, outcomes[], required_node_ids[]. Validate unique node IDs, consistent required sets, no cycles, every node reachable, no cross-dialect content refs, and all pinned revisions approved.

### Learner records

| Collection | Required fields and relationships | Key queries |
|---|---|---|
| `enrollments` | user_id, curriculum_key, dialect_id, release_id, status, current_node_id, projection {completed_count,total_required,earned_xp}, timestamps/version | U(user_id,curriculum_key,dialect_id); user/status |
| `attempts` | user_id, dialect_id, enrollment_id nullable, node_id nullable, lesson/checkpoint revision ref, grading config ref, selected exercises/seed, answers, state, score numerator/denominator, passed, started_at, submitted_at, version | user/time; user/state; enrollment/node |
| `node_progress` | enrollment_id, node_id, state, first_passed_attempt_id, latest_attempt_id, completed_at, review_due, version | U(enrollment_id,node_id) |
| `objective_progress` | user_id, dialect_id, objective_id, practice_count, distinct_success_days, review_stage, last_result, last_success_day, due_at, updated_at/version | U(user_id,dialect_id,objective_id); user/dialect/due_at |
| `reward_ledger` | user_id, enrollment_id nullable, dialect_id, source_key, kind, amount_xp, rule_ref, event_day, created_at | U(user_id,source_key); user/time |
| `activity_days` | user_id, local_date (`YYYY-MM-DD`), timezone_at_award, qualifying_attempt_ids[] bounded, xp_total, created_at | U(user_id,local_date) |
| `bookmarks` | user_id, target_type, target_id, dialect_id, created_at | U(user_id,target_type,target_id,dialect_id); user/time |
| `idempotency_receipts` | user_id, scope, key, request_hash, response_status, safe response payload or resource ref, expires_at | U(user_id,scope,key); TTL(expires_at) |

Use a unique reward source key such as `lesson:{enrollment_id}:{node_id}` or `review:{dialect_id}:{local_date}:{objective_id}`. For a qualifying 5-item review session, allocate its 5 XP to a session key and atomically mark the contributing objectives/day as rewarded; cap all review reward writes per user/day in the same transaction. Do not reward each objective with 5 XP in addition to the session award. Bounded per-day activity arrays may keep only recent evidence; canonical attempts remain in their own collection.

Concurrent devices submitting different attempts for the same node can both store results, but only one completion/reward wins its unique key. Return an authoritative updated projection to both. Reviews should be aggregated into an attempt/session record so objective history can be rebuilt without an unbounded array in the progress document.

### AI, audio, creators, and operations

| Collection | Required fields and relationships | Key queries |
|---|---|---|
| `media_assets` | type, status (`queued/generating/ready/failed/quarantined`), audio_key for speech, utterance_id, fingerprint, gridfs_file_id, content checksum, MIME, bytes/duration, route/profile refs, visibility, QA, created_at | partial U(audio_key string); utterance/status; status/time |
| `media.files`, `media.chunks` | GridFS bucket metadata and binary chunks | driver-required indexes |
| `jobs` | dedupe_key, kind, status, payload refs, available_at, lease_until, lease_token, worker_id, attempts, cancel_requested, result refs, last_error, created_at, expires_at only after final retention eligibility | U(dedupe_key); status/available_at; status/lease_until; TTL(expires_at) |
| `ai_runs` | job_id, purpose, route snapshot, prompt/schema refs, input/output refs, tokens/characters, estimated/actual cost, provider request ID, state, created_at | job_id; purpose/time |
| `budget_buckets` | bucket_key, period_start, limit_microunits, reserved_microunits, spent_microunits, currency, version | U(bucket_key,period_start) |
| `budget_reservations` | request_key, bucket_key, period_start, estimated_microunits, actual_microunits, state, job_id, created_at, settled_at | U(request_key); state/time |
| `creators` | slug, name, bio, profile links[], dialect_ids[], topic_ids[], attribution, verification/permission info, image_media_id nullable, status, featured order/date window | U(slug); status/feature order |
| `creator_resources` | creator_id, platform, canonical_url, provider_resource_id if known, title/description, dialect_ids[], topic_ids[], permitted_thumbnail_ref nullable, embed state, verification_at, status | U(platform,canonical_url); creator/status |
| `reports` | kind (`content/audio/creator_suggestion/removal/feedback`), reporter_user_id nullable, target refs, bounded text/source URL, status, resolution, created_at | status/time; target |
| `migration_runs` | migration_key, checksum, state, source counts, mapped counts, rejected/conflict report refs, started/completed timestamps | U(migration_key) |

Do not store arbitrary third-party embed HTML/scripts as executable content. Store normalized IDs/URLs and render through a platform-specific allowlisted component. Do not fetch arbitrary user-supplied URLs from API servers; use platform host/path allowlists, redirects/DNS checks and bounded metadata adapters to avoid SSRF.

## 3. MongoDB validation policy

The coding agent MUST create JSON Schema validators for every application collection and kind-specific payload validation in Pydantic. Reject unknown sensitive write fields rather than silently mass-assigning them. Use `validationAction: 'error'` and `validationLevel: 'strict'` after a validated initial import. Existing collections require `collMod`; `createCollection` alone does not retrofit validators.

Validator pattern (implement full schemas, not this abbreviated example):

```javascript
db.createCollection('utterances', { validator: { $jsonSchema: {
  bsonType: 'object',
  required: ['_id','schema_version','language_tag','dialect_id',
    'pronunciation_context_id','canonicalization_version','text',
    'canonical_text','text_sha256','created_at'],
  properties: {
    _id: { bsonType: 'string' },
    schema_version: { bsonType: 'int', minimum: 1 },
    language_tag: { bsonType: 'string' },
    dialect_id: { bsonType: ['string','null'] },
    pronunciation_context_id: { bsonType: 'string' },
    canonicalization_version: { bsonType: 'int', minimum: 1 },
    text: { bsonType: 'string', minLength: 1, maxLength: 600 },
    canonical_text: { bsonType: 'string', minLength: 1, maxLength: 600 },
    text_sha256: { bsonType: 'string', pattern: '^[0-9a-f]{64}$' },
    created_at: { bsonType: 'date' }
  }
}}});
```

Utterances longer than the maximum are split editorially, not truncated. Set upload size limits before accepting binary content. Required date fields must be BSON dates for TTL to work.

## 4. Index creation page

Run migrations against an explicit target database using the migration credential. Back up production first, inspect duplicates before unique-index changes, and use a reviewed migration for index replacement. These commands specify index names/options; the implementer should encode them in `scripts/setup_database.py` with `--check`, `--apply`, and environment guards. Do not run destructive `dropDatabase` or automatic index drops.

```javascript
// mongosh: connect using a secret-injected URI; never paste credentials into docs.
const s = db.getSiblingDB('swissspeak'); // substitute configured database explicitly
const ix = (c, key, name, options = {}) =>
  s.getCollection(c).createIndex(key, {name, ...options});
const u = (c, key, name) => ix(c, key, name, {unique: true});
const ttl = c => ix(c, {expires_at: 1}, 'ttl_expires_at', {expireAfterSeconds: 0});

u('users', {email_normalized: 1}, 'u_email');
u('auth_identities', {provider: 1, issuer: 1, subject: 1}, 'u_identity');
ix('auth_identities', {user_id: 1}, 'by_user');
u('auth_challenges', {token_hash: 1}, 'u_token'); ttl('auth_challenges');
u('sessions', {access_hash: 1}, 'u_access');
u('sessions', {refresh_hash: 1}, 'u_refresh');
u('sessions', {family_id: 1}, 'u_family');
ix('sessions', {user_id: 1, revoked_at: 1}, 'by_user_revoked'); ttl('sessions');
u('native_auth_codes', {code_hash: 1}, 'u_code'); ttl('native_auth_codes');
u('rate_limit_buckets', {bucket_key: 1, window_start: 1}, 'u_bucket'); ttl('rate_limit_buckets');
ix('audit_log', {target_type: 1, target_id: 1, created_at: -1}, 'by_target_time');
ix('audit_log', {actor_user_id: 1, created_at: -1}, 'by_actor_time'); ttl('audit_log');

u('dialects', {code: 1}, 'u_code');
u('content_items', {kind: 1, slug: 1}, 'u_kind_slug');
ix('content_items', {kind: 1, dialect_id: 1, status: 1, updated_at: -1, _id: 1}, 'discover');
ix('content_items', {topic_id: 1, kind: 1, status: 1}, 'by_topic');
ix('content_items', {scenario_id: 1, kind: 1, dialect_id: 1}, 'scenario_variants');
u('content_revisions', {item_id: 1, revision: 1}, 'u_item_revision');
ix('content_revisions', {status: 1, kind: 1, dialect_id: 1, updated_at: -1}, 'review_queue');
u('utterances', {language_tag: 1, dialect_id: 1, pronunciation_context_id: 1,
  canonicalization_version: 1, text_sha256: 1}, 'u_utterance');
u('curriculum_releases', {curriculum_key: 1, dialect_id: 1, release_number: 1}, 'u_release');
ix('curriculum_releases', {dialect_id: 1, status: 1, release_number: -1}, 'available_releases');
u('app_config', {key: 1, revision: 1}, 'u_key_revision');
ix('app_config', {key: 1, status: 1}, 'config_status');
u('legacy_mappings', {source: 1, entity_type: 1, legacy_id: 1}, 'u_legacy');

u('enrollments', {user_id: 1, curriculum_key: 1, dialect_id: 1}, 'u_enrollment');
ix('enrollments', {user_id: 1, status: 1}, 'user_enrollments');
ix('attempts', {user_id: 1, submitted_at: -1, _id: 1}, 'user_history');
ix('attempts', {user_id: 1, state: 1, started_at: -1}, 'resume_attempts');
ix('attempts', {enrollment_id: 1, node_id: 1}, 'node_attempts');
u('node_progress', {enrollment_id: 1, node_id: 1}, 'u_node_progress');
u('objective_progress', {user_id: 1, dialect_id: 1, objective_id: 1}, 'u_objective_progress');
ix('objective_progress', {user_id: 1, dialect_id: 1, due_at: 1, _id: 1}, 'due_reviews');
u('reward_ledger', {user_id: 1, source_key: 1}, 'u_reward_source');
ix('reward_ledger', {user_id: 1, created_at: -1}, 'reward_history');
u('activity_days', {user_id: 1, local_date: 1}, 'u_activity_day');
u('bookmarks', {user_id: 1, target_type: 1, target_id: 1, dialect_id: 1}, 'u_bookmark');
ix('bookmarks', {user_id: 1, created_at: -1, _id: 1}, 'user_bookmarks');
u('idempotency_receipts', {user_id: 1, scope: 1, key: 1}, 'u_idempotency'); ttl('idempotency_receipts');

ix('media_assets', {audio_key: 1}, 'u_audio_key',
  {unique: true, partialFilterExpression: {audio_key: {$type: 'string'}}});
ix('media_assets', {utterance_id: 1, status: 1}, 'utterance_audio');
ix('media_assets', {status: 1, created_at: 1}, 'media_operations');
// Drivers normally ensure these GridFS indexes; assert them during setup.
ix('media.files', {filename: 1, uploadDate: 1}, 'filename_1_uploadDate_1');
u('media.chunks', {files_id: 1, n: 1}, 'files_id_1_n_1');
u('jobs', {dedupe_key: 1}, 'u_job_dedupe');
ix('jobs', {status: 1, available_at: 1, _id: 1}, 'claim_queue');
ix('jobs', {status: 1, lease_until: 1}, 'expired_leases'); ttl('jobs');
ix('ai_runs', {job_id: 1}, 'job_runs');
ix('ai_runs', {purpose: 1, created_at: -1}, 'usage_history');
u('budget_buckets', {bucket_key: 1, period_start: 1}, 'u_budget_period');
u('budget_reservations', {request_key: 1}, 'u_budget_request');
ix('budget_reservations', {state: 1, created_at: 1}, 'unsettled_reservations');
u('creators', {slug: 1}, 'u_creator_slug');
ix('creators', {status: 1, featured_order: 1, _id: 1}, 'featured_creators');
u('creator_resources', {platform: 1, canonical_url: 1}, 'u_platform_url');
ix('creator_resources', {creator_id: 1, status: 1}, 'creator_resources');
ix('reports', {status: 1, created_at: 1}, 'moderation_queue');
ix('reports', {target_type: 1, target_id: 1}, 'target_reports');
u('migration_runs', {migration_key: 1}, 'u_migration');
```

Fields absent from a TTL-indexed audit/job record are not automatically expired. Never set `expires_at` on active jobs or permanent media. TTL is asynchronous cleanup: application authorization MUST check expiry/status directly. [MongoDB TTL documentation](https://www.mongodb.com/docs/manual/core/index-ttl/) explains expiration behavior.

GridFS uses separate file metadata and chunks with required indexes; preserve these across restore and deployment. [MongoDB GridFS documentation](https://www.mongodb.com/docs/manual/core/gridfs/) covers the storage contract. GridFS writes are performed outside multi-document transactions; finalize visible application metadata only after a completed upload, using lease fencing and a reconciliation job.

Do not place compound indexes on two independent array fields (such as dialect_ids and topic_ids together). For initial small creator/content sets use indexed status/type plus bounded filtering. Add multikey/text/search indexes only from measured query plans. Launch search can use a normalized bounded `search_text` projection on published metadata; choose one documented simple text index if needed, without requiring paid Atlas Search. Never search private draft/grading fields in the public endpoint.

## 5. Setup runbook

1. Provision TLS-enabled MongoDB replica set and backup storage; create separate runtime, worker and migration principals with minimum privileges.
2. Run schema migration in staging, creating collections/validators and named indexes. Record version/checksum in `migration_runs`.
3. Run setup again: it must be idempotent and report no changes. `--check` compares key order, uniqueness, partial filter, TTL and validators; same names alone are not sufficient.
4. Seed dialects, versioned UI/homepage/grading/reward/route configuration and their heads. Store secret references only. Disable speech routes until evaluation passes. Create the first admin by an explicit one-time CLI with operator-chosen email, audit it, and remove bootstrap capability afterward.
5. Import legacy data using the dry-run/reconciliation process in the delivery document. Preserve unpublished/unverified dialect status.
6. Publish a small validated curriculum and sample homepage, then verify that production API requests succeed when JSON content directories are absent.
7. Check representative queries with `explain('executionStats')`; document intended indexes and bounded examined counts. Measure on a staging corpus matching expected size.
8. Test concurrent completion, session consumption and audio requests; inspect unique constraints and transaction outcomes.
9. Back up, restore to a separate environment, and verify users, published revisions, progress and at least three playable media files.

Initial verification queries:

```javascript
s.getCollection('utterances').getIndexes();
s.getCollection('jobs').getIndexes();
s.getCollection('media_assets').getIndexes();
s.getCollection('objective_progress').find({
  user_id: 'test-user', dialect_id: 'gsw-zh', due_at: {$lte: new Date()}
}).sort({due_at: 1, _id: 1}).limit(20).explain('executionStats');
```

The implemented setup tool must compare the full manifest and fail readiness on missing required migrations. Index changes in production need an explicit migration and reviewed impact; runtime startup must not drop/rebuild indexes automatically.
