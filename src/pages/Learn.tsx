import PhraseCard from "@/components/PhraseCard";
import { Button } from "@/components/ui/button";
import { ChevronRight } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";

const Learn = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      navigate('/auth');
    }
  }, [user, navigate]);

  if (!user) return null;

  const lessons = [
    {
      title: "Greetings",
      icon: "👋",
      phrases: [
        { swissGerman: "Grüezi", german: "Guten Tag", english: "Hello/Good day" },
        { swissGerman: "Wie gaht's?", german: "Wie geht's?", english: "How are you?" },
        { swissGerman: "Guete Morge", german: "Guten Morgen", english: "Good morning" },
      ]
    },
    {
      title: "Food & Drink",
      icon: "🧀",
      phrases: [
        { swissGerman: "Es Brötli", german: "Ein Brötchen", english: "A bread roll" },
        { swissGerman: "Chuchichäschtli", german: "Küchenschrank", english: "Kitchen cupboard" },
        { swissGerman: "En Kafi", german: "Einen Kaffee", english: "A coffee" },
      ]
    },
    {
      title: "Daily Life",
      icon: "🏔️",
      phrases: [
        { swissGerman: "Ich gang ga schaffe", german: "Ich gehe zur Arbeit", english: "I'm going to work" },
        { swissGerman: "Häsch Ziit?", german: "Hast du Zeit?", english: "Do you have time?" },
        { swissGerman: "Das isch guet", german: "Das ist gut", english: "That's good" },
      ]
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Learn Swiss German
            </h1>
            <p className="text-xl text-muted-foreground">
              Master the essentials with our structured lessons. Each phrase includes audio pronunciation and cultural context.
            </p>
          </div>

          <div className="space-y-12">
            {lessons.map((lesson, index) => (
              <div key={index} className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">{lesson.icon}</span>
                    <h2 className="text-2xl md:text-3xl font-bold">{lesson.title}</h2>
                  </div>
                  <Button variant="ghost" className="gap-2">
                    View All
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>

                <div className="grid gap-4">
                  {lesson.phrases.map((phrase, phraseIndex) => (
                    <PhraseCard
                      key={phraseIndex}
                      phraseId={`${lesson.title.toLowerCase().replace(/\s+/g, '_')}_${phraseIndex}`}
                      swissGerman={phrase.swissGerman}
                      german={phrase.german}
                      english={phrase.english}
                      topic={lesson.title}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 card-swiss text-center">
            <h3 className="text-2xl font-bold mb-4">More lessons coming soon!</h3>
            <p className="text-muted-foreground mb-6">
              We're continuously adding new content to help you master Swiss German
            </p>
            <Button className="gradient-hero">
              Request a Topic
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Learn;
