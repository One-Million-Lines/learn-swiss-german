import { useRef, useState } from "react";
import { Volume2, Loader2, AlertCircle } from "lucide-react";
import { audioApi } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";

interface Props {
  itemId?: string;
  revision?: number;
  turnId?: string;
  className?: string;
}

/**
 * Plays per-turn Swiss German audio. Audio is generated lazily by the server on
 * first request (requires sign-in), then cached and reused. All audio is
 * AI-generated and labelled as such; it is never required to finish a lesson.
 */
const TurnAudioButton = ({ itemId, revision, turnId, className = "" }: Props) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [state, setState] = useState<"idle" | "loading" | "playing" | "error">("idle");
  const audioRef = useRef<HTMLAudioElement | null>(null);

  if (!itemId || revision === undefined || !turnId) return null;

  const play = async () => {
    if (state === "loading") return;
    if (!user) {
      toast({ title: "Sign in to hear audio", description: "Audio is generated after you sign in." });
      return;
    }
    setState("loading");
    try {
      let result = await audioApi.request(itemId, revision, turnId);
      let tries = 0;
      while (result.status !== "ready" && result.request_id && tries < 25) {
        await new Promise((r) => setTimeout(r, (result.poll_after_seconds || 2) * 1000));
        result = await audioApi.status(result.request_id);
        tries += 1;
        if (result.status === "failed") break;
      }
      if (result.status !== "ready" || !result.stream_url) {
        setState("error");
        toast({ title: "Audio unavailable", description: "Text learning is unaffected.", variant: "destructive" });
        return;
      }
      const audio = new Audio(audioApi.streamUrl(result.stream_url));
      audioRef.current = audio;
      audio.onended = () => setState("idle");
      audio.onerror = () => setState("error");
      setState("playing");
      await audio.play();
    } catch {
      setState("error");
      toast({ title: "Audio unavailable", description: "Please try again later.", variant: "destructive" });
    }
  };

  return (
    <button
      type="button"
      onClick={play}
      aria-label="Play Swiss German audio (AI-generated)"
      title="AI-generated audio"
      className={`inline-flex items-center justify-center h-8 w-8 min-w-[2rem] rounded-full border border-border hover:bg-muted transition-colors ${className}`}
    >
      {state === "loading" && <Loader2 className="h-4 w-4 animate-spin" />}
      {state === "error" && <AlertCircle className="h-4 w-4 text-destructive" />}
      {(state === "idle" || state === "playing") && (
        <Volume2 className={`h-4 w-4 ${state === "playing" ? "text-primary" : ""}`} />
      )}
    </button>
  );
};

export default TurnAudioButton;
