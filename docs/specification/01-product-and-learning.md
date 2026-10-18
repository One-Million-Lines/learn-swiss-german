# Product, learning method, and interface

## 1. Purpose and audience

SwissSpeak helps German-speaking newcomers understand and participate in everyday Swiss German conversations. Its central object is a realistic dialogue presented in a selected Swiss dialect, Standard German, and a support language.

The learner already understands entry-level German, approximately A2 as a suggested starting point. This is a recommendation, not an admission test. Explain the prerequisite before starting and allow everyone to try the introductory material. Do not teach the German alphabet or represent the programme as a complete beginner German course.

Core promise: “You know some German. Learn how everyday conversations sound in Switzerland.” Initial outcomes: follow familiar situations, notice recurring dialect differences, choose an appropriate response, and rehearse a role in a full conversation.

## 2. User roles and entry flows

| Role | Permissions |
|---|---|
| Visitor | Browse published topics/dialogues, discover creators, try a sample lesson and cached audio |
| Learner | Save profile/preferences, request uncached audio within limits, enroll in paths, submit assessments, review, bookmark, sync devices |
| Editor | Generate/edit drafts, translate, manage creator suggestions, inspect QA and preview |
| Publisher | Editor permissions plus publish/withdraw approved content and curriculum releases |
| Administrator | Manage roles, AI routes/budgets, system configuration, retention/export jobs, and audit access |

Publisher and administrator permissions may belong to one person initially. Enforce permissions in the API; hiding buttons is insufficient. No open self-service admin registration.

Visitor flow: homepage → try a short dialogue → choose dialect and translation → optional sample checks → create account to save learning. Sample state is temporary and must never create verified mastery by itself.

New learner flow: email → magic link → display name (optional) → support language → primary dialect → German familiarity and goal → optional starting-point check → introductory route or recommended next stage. Preferences and onboarding status save in MongoDB.

Returning learner flow: “Continue your journey” → current node or due review → lesson → completion explanation → next unlocked step. Resume the exact published lesson version of an in-progress attempt.

Profile: display name, verified email, support language, UI language, active dialect, IANA time zone, daily goal (5/10/15 minutes as guidance), learning intent, joined date, completed summits, and linked identity methods. Launch UI language is English; support language controls translations, not automatically the whole interface. Email changes require fresh verification; role changes cannot come through profile updates.

## 3. Dialects and language handling

Launch dialect identifiers: `gsw-zh` (Zürichdeutsch), `gsw-be` (Berndeutsch). These are internal stable product IDs, not assertions that these strings are registered BCP 47 language tags. Use `gsw-CH` as the general Swiss German language tag with a separate dialect ID; Standard German uses `de-CH`, translations initially `en` and `es`.

Each dialect record has display names, region description, house spelling guide, pronunciation guidance, editorial sources, status, and available voice profiles. Future records: `gsw-vs`, `gsw-sg`, initially disabled. A canton label describes a teaching variety; document the chosen local variety and do not imply every speaker in a canton speaks identically.

Switching dialect changes available dialogues, pronunciation notes, voice, path enrollment, review queue, and mastery. It does not erase the previous dialect's progress. A global profile summary may combine achievements but must label their dialect. A shared scenario can have different idiomatic wording in each dialect; do not force word-for-word substitutions.

Display the active dialect near every dialogue and player. If a variant is missing, show “Not available in Berndeutsch yet” with an explicit option to view Zürichdeutsch. Never silently mix dialects. Legacy unlabeled content remains “Swiss German — dialect not verified” in the library and cannot enter a dialect-specific path until reviewed.

Swiss German spelling has variation. Store accepted variants per exercise and explain that the spelling guide is an editorial convention. Never reject a valid alternative solely for differing from the house spelling.

## 4. Dialogue-based teaching method

Use a consistent “Understand → Notice → Rehearse → Respond → Recall” cycle. A lesson takes roughly 8–12 minutes, contains one main dialogue of 6–12 turns, 3–5 target chunks, 1–3 pronunciation/grammar observations, and 5–8 scored items. Longer legacy dialogues can remain library references or split into coherent lesson scenes.

1. **Set the scene.** Who is speaking, where, relationship/formality, the practical goal, and a one-sentence learning outcome.
2. **Understand.** Read or listen to the whole exchange; identify the situation and speaker intent. Translations are available; there is no penalty for using them in study mode.
3. **Notice.** Show aligned dialect/Standard German/support-language turns. Highlight meaningful chunks and explain differences in context. Avoid universal sound-change rules with no exceptions.
4. **Rehearse.** Play individual turns, repeat a section, and shadow one role. Hide/show that role's text. Completion is self-reported practice, not an AI pronunciation grade.
5. **Respond.** Use the same situation in comprehension, response selection, chunk reconstruction, and one changed-detail scenario. Prefer whole meaningful turns over disconnected single-word drills.
6. **Recall.** Final short assessment without answer reveals. Explain each answer using the original dialogue and offer a retry or focused review.

Example lesson brief: buying bread and coffee. Outcome: understand a follow-up question, order politely, and respond to the price/payment question. The main dialogue covers greeting → order → clarification → price → payment → farewell. A transfer item changes the quantity or asks whether the order is takeaway. Generate exact wording separately for each dialect; the specification does not provide unreviewed teaching sentences as authoritative examples.

### Assessment and completion

- Study interactions and reveals are unscored. A scored assessment has at least 5 equally weighted gradable items, server-stored answer keys, and a versioned configuration.
- Initial pass threshold: 80% (round neither numerator nor ratio before comparison). Retry freely; preserve attempt history and first/best/latest score.
- Required lesson completion = study steps acknowledged + assessment passed. Audio consumption and microphone use are never required for an ordinary lesson completion.
- A listening-only item requires the relevant cached/generated audio. If unavailable, pause/retry or select an approved equivalent non-audio item with the same objective. Do not silently award a correct listening response.
- Summit checkpoints use at least 10 items spanning their required lessons, require 80%, and include at least two contextual response/transfer items. Only include listening items when an audio-ready equivalent/fallback policy exists.
- Client requests contain answers and acknowledgements, never trusted score/XP/unlock flags. Answer keys and acceptable-answer lists stay out of pre-submission learner payloads.
- Launch automatic grading covers multiple choice, ordering of stable chunk IDs, and constrained text answers with editorially accepted variants. Free spoken/written roleplay is practice and receives no gatekeeping AI score.
- Normalize Unicode and case only where the exercise permits; trim/collapse whitespace. Preserve umlauts and meaning-bearing punctuation. An exercise-specific punctuation policy is versioned. Do not apply approximate spelling/LLM judgment to milestone unlocks at launch.

### Review and mastery

Track mastery for a target chunk/objective within a dialect, not simply for a page visit. Correct first scored retrieval advances its review stage; an incorrect retrieval resets stage to zero. Initial due intervals after successful retrieval: 1, 3, 7, 14, 30 days, then repeat at 30 days. Advance at most once per objective per local day so retries cannot inflate mastery. Failed retrieval is due next local day and also offered immediately for practice.

“Practised” = interacted with the chunk; “Learning” = one successful scored retrieval; “Remembered” = three successful scored retrievals on separate local days. These are product indicators, not scientific certification. The dashboard shows attempts, recent accuracy, due reviews, and completed route nodes independently.

## 5. Mountain journey

Hierarchy: curriculum → ordered stages/summits → nodes → lesson/checkpoint references. Every published curriculum release is an immutable, validated directed acyclic graph. Store node positions and prerequisites in MongoDB. A node can be a lesson, review stop, optional exploration, or summit checkpoint.

Proposed first journey (sequence is pedagogical, not geographic or ranked by mountain difficulty):

| Stage | Theme | Example content | Completion landmark |
|---|---|---|---|
| 0: Discover Switzerland | Bridge from German; greetings, high-frequency chunks, listening differences, politeness | 6 introductory lessons + checkpoint | Welcome trail badge |
| 1: Rigi | Everyday essentials | introductions, time, numbers, directions, ordering | Rigi summit |
| 2: Pilatus | Daily independence | shops, transport, appointments, housing | Pilatus summit |
| 3: Säntis | People and belonging | neighbours, invitations, opinions, clarification | Säntis summit |
| 4: Jungfrau | Work, family, services | colleagues, school, doctor, administration | Jungfrau summit |
| 5: Matterhorn | Flexible conversations | longer exchanges, misunderstandings, mixed scenarios | Matterhorn summit |

Stages 1–5 target 8 lessons plus one checkpoint each. Initial complete release target: 46 lessons and 6 checkpoints per dialect (92 dialect-specific lessons total). Reuse scenarios where helpful; publish a smaller coherent journey if necessary, clearly showing later stages as “Coming soon” and excluding them from available completion totals. Never seed fake completed lessons or advertise unavailable content as ready.

“A to B” means practical outcomes from unfamiliar everyday speech to confident participation in familiar conversations. UI labels use these stages; do not equate them to certified A1/B1/B2 Swiss German levels. Add optional reference metadata about required Standard German familiarity without claiming CEFR accreditation.

### Node state and unlock rules

States: `coming_soon`, `locked`, `available`, `in_progress`, `completed`; an independent `review_due` flag can coexist with completed. The server returns state and a human-readable reason.

- First required node is available on enrollment. Next required node opens after all declared prerequisites pass.
- Optional nodes never block a required route unless explicitly designated required in a newly published release.
- Checkpoint opens when all required lessons in its stage are completed. Passing grants the summit; next stage opens from the checkpoint prerequisite.
- Enrollment pins curriculum release; a new release does not silently add obligations or remove earned flags. Offer an explicit release migration with a preview of mapped nodes. Completed node credit transfers only through publisher-approved equivalence mappings.
- Switching dialect creates/selects a distinct enrollment. Practice browsing remains free even when the corresponding path node is locked.
- An optional placement check can recommend a stage. Unlocking by placement requires passing the corresponding versioned stage checkpoints; never infer mastery from self-reported German level.

### Rewards

Initial defaults: 20 XP for a first completed lesson, 50 XP for a first passed checkpoint, 5 XP for a due review session with at least 5 scored items and 80% accuracy. A specific due objective can contribute to review rewards once per local day. Cap review XP at 20/day. All rules have a version ID; repeat lesson attempts receive feedback without duplicate completion rewards.

Grant deterministic reward ledger entries, not arbitrary increments from the client. XP is motivation and never substitutes for assessment. No hearts, paid skips, streak purchases, or competitive leaderboards in the free first release.

A streak day qualifies after passing a lesson/checkpoint or completing a qualifying review. Use the learner's stored IANA time zone, distinct qualifying dates, and server receipt timestamps. Two sessions in one day count once; a historical streak does not appear current after missing days. Time zone changes take effect for future events and cannot rewrite prior day keys. No negative penalties or loss of conquered summits.

## 6. Screens and visual requirements

### Preserve the current identity

Keep the existing alpine photo hero with dark overlay and fade into the page, white/off-white background, Swiss red primary, alpine blue secondary, cream muted panels, rounded cards, Lucide icons, and red/white dialogue bubbles. Reuse `index.css` tokens: primary `hsl(348 83% 47%)`, secondary `hsl(207 44% 49%)`, background `hsl(0 0% 98%)`, card white, base radius `0.75rem`, card radius around `1rem`.

Do not replace the whole site with a bright green game board. The illustrated journey belongs inside the Learn experience, using soft alpine greens, cream paths, original mountain landmarks, and the site's red highlights. Give the adult learner practical titles and clear outcomes.

Responsive requirements: no horizontal scroll at 360px; touch controls at least 44px; readable dialogue line height; keyboard-operable menus and players; visible focus; labeled node status beyond color; reduced-motion support; sufficient text contrast in both themes. At narrow widths stack translation columns within each speaker bubble.

### Homepage: an attractive doorway

1. **Hero:** “Grüezi! Understand Swiss German in real life.” Supporting text explains German familiarity and the dialogue approach. Primary CTA “Start discovering”; secondary “Explore dialogues.” Include a compact dialect selector and “Free to learn” reassurance.
2. **Interactive sample:** 3–4 turns from one published dialogue, with dialect/German/support-language labels, translation toggle, and play buttons. Fetch MongoDB content; never place a full generated lesson directly in frontend source.
3. **Your alpine journey:** a compact preview showing Discover Switzerland and the next summit. Link to the accessible full path. Returning users see progress and “Continue” first.
4. **Today's phrase and dialogue:** retain existing sections, use curated/published records, display dialect, and expose exact deep links. Daily selections are deterministic for the configured Europe/Zurich editorial date and dialect; no expensive generation on homepage views.
5. **Real situations:** topic cards preserve current browsing, with verified available lesson/dialogue counts for selected dialect.
6. **Learn from real Swiss voices:** three featured creator cards with platform badge, creator attribution, dialect, why featured, and an outbound “Watch on Instagram/TikTok/Facebook” action. Optional embeds load only after user consent/click.
7. **How it works:** Understand → compare → rehearse → use it. Explain prerequisites and honest AI audio labeling.
8. **Footer:** free project, project author, about, feedback, creators, privacy/terms links, accessibility contact. Keep current attribution unless intentionally edited by administrator.

Use lightweight original landmark illustrations, existing first-party hero assets, and curated samples. Avoid social-feed walls, autoplay audio/video, invented success numbers, or fabricated testimonials. All editorial section copy, selected content IDs, featured order, and imagery references are DB-managed. UI components and theme CSS remain source code.

### Main application

Desktop navigation: Home, Learn, Dialogues/Topics, Patterns, Vocabulary, Creators, profile. Mobile uses compact navigation or bottom navigation for Learn, Explore, Review, Profile. Respect the current production basename `/demo/learn-swiss-german/`; also support root deployment by configuration.

| Screen | Required behavior |
|---|---|
| `/learn` | Winding route, active dialect, current summit, node outcomes, accessible ordered-list toggle, jump to current node |
| `/learn/lessons/:lessonId` | Versioned lesson runner with step navigation, transcript/translation controls, playback, assessment and resume |
| `/review` | Due objectives and short contextual review session, clear empty state |
| `/topics`, `/topics/:slug` | Existing topic hierarchy, dialect/language availability, search/filter and published counts |
| `/subtopics/:slug` | Existing dialogue list and side-by-side explanations, now with per-turn audio and lesson links |
| `/dialogues/:dialogueId` | Stable direct dialogue link, dialect selector and related lesson/objectives |
| `/patterns`, `/vocabulary` | Published dialect-aware reference content; bookmarks and review linkage where applicable |
| `/creators`, `/creators/:slug` | Curated real creators, platform/dialect/topic filters, source attribution, related resources |
| `/profile` | Preferences, achievements, session management, export/delete account actions |
| `/auth`, `/auth/callback` | Request link, check-email/resend state, explicit completion action, used/expired/error handling |

Every data screen supports loading, empty, offline/network error, retry, unavailable dialect, and archived/deleted content states. Clear authenticated TanStack Query caches on logout/user change. Include user ID, dialect, support language, and release in relevant query keys.

## 7. Creator promotion

Launch as a curated directory and selected-post collection, not an automated aggregator. Support Instagram, TikTok, Facebook and optionally YouTube. Reuse `CreatorCard` but remove placeholder identities and generic platform-root links.

Admin flow: paste a real profile/post URL → select platform → enter/verify creator name and handle → tag dialect/topics → write or AI-draft a short neutral explanation → choose a permitted image or generated generic card → preview → publish. Store attribution/source URL, permission or embedding basis, verified date, embed availability, and any expiry/removal request.

Cards must work with only text, platform badge, and canonical link. Prefer approved creator-supplied images or authorized provider metadata; use a branded placeholder otherwise. No downloading/rehosting social videos, unlicensed thumbnails, scraping private profiles, or transcribing third-party work into lessons without explicit permission recorded separately.

Use official platform embed adapters when supported for the exact public resource. Native embeds are optional progressive enhancement: handle unavailable posts, blocked scripts, approval/token failures, removed videos, and consent rejection with a normal outbound link. Do not promise Instagram/Facebook API access before integration eligibility is confirmed.

Suggestions: authenticated learner submits a URL and optional reason, rate-limited, private until moderation. No contact messages are automatically sent to creators. Creator removal requests enter a moderation queue; an administrator can immediately hide all linked resources and remove featured placements. AI can assist descriptions and tagging but cannot establish identity, permission, or endorsement.

## 8. Administration

Add a protected `/admin` application using existing components. Main sections:

- **Dashboard:** draft/review counts, recent publishing, failed AI/audio jobs, budget remaining, reports.
- **Curriculum:** graph and ordered-list editor, prerequisite validation, node positions, summit metadata, completion preview and release/equivalence mapping.
- **Content library:** topics/subtopics, dialogues, phrases, objectives, lessons, exercises, patterns, vocabulary, filters by dialect/status/translation completeness and bulk actions.
- **AI workshop:** structured brief (situation, learner outcome, dialect, difficulty, number of turns, register, target chunks, support languages), prompt template/model route, estimate and bounded batch size, generation, cancellation and retries.
- **Review workspace:** original versus proposed revision diff, three-language preview, variant/spelling notes, automated QA findings, listening preview on demand, change requests, publish controls.
- **Audio library:** cache key/phrase, dialect, resolved provider/model/voice/version, status, cost/duration, reports, approve/reject/quarantine/regenerate action. Never silently overwrite an immutable asset.
- **Creators:** real profile/resource curation, feature scheduling, suggestions and removal queue.
- **Homepage:** section ordering, hero copy/asset, sample dialogue, featured creators, daily-content schedules; preview before publication.
- **Users:** search, role assignments limited to administrators, suspend/reactivate, revocation and account request processing. Never reveal magic tokens, refresh tokens, or provider keys.
- **System:** dialect/voice configuration, AI routes and secret references, budgets, rate limits, publishing validation, migration status and database/index health. Show the index guide from the documentation; no arbitrary shell/database query console.
- **Audit:** actor, action, target, timestamp, before/after revision references, trace ID and reason.

Content states: `draft → generated → in_review → approved → published → archived`. Rejected items return to draft with findings. A published revision is immutable; edits create new drafts. Authors may preview unpublished revisions only through authenticated, expiring preview access. Optimistic concurrency via revision/ETag prevents lost edits. Withdrawal takes effect immediately in public discovery and audio request authorization without deleting historical progress.

Publication gates: valid schemas/references, correct target dialect, aligned translations, meaningful complete dialogue, valid deterministic answer keys, no answer leakage, supported learner difficulty, required attribution, approved voice configuration, no unresolved critical QA reports. AI QA is an advisory check, not evidence of native dialect accuracy. All teaching text may be AI-generated; publishers remain accountable for release quality.
