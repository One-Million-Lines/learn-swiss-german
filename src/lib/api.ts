const API_BASE = "http://localhost:5020";

async function fetchApi<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
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
  getTopics: () => fetchApi<{ topics: Topic[] }>("/content/topics"),
  getTopic: (id: string) =>
    fetchApi<Topic & { subtopics: Subtopic[]; vocabulary: VocabularyGroup[] }>(
      `/content/topics/${encodeURIComponent(id)}`
    ),
  getSubtopic: (id: string) =>
    fetchApi<Subtopic>(`/content/subtopics/${encodeURIComponent(id)}`),
  getPatterns: () => fetchApi<{ patterns: Pattern[] }>("/content/patterns"),
  getVocabulary: (topicId?: string) =>
    fetchApi<{ vocabulary: VocabularyGroup[] }>(
      `/content/vocabulary${topicId ? `?topic_id=${encodeURIComponent(topicId)}` : ""}`
    ),
  getDailyPhrase: () =>
    fetchApi<{ phrase: DailyPhrase; date: string }>("/content/daily-phrase"),
  getDailyDialogue: () =>
    fetchApi<{
      dialogue: Dialogue & { subtopicId: string; subtopicTitle: string };
      date: string;
    }>("/content/daily-dialogue"),
};
