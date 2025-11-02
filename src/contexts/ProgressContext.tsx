import React, { createContext, useContext, useState, useEffect } from 'react';
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
}

const ProgressContext = createContext<ProgressContextType | undefined>(undefined);

export const ProgressProvider = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  const [progress, setProgress] = useState<Record<string, PhraseProgress>>({});
  const [quizResults, setQuizResults] = useState<QuizResult[]>([]);

  useEffect(() => {
    if (user) {
      const userProgress = localStorage.getItem(`progress_${user.id}`);
      const userQuizResults = localStorage.getItem(`quizResults_${user.id}`);
      
      if (userProgress) setProgress(JSON.parse(userProgress));
      if (userQuizResults) setQuizResults(JSON.parse(userQuizResults));
    } else {
      setProgress({});
      setQuizResults([]);
    }
  }, [user]);

  const saveProgress = (newProgress: Record<string, PhraseProgress>) => {
    if (user) {
      localStorage.setItem(`progress_${user.id}`, JSON.stringify(newProgress));
      setProgress(newProgress);
    }
  };

  const saveQuizResults = (results: QuizResult[]) => {
    if (user) {
      localStorage.setItem(`quizResults_${user.id}`, JSON.stringify(results));
      setQuizResults(results);
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
