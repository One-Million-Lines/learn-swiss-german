import React, { createContext, useContext, useState } from "react";

/**
 * Lightweight client-side UI state only (e.g., local favourites). Authoritative
 * learning progress, mastery, streaks and XP now live server-side and are read
 * through `learningApi` (see the Learn / Profile pages). This context no longer
 * stores any passwords, quiz scores or unlock state in localStorage.
 */
interface PhraseProgress {
  phraseId: string;
  topic: string;
  isFavorite: boolean;
  timesPracticed: number;
  lastPracticedAt: string;
}

interface ProgressContextType {
  progress: Record<string, PhraseProgress>;
  quizResults: never[];
  toggleFavorite: (phraseId: string, topic: string) => void;
  markPracticed: (phraseId: string, topic: string) => void;
  getFavorites: () => PhraseProgress[];
  getTopicProgress: (topic: string) => number;
  getTotalPhrasesPracticed: () => number;
  getStreak: () => number;
  getAccuracy: () => number;
  getLevelProgress: (level: string) => { completed: number; total: number };
  isLevelUnlocked: (level: string) => boolean;
}

const ProgressContext = createContext<ProgressContextType | undefined>(undefined);

export const ProgressProvider = ({ children }: { children: React.ReactNode }) => {
  const [progress, setProgress] = useState<Record<string, PhraseProgress>>({});

  const toggleFavorite = (phraseId: string, topic: string) => {
    const key = `${topic}_${phraseId}`;
    setProgress((prev) => {
      const current = prev[key];
      return {
        ...prev,
        [key]: current
          ? { ...current, isFavorite: !current.isFavorite }
          : { phraseId, topic, isFavorite: true, timesPracticed: 0, lastPracticedAt: new Date().toISOString() },
      };
    });
  };

  const markPracticed = (phraseId: string, topic: string) => {
    const key = `${topic}_${phraseId}`;
    setProgress((prev) => {
      const current = prev[key];
      return {
        ...prev,
        [key]: current
          ? { ...current, timesPracticed: current.timesPracticed + 1, lastPracticedAt: new Date().toISOString() }
          : { phraseId, topic, isFavorite: false, timesPracticed: 1, lastPracticedAt: new Date().toISOString() },
      };
    });
  };

  const getFavorites = () => Object.values(progress).filter((p) => p.isFavorite);
  const getTopicProgress = () => 0;
  const getTotalPhrasesPracticed = () => 0;
  const getStreak = () => 0;
  const getAccuracy = () => 0;
  const getLevelProgress = () => ({ completed: 0, total: 0 });
  const isLevelUnlocked = (level: string) => level === "Level 1";

  return (
    <ProgressContext.Provider
      value={{
        progress,
        quizResults: [],
        toggleFavorite,
        markPracticed,
        getFavorites,
        getTopicProgress,
        getTotalPhrasesPracticed,
        getStreak,
        getAccuracy,
        getLevelProgress,
        isLevelUnlocked,
      }}
    >
      {children}
    </ProgressContext.Provider>
  );
};

export const useProgress = () => {
  const context = useContext(ProgressContext);
  if (!context) {
    throw new Error("useProgress must be used within ProgressProvider");
  }
  return context;
};
