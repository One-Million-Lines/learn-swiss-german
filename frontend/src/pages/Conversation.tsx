import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ArrowRightLeft, Check, Key, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Toggle } from "@/components/ui/toggle";
import { api, type Subtopic } from "@/lib/api";

const SubtopicPage = () => {
  const { subtopicId } = useParams<{ subtopicId: string }>();
  const [dialogueIdx, setDialogueIdx] = useState(0);
  const [visited, setVisited] = useState<Set<number>>(new Set([0]));
  const [showEnglish, setShowEnglish] = useState(() => {
    const saved = localStorage.getItem("lsg-lang-english");
    return saved !== null ? saved === "true" : true;
  });
  const [showSpanish, setShowSpanish] = useState(() => {
    const saved = localStorage.getItem("lsg-lang-spanish");
    return saved !== null ? saved === "true" : false;
  });

  const toggleEnglish = (v: boolean) => {
    setShowEnglish(v);
    localStorage.setItem("lsg-lang-english", String(v));
  };
  const toggleSpanish = (v: boolean) => {
    setShowSpanish(v);
    localStorage.setItem("lsg-lang-spanish", String(v));
  };

  const { data: sub, isLoading } = useQuery<Subtopic>({
    queryKey: ["subtopic", subtopicId],
    queryFn: () => api.getSubtopic(subtopicId!),
    enabled: !!subtopicId,
  });

  const handleSelectDialogue = (i: number) => {
    setDialogueIdx(i);
    setVisited((prev) => new Set(prev).add(i));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen py-12 container mx-auto px-4 max-w-3xl">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-40 rounded-xl mb-6" />
        <Skeleton className="h-60 rounded-xl" />
      </div>
    );
  }

  if (!sub) return null;

  const dialogue = sub.dialogues[dialogueIdx] ?? sub.dialogues[0];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        <Link to={`/topics/${sub.topicId}`}>
          <Button variant="ghost" size="sm" className="mb-4 -ml-2">
            <ArrowLeft className="h-4 w-4 mr-1" /> Back to Topic
          </Button>
        </Link>

        <h1 className="text-3xl font-bold mb-2">{sub.title}</h1>
        <p className="text-muted-foreground mb-6">{sub.description}</p>

        {/* Dialogue list */}
        <div className="space-y-1 mb-8">
          {sub.dialogues.map((d, i) => (
            <button
              key={d.id}
              onClick={() => handleSelectDialogue(i)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
                dialogueIdx === i
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted"
              }`}
            >
              <span className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border ${
                dialogueIdx === i
                  ? "border-primary-foreground/30 text-primary-foreground"
                  : visited.has(i)
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-muted-foreground/30 text-muted-foreground"
              }`}>
                {visited.has(i) && dialogueIdx !== i ? <Check className="h-3 w-3" /> : i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-medium truncate ${dialogueIdx === i ? "" : ""}`}>{d.title}</p>
                <p className={`text-xs truncate ${dialogueIdx === i ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                  {d.level.charAt(0).toUpperCase() + d.level.slice(1)} · {d.lines?.length ?? 0} lines
                </p>
              </div>
            </button>
          ))}
        </div>

        {/* Situation */}
        <Card className="card-swiss bg-muted/50 mb-8">
          <p className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-2">
            {dialogue.title}
          </p>
          <p className="text-lg">{dialogue.situation}</p>
        </Card>

        {/* Dialogue — chat style */}
        <section className="mb-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold">Dialogue</h2>
            </div>
            <div className="flex gap-1.5">
              <Toggle
                variant="outline"
                size="sm"
                pressed={showEnglish}
                onPressedChange={toggleEnglish}
                aria-label="Toggle English"
                className="text-xs gap-1.5"
              >
                🇬🇧 English
              </Toggle>
              <Toggle
                variant="outline"
                size="sm"
                pressed={showSpanish}
                onPressedChange={toggleSpanish}
                aria-label="Toggle Spanish"
                className="text-xs gap-1.5"
              >
                🇪🇸 Spanish
              </Toggle>
            </div>
          </div>
          <div className="rounded-2xl border border-border bg-muted/30 p-5 shadow-inner">
            <div className="space-y-4">
              {dialogue.lines.map((line, i) => {
                const isYou = line.speaker === "You";
                return (
                  <div key={i} className={`flex ${isYou ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[80%] ${isYou ? "items-end" : "items-start"}`}>
                      <p className={`text-xs font-semibold uppercase tracking-wide mb-1 ${
                        isYou ? "text-right text-primary" : "text-secondary"
                      }`}>
                        {line.speaker}
                      </p>
                      <div className={`rounded-2xl px-4 py-3 ${
                        isYou
                          ? "bg-primary text-primary-foreground rounded-br-md"
                          : "bg-background rounded-bl-md shadow-sm"
                      }`}>
                        <p className="font-semibold">{line.swissGerman}</p>
                        <p className={`text-sm mt-1 ${isYou ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                          {line.german}
                        </p>
                        {showEnglish && (
                          <p className={`text-sm italic ${isYou ? "text-primary-foreground/60" : "text-muted-foreground/80"}`}>
                            {line.english}
                          </p>
                        )}
                        {showSpanish && line.spanish && (
                          <p className={`text-sm italic ${isYou ? "text-primary-foreground/60" : "text-muted-foreground/80"}`}>
                            {line.spanish}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Differences */}
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <ArrowRightLeft className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold">Swiss German vs German</h2>
          </div>
          <div className="space-y-4">
            {dialogue.differences.map((diff, i) => (
              <Card key={i} className="card-swiss">
                <div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
                  <Badge className="w-fit">{diff.swissGerman}</Badge>
                  <span className="text-muted-foreground">→</span>
                  <Badge variant="outline" className="w-fit">{diff.german}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{diff.explanation}</p>
              </Card>
            ))}
          </div>
        </section>

        {/* Key Phrases */}
        <section>
          <div className="flex items-center gap-2 mb-4">
            <Key className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold">Key Phrases</h2>
          </div>
          <Card className="card-swiss">
            <div className="space-y-3">
              {dialogue.keyPhrases.map((kp, i) => (
                <div
                  key={i}
                  className="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 py-2 border-b border-border last:border-0"
                >
                  <span className="font-bold text-primary">{kp.swissGerman}</span>
                  <span className="text-muted-foreground">{kp.german}</span>
                  <span className="text-muted-foreground italic">{kp.english}</span>
                </div>
              ))}
            </div>
          </Card>
        </section>
      </div>
    </div>
  );
};

export default SubtopicPage;
