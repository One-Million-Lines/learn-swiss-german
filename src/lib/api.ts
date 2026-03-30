const API_BASE = import.meta.env.VITE_API_BASE;
const DATA_BASE = import.meta.env.BASE_URL + "data";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${DATA_BASE}${path}`);
  if (!res.ok) throw new Error(`Static JSON error: ${res.status}`);
  return res.json();
}

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
  level: "beginner" | "intermediate";
  title: string;
  situation: string;
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

export interface PatternExample {
  german: string;
  swissGerman: string;
  english: string;
}

export interface Pattern {
  id: string;
  title: string;
  description: string;
  examples: PatternExample[];
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

export const api = {
  getTopics: () =>
    fetchJson<Topic[]>("/topics.json").then((topics) => ({ topics })),
  getTopic: async (id: string) => {
    const [topics, index, vocabulary] = await Promise.all([
      fetchJson<Topic[]>("/topics.json"),
      fetchJson<{ id: string; topicId: string; title: string; description: string; dialogueCount: number }[]>("/subtopics/index.json"),
      fetchJson<VocabularyGroup[]>("/vocabulary.json"),
    ]);
    const topic = topics.find((t) => t.id === id);
    if (!topic) throw new Error("Topic not found");
    const subtopicMeta = index.filter((s) => s.topicId === id);
    const subtopics = await Promise.all(
      subtopicMeta.map((s) => fetchJson<Subtopic>(`/subtopics/${s.id}.json`))
    );
    const vocab = vocabulary.filter((v) => v.topicId === id);
    return { ...topic, subtopics, vocabulary: vocab };
  },
  getSubtopic: (id: string) =>
    fetchJson<Subtopic>(`/subtopics/${encodeURIComponent(id)}.json`),
  getPatterns: () =>
    fetchJson<Pattern[]>("/patterns.json").then((patterns) => ({ patterns })),
  getVocabulary: (topicId?: string) =>
    fetchJson<VocabularyGroup[]>("/vocabulary.json").then((vocabulary) => ({
      vocabulary: topicId ? vocabulary.filter((v) => v.topicId === topicId) : vocabulary,
    })),
  getDailyPhrase: () =>
    fetchApi<{ phrase: DailyPhrase; date: string }>("/content/daily-phrase"),
  getDailyDialogue: () =>
    fetchApi<{
      dialogue: Dialogue & { subtopicId: string; subtopicTitle: string };
      date: string;
    }>("/content/daily-dialogue"),
};
