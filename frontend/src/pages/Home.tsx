import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { ArrowRight, MessageCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import heroImage from "@/assets/hero-mountains.jpg";

const Home = () => {
  const { data: topicsData, isLoading: topicsLoading } = useQuery({
    queryKey: ["topics"],
    queryFn: api.getTopics,
  });

  const { data: dailyData } = useQuery({
    queryKey: ["daily-phrase"],
    queryFn: api.getDailyPhrase,
  });

  const { data: dailyDialogueData } = useQuery({
    queryKey: ["daily-dialogue"],
    queryFn: api.getDailyDialogue,
  });

  const topics = topicsData?.topics ?? [];

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-background" />
        </div>
        <div className="container relative z-10 mx-auto px-4 pt-20 pb-24 md:pt-32 md:pb-36">
          <div className="max-w-3xl">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              Grüezi! 🇨🇭
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 leading-relaxed">
              Learn Swiss German through real conversations and everyday situations. Using English, German and Spanish.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/topics">
                <Button size="lg" className="gradient-hero w-full sm:w-auto group">
                  Choose a Topic
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link to="/patterns">
                <Button
                  size="lg"
                  variant="outline"
                  className="w-full sm:w-auto bg-white/10 backdrop-blur-sm text-white border-white/20 hover:bg-white/20"
                >
                  <Sparkles className="mr-2 h-5 w-5" />
                  Explore Patterns
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Daily Phrase */}
      {dailyData?.phrase && (
        <section className="py-12 bg-muted/30">
          <div className="container mx-auto px-4 max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">☀️</span>
              <h2 className="text-2xl font-bold">Today's Phrase</h2>
            </div>
            <Card className="card-swiss">
              <p className="text-2xl font-bold text-primary mb-1">{dailyData.phrase.swissGerman}</p>
              <p className="text-lg text-muted-foreground mb-1">{dailyData.phrase.german}</p>
              <p className="text-base text-muted-foreground italic">{dailyData.phrase.english}</p>
              <Badge variant="secondary" className="mt-3">{dailyData.phrase.topic}</Badge>
            </Card>
          </div>
        </section>
      )}

      {/* Daily Dialogue */}
      {dailyDialogueData?.dialogue && (
        <section className="py-12 bg-muted/30">
          <div className="container mx-auto px-4 max-w-3xl">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">💬</span>
              <h2 className="text-2xl font-bold">Today's Dialogue</h2>
            </div>
            <Card className="card-swiss">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-lg font-bold">{dailyDialogueData.dialogue.title}</p>
                  <p className="text-sm text-muted-foreground">{dailyDialogueData.dialogue.situation}</p>
                </div>
                <Badge variant="secondary">{dailyDialogueData.dialogue.level}</Badge>
              </div>

              <div className="space-y-2 mb-4">
                {dailyDialogueData.dialogue.lines.slice(0, 4).map((line, i) => {
                  const isYou = line.speaker.toLowerCase() === "you";
                  return (
                    <div key={i} className={`flex ${isYou ? "justify-end" : "justify-start"}`}>
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
                          isYou
                            ? "bg-primary text-primary-foreground rounded-br-md"
                            : "bg-muted rounded-bl-md"
                        }`}
                      >
                        <p className="text-xs font-medium opacity-70 mb-0.5">{line.speaker}</p>
                        <p className="font-medium">{line.swissGerman}</p>
                        <p className="text-xs opacity-70">{line.english}</p>
                      </div>
                    </div>
                  );
                })}
                {dailyDialogueData.dialogue.lines.length > 4 && (
                  <p className="text-center text-sm text-muted-foreground">
                    +{dailyDialogueData.dialogue.lines.length - 4} more lines
                  </p>
                )}
              </div>

              <Link to={`/subtopics/${dailyDialogueData.dialogue.subtopicId}`}>
                <Button variant="outline" size="sm" className="w-full group">
                  <MessageCircle className="mr-2 h-4 w-4" />
                  See Full Conversation
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </Card>
          </div>
        </section>
      )}

      {/* Recommended Conversations */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold mb-2">Start Here</h2>
          <p className="text-muted-foreground mb-8">Pick a topic to explore conversations, vocabulary and patterns.</p>

          {topicsLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-40 rounded-xl" />
              ))}
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {topics.slice(0, 6).map((topic) => (
                <Link key={topic.id} to={`/topics/${topic.id}`}>
                  <Card className="card-swiss group cursor-pointer hover:shadow-lg transition-all">
                    <div className={`h-2 rounded-t-xl bg-gradient-to-r ${topic.color} -mx-6 -mt-6 mb-4`} />
                    <h3 className="text-xl font-bold mb-1 group-hover:text-primary transition-colors">
                      {topic.title}
                    </h3>
                    <p className="text-sm text-muted-foreground mb-3">{topic.description}</p>
                    <Badge variant="outline">{topic.subtopicCount} subtopics</Badge>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;
