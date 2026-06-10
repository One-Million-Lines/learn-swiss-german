import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

const Topics = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["topics"],
    queryFn: api.getTopics,
  });

  const topics = data?.topics ?? [];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-4xl font-bold mb-2">Topics</h1>
        <p className="text-muted-foreground mb-8">
          Choose a topic to explore real Swiss German conversations.
        </p>

        {isLoading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-44 rounded-xl" />
            ))}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {topics.map((topic) => (
              <Link key={topic.id} to={`/topics/${topic.id}`}>
                <Card className="card-swiss group cursor-pointer hover:shadow-lg transition-all h-full">
                  <div
                    className={`h-2 rounded-t-xl bg-gradient-to-r ${topic.color} -mx-6 -mt-6 mb-4`}
                  />
                  <h2 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors">
                    {topic.title}
                  </h2>
                  <p className="text-sm text-muted-foreground mb-4">{topic.description}</p>
                  <Badge variant="outline">{topic.subtopicCount} subtopics</Badge>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Topics;
