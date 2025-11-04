import PhraseCard from "@/components/PhraseCard";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Lock, CheckCircle2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useProgress } from "@/contexts/ProgressContext";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const Learn = () => {
  const { user } = useAuth();
  const { getLevelProgress, isLevelUnlocked } = useProgress();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
    }
  }, [user, navigate]);

  if (!user) return null;

  const levels = [
    {
      level: "Level 1",
      title: "Simple Words",
      description: "Start with essential Swiss German words",
      icon: "📝",
      topics: [
        {
          title: "Basic Greetings",
          icon: "👋",
          phrases: [
            { swissGerman: "Grüezi", german: "Guten Tag", english: "Hello" },
            { swissGerman: "Hoi", german: "Hallo", english: "Hi" },
            { swissGerman: "Tschüss", german: "Auf Wiedersehen", english: "Goodbye" },
          ]
        },
        {
          title: "Common Words",
          icon: "💬",
          phrases: [
            { swissGerman: "Merci", german: "Danke", english: "Thank you" },
            { swissGerman: "Bitte", german: "Bitte", english: "Please" },
            { swissGerman: "Ja", german: "Ja", english: "Yes" },
          ]
        },
        {
          title: "Food Words",
          icon: "🧀",
          phrases: [
            { swissGerman: "Brötli", german: "Brötchen", english: "Bread roll" },
            { swissGerman: "Chäs", german: "Käse", english: "Cheese" },
            { swissGerman: "Wasser", german: "Wasser", english: "Water" },
          ]
        }
      ]
    },
    {
      level: "Level 2",
      title: "Short Sentences",
      description: "Build simple sentences and questions",
      icon: "💭",
      topics: [
        {
          title: "Questions",
          icon: "❓",
          phrases: [
            { swissGerman: "Wie gaht's?", german: "Wie geht's?", english: "How are you?" },
            { swissGerman: "Wo bisch?", german: "Wo bist du?", english: "Where are you?" },
            { swissGerman: "Was machsch?", german: "Was machst du?", english: "What are you doing?" },
          ]
        },
        {
          title: "Simple Statements",
          icon: "💬",
          phrases: [
            { swissGerman: "Mir gaht's guet", german: "Mir geht's gut", english: "I'm doing well" },
            { swissGerman: "Das isch guet", german: "Das ist gut", english: "That's good" },
            { swissGerman: "Ich verstah", german: "Ich verstehe", english: "I understand" },
          ]
        },
        {
          title: "Daily Actions",
          icon: "🚶",
          phrases: [
            { swissGerman: "Ich gang hei", german: "Ich gehe heim", english: "I'm going home" },
            { swissGerman: "Ich chume", german: "Ich komme", english: "I'm coming" },
            { swissGerman: "Ich esse", german: "Ich esse", english: "I'm eating" },
          ]
        }
      ]
    },
    {
      level: "Level 3",
      title: "Small Conversations",
      description: "Practice real-world dialogues",
      icon: "🗣️",
      topics: [
        {
          title: "Greeting Someone",
          icon: "👋",
          phrases: [
            { swissGerman: "Grüezi, wie gaht's?", german: "Guten Tag, wie geht's?", english: "Hello, how are you?" },
            { swissGerman: "Guet, danke! Und dir?", german: "Gut, danke! Und dir?", english: "Good, thanks! And you?" },
          ]
        },
        {
          title: "At a Café",
          icon: "☕",
          phrases: [
            { swissGerman: "En Kafi, bitte", german: "Einen Kaffee, bitte", english: "A coffee, please" },
            { swissGerman: "Was chostet das?", german: "Was kostet das?", english: "How much is that?" },
          ]
        },
        {
          title: "Making Plans",
          icon: "📅",
          phrases: [
            { swissGerman: "Häsch Ziit?", german: "Hast du Zeit?", english: "Do you have time?" },
            { swissGerman: "Ich gang ga schaffe", german: "Ich gehe zur Arbeit", english: "I'm going to work" },
          ]
        }
      ]
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Your Learning Path
            </h1>
            <p className="text-xl text-muted-foreground">
              Progress through structured levels to master Swiss German
            </p>
          </div>

          <div className="space-y-8">
            {levels.map((level, levelIndex) => {
              const isUnlocked = isLevelUnlocked(level.level);
              const { completed, total } = getLevelProgress(level.level);
              const progress = total > 0 ? (completed / total) * 100 : 0;

              return (
                <Card key={levelIndex} className={`p-6 ${!isUnlocked ? 'opacity-60' : ''}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-4xl">{level.icon}</span>
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-2xl font-bold">{level.title}</h2>
                          {!isUnlocked && <Lock className="h-5 w-5 text-muted-foreground" />}
                          {completed === total && total > 0 && <CheckCircle2 className="h-5 w-5 text-primary" />}
                        </div>
                        <p className="text-muted-foreground">{level.description}</p>
                      </div>
                    </div>
                  </div>

                  {isUnlocked && (
                    <>
                      <div className="mb-6">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="font-medium">Progress</span>
                          <span className="text-muted-foreground">{completed}/{total} completed</span>
                        </div>
                        <Progress value={progress} className="h-2" />
                      </div>

                      <div className="space-y-8">
                        {level.topics.map((topic, topicIndex) => (
                          <div key={topicIndex} className="space-y-4">
                            <div className="flex items-center gap-2">
                              <span className="text-2xl">{topic.icon}</span>
                              <h3 className="text-xl font-semibold">{topic.title}</h3>
                            </div>
                            <div className="grid gap-3">
                              {topic.phrases.map((phrase, phraseIndex) => (
                                <PhraseCard
                                  key={phraseIndex}
                                  phraseId={`${level.level}_${topic.title.toLowerCase().replace(/\s+/g, '_')}_${phraseIndex}`}
                                  swissGerman={phrase.swissGerman}
                                  german={phrase.german}
                                  english={phrase.english}
                                  topic={`${level.level} - ${topic.title}`}
                                />
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </>
                  )}

                  {!isUnlocked && (
                    <div className="text-center py-8">
                      <Lock className="h-12 w-12 mx-auto mb-3 text-muted-foreground" />
                      <p className="text-muted-foreground">
                        Complete the previous level to unlock
                      </p>
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Learn;
