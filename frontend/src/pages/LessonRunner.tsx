import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, useNavigate, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { learningApi, audioApi, type LessonData, type AttemptData, type SubmitResult } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Progress } from "@/components/ui/progress";
import TurnAudioButton from "@/components/TurnAudioButton";
import { ArrowLeft, CheckCircle2, XCircle, Trophy, ArrowRight } from "lucide-react";

type Phase = "study" | "assess" | "result";

const LessonRunner = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [params] = useSearchParams();
  const enrollmentId = params.get("enrollment");
  const nodeId = params.get("node");
  const navigate = useNavigate();
  const { user, isLoading: authLoading } = useAuth();

  const [phase, setPhase] = useState<Phase>("study");
  const [attempt, setAttempt] = useState<AttemptData | null>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [idemKey] = useState(() => crypto.randomUUID());

  useEffect(() => {
    if (!authLoading && !user) navigate("/auth");
  }, [authLoading, user, navigate]);

  const { data: lesson, isLoading } = useQuery<LessonData>({
    queryKey: ["lesson", lessonId],
    queryFn: () => learningApi.lesson(lessonId!),
    enabled: !!lessonId && !!user,
  });

  const dialogue = lesson?.dialogues?.[0];

  const startAssessment = async () => {
    if (!lessonId) return;
    const att = await learningApi.createAttempt({
      mode: "path",
      lesson_id: lessonId,
      enrollment_id: enrollmentId,
      node_id: nodeId,
      dialect_id: "gsw-zh",
    });
    setAttempt(att);
    setPhase("assess");
  };

  const allAnswered = useMemo(
    () => attempt?.exercises.every((e) => answers[e.id]) ?? false,
    [attempt, answers]
  );

  const submit = async () => {
    if (!attempt) return;
    setSubmitting(true);
    try {
      const res = await learningApi.submitAttempt(
        attempt.id,
        {
          attempt_version: attempt.version,
          answers: attempt.exercises.map((e) => ({ exercise_id: e.id, choice_id: answers[e.id] })),
          acknowledged_steps: ["scene", "understand", "notice", "rehearse", "respond", "recall"],
        },
        idemKey
      );
      setResult(res);
      setPhase("result");
    } finally {
      setSubmitting(false);
    }
  };

  if (authLoading || isLoading || !lesson) {
    return <div className="container mx-auto px-4 py-12 max-w-2xl"><Skeleton className="h-96 w-full rounded-xl" /></div>;
  }

  return (
    <div className="min-h-screen py-10">
      <div className="container mx-auto px-4 max-w-2xl">
        <Link to="/learn">
          <Button variant="ghost" size="sm" className="mb-4 -ml-2">
            <ArrowLeft className="h-4 w-4 mr-1" /> Back to journey
          </Button>
        </Link>

        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">{lesson.title}</h1>
          <Badge variant="secondary">{lesson.estimated_duration_min} min</Badge>
        </div>

        {!lesson.dialect_verified && (
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2 mb-6">
            Dialect not yet reviewed · audio is AI-generated
          </p>
        )}

        {/* STUDY */}
        {phase === "study" && dialogue && (
          <div className="space-y-6">
            <Card className="card-swiss bg-muted/40">
              <p className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-1">Set the scene</p>
              <p>{dialogue.situation}</p>
            </Card>

            <div className="rounded-2xl border border-border bg-muted/30 p-4 space-y-3">
              {dialogue.turns.map((t) => (
                <div key={t.id} className="flex items-start gap-2">
                  <TurnAudioButton itemId={dialogue.id} revision={dialogue.revision} turnId={t.id} className="mt-1" />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-secondary uppercase">{t.speaker}</p>
                    <p className="font-semibold">{t.swiss_german}</p>
                    <p className="text-sm text-muted-foreground">{t.german}</p>
                    <p className="text-sm italic text-muted-foreground/80">{t.translation}</p>
                  </div>
                </div>
              ))}
            </div>

            <Button className="w-full btn-swiss" onClick={startAssessment}>
              I'm ready — start the check
            </Button>
          </div>
        )}

        {/* ASSESS */}
        {phase === "assess" && attempt && (
          <div className="space-y-6">
            <p className="text-sm text-muted-foreground">
              Answer all {attempt.exercises.length} questions. You need 80% to pass; retry freely.
            </p>
            {attempt.exercises.map((ex, idx) => (
              <Card key={ex.id} className="card-swiss">
                <p className="font-semibold mb-3">{idx + 1}. {ex.prompt}</p>
                <div className="space-y-2">
                  {ex.choices.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => setAnswers((a) => ({ ...a, [ex.id]: c.id }))}
                      className={`w-full text-left px-4 py-2 rounded-lg border transition-colors ${
                        answers[ex.id] === c.id
                          ? "border-primary bg-primary/10 text-primary font-medium"
                          : "border-border hover:bg-muted"
                      }`}
                    >
                      {c.text}
                    </button>
                  ))}
                </div>
              </Card>
            ))}
            <Button className="w-full btn-swiss" disabled={!allAnswered || submitting} onClick={submit}>
              {submitting ? "Checking…" : "Submit answers"}
            </Button>
          </div>
        )}

        {/* RESULT */}
        {phase === "result" && result && (
          <Card className="card-swiss text-center p-8 space-y-4">
            {result.passed ? (
              <Trophy className="h-14 w-14 text-primary mx-auto" />
            ) : (
              <XCircle className="h-14 w-14 text-muted-foreground mx-auto" />
            )}
            <h2 className="text-2xl font-bold">
              {result.passed ? "Lesson complete!" : "Almost there"}
            </h2>
            <div className="max-w-xs mx-auto">
              <Progress value={(result.score.correct / result.score.total) * 100} />
              <p className="text-sm text-muted-foreground mt-2">
                You scored {result.score.correct} / {result.score.total}
              </p>
            </div>
            {result.passed && result.awarded_xp > 0 && (
              <p className="text-primary font-semibold flex items-center justify-center gap-1">
                <CheckCircle2 className="h-4 w-4" /> +{result.awarded_xp} XP
              </p>
            )}
            <div className="flex gap-2 justify-center pt-2">
              {!result.passed && (
                <Button variant="outline" onClick={() => { setPhase("study"); setResult(null); setAnswers({}); }}>
                  Try again
                </Button>
              )}
              <Button className="btn-swiss" onClick={() => navigate("/learn")}>
                Back to journey <ArrowRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
};

export default LessonRunner;
