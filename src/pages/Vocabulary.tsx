import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

const Vocabulary = () => {
  const { data: vocabData, isLoading: vocabLoading } = useQuery({
    queryKey: ["vocabulary"],
    queryFn: () => api.getVocabulary(),
  });

  const { data: topicsData } = useQuery({
    queryKey: ["topics"],
    queryFn: api.getTopics,
  });

  const vocab = vocabData?.vocabulary ?? [];
  const topics = topicsData?.topics ?? [];

  const topicName = (topicId: string) =>
    topics.find((t) => t.id === topicId)?.title ?? topicId;

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold mb-2">Vocabulary</h1>
        <p className="text-muted-foreground mb-8">
          Essential Swiss German words grouped by topic.
        </p>

        {vocabLoading ? (
          <div className="grid md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-48 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6">
            {vocab.map((group) => (
              <Card key={group.id} className="card-swiss">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">{group.title}</h2>
                  <Badge variant="secondary">{topicName(group.topicId)}</Badge>
                </div>
                <div className="space-y-2">
                  {group.words.map((w, i) => (
                    <div
                      key={i}
                      className="grid grid-cols-3 gap-2 text-sm py-1.5 border-b border-border last:border-0"
                    >
                      <span className="font-semibold text-primary">{w.swissGerman}</span>
                      <span className="text-muted-foreground">{w.german}</span>
                      <span className="text-muted-foreground italic">{w.english}</span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Vocabulary;
