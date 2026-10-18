import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/contexts/AuthContext";
import { learningApi, type EnrollmentPath, type PathNode } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Lock, CheckCircle2, Flag, Play, List, Map, Mountain, AlertTriangle } from "lucide-react";

const CURRICULUM = "mountain_journey";
const DIALECT = "gsw-zh";

const Learn = () => {
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [listView, setListView] = useState(false);
  const [enrollmentId, setEnrollmentId] = useState<string | null>(null);

  // Ensure an enrollment exists for this dialect, then load the path.
  useEffect(() => {
    if (!user) return;
    (async () => {
      const existing = await learningApi.enrollments();
      const match = existing.find((e) => e.curriculum_key === CURRICULUM && e.dialect_id === DIALECT);
      if (match) {
        setEnrollmentId(match.id);
      } else {
        const created = await learningApi.enroll(CURRICULUM, DIALECT);
        setEnrollmentId(created.id);
      }
    })();
  }, [user]);

  const { data: path, isLoading } = useQuery<EnrollmentPath>({
    queryKey: ["path", enrollmentId],
    queryFn: () => learningApi.path(enrollmentId!),
    enabled: !!enrollmentId,
  });

  const stages = useMemo(() => {
    if (!path) return [];
    return path.stages.map((s) => ({
      ...s,
      nodes: path.nodes.filter((n) => n.stage_id === s.id),
    }));
  }, [path]);

  if (authLoading) {
    return <div className="container mx-auto px-4 py-12"><Skeleton className="h-64 w-full rounded-xl" /></div>;
  }

  if (!user) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center px-4">
        <Card className="card-swiss max-w-md text-center p-8">
          <Mountain className="h-12 w-12 text-primary mx-auto mb-4" />
          <h1 className="text-2xl font-bold mb-2">Your alpine journey</h1>
          <p className="text-muted-foreground mb-6">
            Sign in to start the mountain journey, save your progress and sync across devices.
          </p>
          <Button className="btn-swiss" onClick={() => navigate("/auth")}>Sign in to start</Button>
        </Card>
      </div>
    );
  }

  const openNode = (node: PathNode) => {
    if (node.state === "locked" || node.state === "coming_soon") return;
    navigate(`/learn/lessons/${node.lesson_ref.item_id}?enrollment=${enrollmentId}&node=${node.id}`);
    queryClient.invalidateQueries({ queryKey: ["path", enrollmentId] });
  };

  return (
    <div className="min-h-screen py-10">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Mountain className="h-7 w-7 text-primary" /> Your alpine journey
          </h1>
          <Button variant="outline" size="sm" onClick={() => setListView((v) => !v)}>
            {listView ? <Map className="h-4 w-4 mr-1" /> : <List className="h-4 w-4 mr-1" />}
            {listView ? "Map view" : "List view"}
          </Button>
        </div>

        {path?.provenance?.source?.includes("unverified") && (
          <div className="flex items-start gap-2 rounded-lg border border-amber-300 bg-amber-50 text-amber-900 px-4 py-3 mb-6 text-sm">
            <AlertTriangle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span>
              Preview journey built from legacy content. The Swiss German here is <strong>not yet dialect-reviewed</strong>,
              and audio is AI-generated. It is great for practising the learning flow while verified Zürichdeutsch lessons are prepared.
            </span>
          </div>
        )}

        {isLoading && <Skeleton className="h-96 w-full rounded-xl" />}

        {path && (
          <div className="space-y-10">
            {stages.map((stage, si) => (
              <section key={stage.id}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="flex items-center justify-center h-7 w-7 rounded-full bg-secondary text-secondary-foreground text-sm font-bold">
                    {si}
                  </span>
                  <h2 className="text-xl font-bold">{stage.name}</h2>
                </div>
                <p className="text-sm text-muted-foreground mb-4 ml-9">{stage.outcomes.join(" · ")}</p>

                <div className={listView ? "space-y-2 ml-9" : "relative ml-9 flex flex-wrap gap-4 items-center"}>
                  {stage.nodes.map((node) => (
                    <NodeButton key={node.id} node={node} listView={listView} onOpen={() => openNode(node)} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const NodeButton = ({ node, listView, onOpen }: { node: PathNode; listView: boolean; onOpen: () => void }) => {
  const isCheckpoint = node.kind === "checkpoint";
  const locked = node.state === "locked" || node.state === "coming_soon";
  const completed = node.state === "completed";

  const icon = completed ? <CheckCircle2 className="h-5 w-5" /> : locked ? <Lock className="h-4 w-4" /> : isCheckpoint ? <Flag className="h-5 w-5" /> : <Play className="h-4 w-4" />;

  const base = isCheckpoint
    ? "bg-gradient-to-br from-primary to-secondary text-white"
    : completed
    ? "bg-primary text-primary-foreground"
    : locked
    ? "bg-muted text-muted-foreground cursor-not-allowed"
    : "bg-card border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground";

  if (listView) {
    return (
      <button
        onClick={onOpen}
        disabled={locked}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-colors ${
          locked ? "bg-muted/50 cursor-not-allowed" : "hover:bg-muted"
        }`}
      >
        <span className={`flex items-center justify-center h-8 w-8 rounded-full ${base}`}>{icon}</span>
        <div className="flex-1 min-w-0">
          <p className="font-medium truncate">{node.title}</p>
          <p className="text-xs text-muted-foreground">{node.reason}</p>
        </div>
        {isCheckpoint && <Badge variant="secondary">Summit</Badge>}
        {node.review_due && <Badge className="bg-amber-500">Review due</Badge>}
      </button>
    );
  }

  return (
    <div className="flex flex-col items-center gap-1" style={{ marginTop: (node.layout?.y % 2) * 10 }}>
      <button
        onClick={onOpen}
        disabled={locked}
        title={node.reason}
        aria-label={`${node.title} — ${node.state}`}
        className={`flex items-center justify-center rounded-full shadow transition-all ${base} ${
          isCheckpoint ? "h-16 w-16" : "h-14 w-14"
        }`}
      >
        {icon}
      </button>
      <span className="text-[11px] text-center max-w-[6rem] leading-tight text-muted-foreground truncate">{node.title}</span>
    </div>
  );
};

export default Learn;
