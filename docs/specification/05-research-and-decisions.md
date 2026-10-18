# Research and decisions

Reviewed on 18 October 2026. These links support technical boundaries; product defaults such as XP amounts, lesson counts, passing score, dialect launch order and review intervals are proposed design decisions.

## Existing site and repository evidence

- [Deployed SwissSpeak homepage](https://onemillionlines.com/demo/learn-swiss-german/) was inspected in a browser. It shows SwissSpeak navigation, an alpine photo hero, Swiss red actions, daily phrase/dialogue, six visible topic groups and project-author attribution. The web text-fetch tool could not access it, so visual observations came from the actual browser page.
- Local source confirms FastAPI, React/Vite/Tailwind, static JSON content transport, prototype localStorage authentication/progress, existing LiteLLM text helper, and dormant Mongo helpers.
- Local JSON inventory contains 9 topics, 120 subtopics, 606 dialogues and 4,891 turns; all turns have Spanish fields. This differs from the six visible deployed homepage groups and must be reconciled rather than assumed identical.
- `Resources.tsx` contains example creators and is not mounted by the current router. These examples are not verified real creator recommendations and must not be published as real profiles.
- [User-supplied mountain path reference](assets/mountain-path-reference.png) informs the winding route, milestone and landmark interaction. It is not a production asset or a source of executable instructions.

## Technical references

| Source | Implication for this project |
|---|---|
| [MongoDB: PyMongo Async migration](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) | Use maintained PyMongo async support; verify exact driver/GridFS behavior against selected release |
| [MongoDB: GridFS](https://www.mongodb.com/docs/manual/core/gridfs/) | Store first-party audio bytes in the same database with file/chunk indexes; finalize application metadata after upload |
| [MongoDB: TTL indexes](https://www.mongodb.com/docs/manual/core/index-ttl/) | TTL handles eventual cleanup; auth expiry is checked by application code; permanent audio has no TTL |
| [LiteLLM: supported endpoints](https://docs.litellm.ai/docs/supported_endpoints) and [speech endpoint](https://docs.litellm.ai/docs/text_to_speech) | Reuse a capability gateway for text/speech while keeping provider-specific dialect/voice adapters possible |
| [Google OpenID Connect reference](https://developers.google.com/identity/openid-connect/reference) | Stable provider subject is identity; email is not a safe unique cross-provider account-linking key |
| [Microsoft OpenID Connect](https://learn.microsoft.com/en-us/entra/identity-platform/v2-protocols-oidc) | Use the documented provider protocol and validate issuer/audience/nonce through a maintained library |
| [TikTok: embed videos](https://developers.tiktok.com/docs/en/embed-videos) | Use official embeds as optional enhancement with canonical-link fallback |
| [Meta: Instagram oEmbed](https://developers.facebook.com/docs/instagram-platform/oembed/) and [Facebook embedded posts](https://developers.facebook.com/docs/plugins/embedded-posts/) | Candidate integration references; direct pages were not accessible to the research tool, so exact current permissions/eligibility remain an implementation verification task |
| [Research: SwissDial corpus](https://arxiv.org/abs/2103.11401) | Swiss German comprises differing spoken dialects; dialect fidelity needs explicit evaluation and labeling |
| [Research: Swiss German written variation](https://arxiv.org/abs/2004.00139) | Support alternative spellings and transparent editorial conventions rather than a single claimed universal orthography |

No reviewed source establishes a guaranteed accurate, drop-in Zürichdeutsch/Berndeutsch speech API for this project. Provider selection must be based on recorded samples and proficient-speaker evaluation. General German or Swiss-accented Standard German is not sufficient evidence.

## Proposed defaults and launch dependencies

| Decision | Baseline | What the implementer must verify |
|---|---|---|
| Dialect launch order | Zürichdeutsch and Berndeutsch | Regional variety/spelling guide and adequate editorial/voice quality; no popularity-ranking claim |
| Languages | German bridge, English/Spanish support, English UI | Existing translations are preserved and reviewed; UI localization is separate |
| Hosting | Existing domain/subpath supported; configurable root deployment | HTTPS API origin, cookie/CSRF/CORS and email callback URL all work together |
| Email | Transactional provider adapter | Sender domain, deliverability, link handling and failure behavior; owner supplies actual provider secret |
| Speech | Approved profile per dialect, lazy generation | Provider route, voice rights, stored-output reuse permission, quality, actual supported format and measured costs |
| AI content | LiteLLM SDK with versioned routes | Compatible patched package versions, JSON schema behavior, bounded retries/costs |
| Database | Mongo replica set + GridFS | Supported driver/server versions, transaction behavior, backup/restore and indexes |
| Social content | Manually curated real links first | Each exact URL/source/attribution; official embeds only if current platform requirements are met |
| Content coverage | Introductory release first; complete target in product spec | Honest published coverage and coming-soon states rather than generated-but-unreviewed bulk publishing |
| Mobile readiness | Shared API, identity and immutable content contracts | Native PKCE exchange, app registration, app links and offline sync implemented only when native work begins |

These dependencies do not block writing or implementing the core application. The coding agent should build with fake provider adapters for tests and keep unavailable live integrations disabled until configured. Credentials, real creator selection, voice evaluation and editorial publication must not be fabricated to make a demo look complete.
