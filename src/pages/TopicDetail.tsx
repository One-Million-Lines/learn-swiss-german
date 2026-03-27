import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, MessageSquare, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

const TopicDetail = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["topic", topicId],
    queryFn: () => api.getTopic(topicId!),
    enabled: !!topicId,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen py-12 container mx-auto px-4">
        <Skeleton className="h-8 w-48 mb-4" />
        <Skeleton className="h-6 w-96 mb-8" />
        <div className="grid md:grid-cols-2 gap-6">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <Link to="/topics">
          <Button variant="ghost" size="sm" className="mb-4 -ml-2">
            <ArrowLeft className="h-4 w-4 mr-1" /> All Topics
          </Button>
        </Link>

        <div className={`h-2 rounded-xl bg-gradient-to-r ${data.color} w-24 mb-4`} />
        <h1 className="text-4xl font-bold mb-2">{data.title}</h1>
        <p className="text-muted-foreground mb-10">{data.description}</p>

        {/* Subtopics */}
        <section className="mb-12">
          <div className="flex items-center gap-2 mb-6">
            <MessageSquare className="h-5 w-5 text-primary" />
            <h2 className="text-2xl font-bold">Subtopics</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {data.subtopics.map((sub) => (
              <Link key={sub.id} to={`/subtopics/${sub.id}`}>
                <Card className="card-swiss group cursor-pointer hover:shadow-lg transition-all h-full">
                  <h3 className="text-lg font-bold mb-2 group-hover:text-primary transition-colors">
                    {sub.title}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-3">{sub.description}</p>
                  <Badge variant="secondary">
                    {sub.dialogues.length} {sub.dialogues.length === 1 ? "dialogue" : "dialogues"}
                  </Badge>
                </Card>
              </Link>
            ))}
          </div>
        </section>

        {/* Vocabulary */}
        {data.vocabulary.length > 0 && (
          <section>
            <div className="flex items-center gap-2 mb-6">
              <BookOpen className="h-5 w-5 text-primary" />
              <h2 className="text-2xl font-bold">Vocabulary</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              {data.vocabulary.map((group) => (
                <Card key={group.id} className="card-swiss">
                  <h3 className="text-lg font-bold mb-4">{group.title}</h3>
                  <div className="space-y-2">
                    {group.words.map((w, i) => (
                      <div key={i} className="grid grid-cols-3 gap-2 text-sm py-1 border-b border-border last:border-0">
                        <span className="font-semibold text-primary">{w.swissGerman}</span>
                        <span className="text-muted-foreground">{w.german}</span>
                        <span className="text-muted-foreground italic">{w.english}</span>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default TopicDetail;
