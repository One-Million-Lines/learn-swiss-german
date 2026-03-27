import React, { createContext, useContext, useState } from 'react';
import { useAuth } from './AuthContext';

interface PhraseProgress {
  phraseId: string;
  topic: string;
  isFavorite: boolean;
  timesPracticed: number;
  lastPracticedAt: string;
}

interface QuizResult {
  id: string;
  topic: string;
  score: number;
  totalQuestions: number;
  createdAt: string;
}

interface ProgressContextType {
  progress: Record<string, PhraseProgress>;
  quizResults: QuizResult[];
  toggleFavorite: (phraseId: string, topic: string) => void;
  markPracticed: (phraseId: string, topic: string) => void;
  addQuizResult: (topic: string, score: number, totalQuestions: number) => void;
  getFavorites: () => PhraseProgress[];
  getTopicProgress: (topic: string) => number;
  getTotalPhrasesPracticed: () => number;
  getStreak: () => number;
  getAccuracy: () => number;
  getLevelProgress: (level: string) => { completed: number; total: number };
  isLevelUnlocked: (level: string) => boolean;
}

const ProgressContext = createContext<ProgressContextType | undefined>(undefined);

const loadUserProgress = (userId: string): Record<string, PhraseProgress> => {
  const storedProgress = localStorage.getItem(`progress_${userId}`);
  return storedProgress ? JSON.parse(storedProgress) : {};
};

const loadUserQuizResults = (userId: string): QuizResult[] => {
  const storedQuizResults = localStorage.getItem(`quizResults_${userId}`);
  return storedQuizResults ? JSON.parse(storedQuizResults) : [];
};

export const ProgressProvider = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  const [progressByUser, setProgressByUser] = useState<Record<string, Record<string, PhraseProgress>>>(() =>
    user ? { [user.id]: loadUserProgress(user.id) } : {},
  );
  const [quizResultsByUser, setQuizResultsByUser] = useState<Record<string, QuizResult[]>>(() =>
    user ? { [user.id]: loadUserQuizResults(user.id) } : {},
  );

  const progress = user ? (progressByUser[user.id] ?? loadUserProgress(user.id)) : {};
  const quizResults = user ? (quizResultsByUser[user.id] ?? loadUserQuizResults(user.id)) : [];

  const saveProgress = (newProgress: Record<string, PhraseProgress>) => {
    if (user) {
      localStorage.setItem(`progress_${user.id}`, JSON.stringify(newProgress));
      setProgressByUser((current) => ({
        ...current,
        [user.id]: newProgress,
      }));
    }
  };

  const saveQuizResults = (results: QuizResult[]) => {
    if (user) {
      localStorage.setItem(`quizResults_${user.id}`, JSON.stringify(results));
      setQuizResultsByUser((current) => ({
        ...current,
        [user.id]: results,
      }));
    }
  };

  const toggleFavorite = (phraseId: string, topic: string) => {
    const key = `${topic}_${phraseId}`;
    const newProgress = { ...progress };
    
    if (newProgress[key]) {
      newProgress[key].isFavorite = !newProgress[key].isFavorite;
    } else {
      newProgress[key] = {
        phraseId,
        topic,
        isFavorite: true,
        timesPracticed: 0,
        lastPracticedAt: new Date().toISOString(),
      };
    }
    
    saveProgress(newProgress);
  };

  const markPracticed = (phraseId: string, topic: string) => {
    const key = `${topic}_${phraseId}`;
    const newProgress = { ...progress };
    
    if (newProgress[key]) {
      newProgress[key].timesPracticed++;
      newProgress[key].lastPracticedAt = new Date().toISOString();
    } else {
      newProgress[key] = {
        phraseId,
        topic,
        isFavorite: false,
        timesPracticed: 1,
        lastPracticedAt: new Date().toISOString(),
      };
    }
    
    saveProgress(newProgress);
  };

  const addQuizResult = (topic: string, score: number, totalQuestions: number) => {
    const newResult: QuizResult = {
      id: crypto.randomUUID(),
      topic,
      score,
      totalQuestions,
      createdAt: new Date().toISOString(),
    };
    
    saveQuizResults([...quizResults, newResult]);
  };

  const getFavorites = () => {
    return Object.values(progress).filter(p => p.isFavorite);
  };

  const getTopicProgress = (topic: string) => {
    const topicPhrases = Object.values(progress).filter(p => p.topic === topic && p.timesPracticed > 0);
    return topicPhrases.length;
  };

  const getTotalPhrasesPracticed = () => {
    return Object.values(progress).filter(p => p.timesPracticed > 0).length;
  };

  const getStreak = () => {
    const results = [...quizResults].sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
    
    let streak = 0;
    let lastDate: Date | null = null;
    
    for (const result of results) {
      const resultDate = new Date(result.createdAt);
      resultDate.setHours(0, 0, 0, 0);
      
      if (!lastDate) {
        streak = 1;
        lastDate = resultDate;
      } else {
        const dayDiff = Math.floor((lastDate.getTime() - resultDate.getTime()) / (1000 * 60 * 60 * 24));
        if (dayDiff === 1) {
          streak++;
          lastDate = resultDate;
        } else {
          break;
        }
      }
    }
    
    return streak;
  };

  const getAccuracy = () => {
    if (quizResults.length === 0) return 0;
    const totalScore = quizResults.reduce((sum, r) => sum + r.score, 0);
    const totalQuestions = quizResults.reduce((sum, r) => sum + r.totalQuestions, 0);
    return totalQuestions > 0 ? Math.round((totalScore / totalQuestions) * 100) : 0;
  };

  const getLevelProgress = (level: string) => {
    const levelPhrases = Object.values(progress).filter(p => p.topic.startsWith(level));
    const completed = levelPhrases.filter(p => p.timesPracticed > 0).length;
    
    // Define total phrases per level
    const totals: Record<string, number> = {
      'Level 1': 9,
      'Level 2': 9,
      'Level 3': 6,
    };
    
    return { completed, total: totals[level] || 0 };
  };

  const isLevelUnlocked = (level: string) => {
    if (level === 'Level 1') return true;
    
    if (level === 'Level 2') {
      const level1Progress = getLevelProgress('Level 1');
      return level1Progress.completed >= level1Progress.total;
    }
    
    if (level === 'Level 3') {
      const level2Progress = getLevelProgress('Level 2');
      return level2Progress.completed >= level2Progress.total;
    }
    
    return false;
  };

  return (
    <ProgressContext.Provider value={{
      progress,
      quizResults,
      toggleFavorite,
      markPracticed,
      addQuizResult,
      getFavorites,
      getTopicProgress,
      getTotalPhrasesPracticed,
      getStreak,
      getAccuracy,
      getLevelProgress,
      isLevelUnlocked,
    }}>
      {children}
    </ProgressContext.Provider>
  );
};

export const useProgress = () => {
  const context = useContext(ProgressContext);
  if (!context) {
    throw new Error('useProgress must be used within ProgressProvider');
  }
  return context;
};
