const API_BASE = import.meta.env.VITE_API_BASE;
const API_V1 = `${API_BASE}/api/v1`;

function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method || "GET").toUpperCase();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  // Attach CSRF token for cookie-authenticated, state-changing requests.
  if (method !== "GET" && method !== "HEAD") {
    const csrf = readCookie("ss_csrf");
    if (csrf) headers["X-CSRF-Token"] = csrf;
  }
  const res = await fetch(`${API_V1}${path}`, { ...options, headers, credentials: "include" });
  if (!res.ok) {
    let message = `API error: ${res.status}`;
    try {
      const body = await res.json();
      message = body?.error?.message || message;
    } catch {
      /* ignore */
    }
    const err = new Error(message) as Error & { status?: number };
    err.status = res.status;
    throw err;
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

const unwrap = <T>(p: Promise<{ data: T }>): Promise<T> => p.then((r) => r.data);

// --------------------------------------------------------------------------- //
// Content interfaces (stable UI shapes).                                       //
// --------------------------------------------------------------------------- //
export interface Topic {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  subtopicCount: number;
}

export interface DialogueLine {
  speaker: string;
  swissGerman: string;
  german: string;
  english: string;
  spanish?: string;
  turnId?: string;
  utteranceId?: string;
}

export interface Difference {
  swissGerman: string;
  german: string;
  explanation: string;
}

export interface KeyPhrase {
  swissGerman: string;
  german: string;
  english: string;
}

export interface Dialogue {
  id: string;
  itemId?: string;
  revision?: number;
  level: "beginner" | "intermediate";
  title: string;
  situation: string;
  dialectVerified?: boolean;
  dialectLabel?: string;
  lines: DialogueLine[];
  differences: Difference[];
  keyPhrases: KeyPhrase[];
}

export interface Subtopic {
  id: string;
  topicId: string;
  title: string;
  description: string;
  dialogues: Dialogue[];
}

export interface Pattern {
  id: string;
  title: string;
  description: string;
  examples: { german: string; swissGerman: string; english: string; spanish?: string }[];
}

export interface Word {
  swissGerman: string;
  german: string;
  english: string;
}

export interface VocabularyGroup {
  id: string;
  topicId: string;
  title: string;
  words: Word[];
}

export interface DailyPhrase {
  swissGerman: string;
  german: string;
  english: string;
  topic: string;
}

interface ApiTurn {
  id: string;
  speaker: string;
  swiss_german: string;
  german: string;
  translation: string;
  translations?: Record<string, string>;
  utterance_id?: string;
}

interface ApiDialogue {
  id: string;
  legacy_id?: string;
  revision?: number;
  title: string;
  situation: string;
  level: Dialogue["level"];
  dialect_verified?: boolean;
  dialect_label?: string;
  subtopic_id?: string;
  turns: ApiTurn[];
  differences: { swiss_german: string; german: string; explanation: string }[];
  key_phrases: { swiss_german: string; german: string; translations?: Record<string, string> }[];
}

interface ApiExample { german: string; swiss_german: string; english: string; spanish?: string }
interface ApiWord { swiss_german: string; german: string; english: string }

function reshapeDialogue(d: ApiDialogue): Dialogue {
  return {
    id: d.legacy_id || d.id,
    itemId: d.id,
    revision: d.revision,
    level: d.level,
    title: d.title,
    situation: d.situation,
    dialectVerified: d.dialect_verified,
    dialectLabel: d.dialect_label,
    lines: d.turns.map((t) => ({
      speaker: t.speaker,
      swissGerman: t.swiss_german,
      german: t.german,
      english: t.translations?.en ?? t.translation,
      spanish: t.translations?.es,
      turnId: t.id,
      utteranceId: t.utterance_id,
    })),
    differences: d.differences.map((x) => ({
      swissGerman: x.swiss_german,
      german: x.german,
      explanation: x.explanation,
    })),
    keyPhrases: d.key_phrases.map((k) => ({
      swissGerman: k.swiss_german,
      german: k.german,
      english: k.translations?.en ?? "",
    })),
  };
}

export interface Dialect {
  code: string;
  labels: Record<string, string>;
  status: string;
  voice_review_status?: string;
}

export interface HomePayload {
  homepage: { hero?: Record<string, string>; sections?: string[] };
  topics: (Topic & { subtopic_count: number })[];
  daily: { date: string; phrase: unknown; dialogue: ApiDialogue | null };
  sample: ApiDialogue | null;
  creators: { slug: string; name: string; bio?: string; profile_links: unknown[] }[];
}

// --------------------------------------------------------------------------- //
// Public content API (used by existing pages).                                 //
// --------------------------------------------------------------------------- //
export const api = {
  getTopics: () =>
    unwrap<(Topic & { subtopic_count: number })[]>(request("/topics")).then((data) => ({
      topics: data.map((t) => ({ ...t, subtopicCount: t.subtopic_count })),
    })),

  getTopic: async (id: string) => {
    const t = await unwrap<{
      id: string; title: string; description: string; icon: string; color: string;
      subtopics: { id: string; title: string; description: string; dialogue_count: number }[];
      vocabulary: { id: string; topic_id: string; title: string; words: ApiWord[] }[];
    }>(request(`/topics/${encodeURIComponent(id)}`));
    return {
      id: t.id,
      title: t.title,
      description: t.description,
      icon: t.icon,
      color: t.color,
      subtopics: t.subtopics.map((s) => ({
        id: s.id, topicId: t.id, title: s.title, description: s.description,
        dialogues: new Array(s.dialogue_count).fill(null) as Dialogue[],
      })),
      vocabulary: t.vocabulary.map((g) => ({
        id: g.id, topicId: g.topic_id, title: g.title,
        words: g.words.map((w) => ({ swissGerman: w.swiss_german, german: w.german, english: w.english })),
      })),
    };
  },

  getSubtopic: async (id: string): Promise<Subtopic> => {
    const s = await unwrap<{ id: string; topic_id: string; title: string; description: string; dialogues: ApiDialogue[] }>(
      request(`/subtopics/${encodeURIComponent(id)}`)
    );
    return {
      id: s.id, topicId: s.topic_id, title: s.title, description: s.description,
      dialogues: s.dialogues.map(reshapeDialogue),
    };
  },

  getDialogue: (id: string) =>
    unwrap<ApiDialogue>(request(`/dialogues/${encodeURIComponent(id)}`)).then(reshapeDialogue),

  getPatterns: () =>
    unwrap<{ id: string; title: string; description: string; examples: ApiExample[] }[]>(request("/patterns")).then(
      (patterns) => ({
        patterns: patterns.map((p) => ({
          id: p.id, title: p.title, description: p.description,
          examples: p.examples.map((e) => ({
            german: e.german, swissGerman: e.swiss_german, english: e.english, spanish: e.spanish,
          })),
        })),
      })
    ),

  getVocabulary: (topicId?: string) =>
    unwrap<{ id: string; topic_id: string; title: string; words: ApiWord[] }[]>(
      request(`/vocabulary${topicId ? `?topic_id=${encodeURIComponent(topicId)}` : ""}`)
    ).then((groups) => ({
      vocabulary: groups.map((g) => ({
        id: g.id, topicId: g.topic_id, title: g.title,
        words: g.words.map((w) => ({ swissGerman: w.swiss_german, german: w.german, english: w.english })),
      })),
    })),

  getDailyPhrase: () =>
    unwrap<{ date: string; phrase: { swiss_german: string; german: string; translation: string; topic: string } | null }>(
      request("/daily")
    ).then((d) => ({
      date: d.date,
      phrase: d.phrase
        ? { swissGerman: d.phrase.swiss_german, german: d.phrase.german, english: d.phrase.translation, topic: d.phrase.topic }
        : { swissGerman: "", german: "", english: "", topic: "" },
    })),

  getDailyDialogue: () =>
    unwrap<{ date: string; dialogue: ApiDialogue | null }>(request("/daily")).then((d) => ({
      date: d.date,
      dialogue: d.dialogue
        ? { ...reshapeDialogue(d.dialogue), subtopicId: d.dialogue.subtopic_id, subtopicTitle: d.dialogue.title }
        : null,
    })),

  getDialects: () => unwrap<Dialect[]>(request("/dialects")),
  getHome: (supportLanguage = "en") => unwrap<HomePayload>(request(`/home?support_language=${supportLanguage}`)),
};

// --------------------------------------------------------------------------- //
// Auth API (magic link).                                                       //
// --------------------------------------------------------------------------- //
export interface AuthUser {
  id: string;
  email: string;
  display_name: string | null;
  roles: string[];
  preferences: Record<string, unknown>;
  onboarding: Record<string, unknown>;
}

export const authApi = {
  requestMagicLink: (email: string, returnPath = "/auth/callback") =>
    request("/auth/magic-links", { method: "POST", body: JSON.stringify({ email, return_path: returnPath }) }),
  consume: (token: string) =>
    unwrap<{ user: AuthUser; csrf_token: string }>(
      request("/auth/magic-links/consume", { method: "POST", body: JSON.stringify({ token }) })
    ),
  me: () => unwrap<AuthUser>(request("/me")),
  refresh: () => request("/auth/refresh", { method: "POST" }),
  logout: () => request("/auth/logout", { method: "POST" }),
  updateProfile: (patch: Record<string, unknown>) =>
    unwrap<AuthUser>(request("/me", { method: "PATCH", body: JSON.stringify(patch) })),
};

// --------------------------------------------------------------------------- //
// Learning API.                                                                //
// --------------------------------------------------------------------------- //
export interface PathNode {
  id: string;
  stage_id: string;
  kind: string;
  title: string;
  required: boolean;
  lesson_ref: { item_id: string; revision: number };
  layout: { x: number; y: number; segment: string };
  state: "coming_soon" | "locked" | "available" | "in_progress" | "completed";
  reason: string;
  review_due: boolean;
}

export interface EnrollmentPath {
  enrollment: { id: string; current_node_id: string; projection: Record<string, number> };
  dialect_id: string;
  provenance?: { source?: string };
  stages: { id: string; name: string; landmark: string; outcomes: string[] }[];
  nodes: PathNode[];
}

export interface LessonExercise {
  id: string;
  kind: string;
  prompt: string;
  choices: { id: string; text: string }[];
  objective_ids: string[];
}

export interface LessonData {
  id: string;
  title: string;
  estimated_duration_min: number;
  dialect_verified: boolean;
  dialogues: ApiDialogue[];
  exercises: LessonExercise[];
}

export interface AttemptData {
  id: string;
  version: number;
  exercises: LessonExercise[];
}

export interface SubmitResult {
  attempt_id: string;
  score: { correct: number; total: number };
  passed: boolean;
  awarded_xp: number;
  next_node_id: string | null;
  completed_node_id: string | null;
}

export const learningApi = {
  enroll: (curriculumKey: string, dialectId: string) =>
    unwrap<{ id: string }>(request("/me/enrollments", { method: "POST", body: JSON.stringify({ curriculum_key: curriculumKey, dialect_id: dialectId }) })),
  enrollments: () => unwrap<{ id: string; dialect_id: string; curriculum_key: string }[]>(request("/me/enrollments")),
  path: (enrollmentId: string) => unwrap<EnrollmentPath>(request(`/me/enrollments/${enrollmentId}/path`)),
  lesson: (lessonId: string) => unwrap<LessonData>(request(`/lessons/${lessonId}`)),
  createAttempt: (body: Record<string, unknown>) =>
    unwrap<AttemptData>(request("/attempts", { method: "POST", body: JSON.stringify(body) })),
  submitAttempt: (attemptId: string, body: Record<string, unknown>, idempotencyKey: string) =>
    unwrap<SubmitResult>(request(`/attempts/${attemptId}/submit`, {
      method: "POST",
      headers: { "Idempotency-Key": idempotencyKey },
      body: JSON.stringify(body),
    })),
  progress: (dialectId = "gsw-zh") =>
    unwrap<{ attempts: number; passed: number; earned_xp: number; due_reviews: number; streak_days: number; remembered_objectives: number }>(
      request(`/me/progress?dialect_id=${dialectId}`)
    ),
  reviews: (dialectId = "gsw-zh") => unwrap<{ due_count: number; has_session: boolean }>(request(`/me/reviews?dialect_id=${dialectId}`)),
};

// --------------------------------------------------------------------------- //
// Audio API (lazy per-turn generation).                                        //
// --------------------------------------------------------------------------- //
export interface AudioResult {
  status: "ready" | "queued" | "generating" | "failed";
  media_id?: string;
  stream_url?: string;
  duration_ms?: number;
  ai_generated?: boolean;
  human_reviewed?: boolean;
  request_id?: string;
  poll_after_seconds?: number;
}

export const audioApi = {
  request: (itemId: string, revision: number, turnId: string, languageTag = "gsw-CH") =>
    unwrap<AudioResult>(
      request("/audio/requests", {
        method: "POST",
        body: JSON.stringify({ content_ref: { item_id: itemId, revision }, turn_id: turnId, language_tag: languageTag }),
      })
    ),
  status: (requestId: string) => unwrap<AudioResult>(request(`/audio/requests/${requestId}`)),
  streamUrl: (streamPath: string) => `${API_V1}${streamPath.replace(/^\/api\/v1/, "")}`,
};
