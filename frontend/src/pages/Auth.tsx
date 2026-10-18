import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { Mail, CheckCircle2, Loader2 } from "lucide-react";

const Auth = () => {
  const { requestMagicLink, consumeToken, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();

  const isCallback = location.pathname.endsWith("/callback");
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [callbackState, setCallbackState] = useState<"idle" | "ready" | "working" | "error">("idle");
  const [token, setToken] = useState<string | null>(null);

  // On the callback page, read the token from the URL fragment and remove it
  // from history immediately (avoids referrer/log leakage).
  useEffect(() => {
    if (!isCallback) return;
    const hash = window.location.hash;
    const match = hash.match(/token=([^&]+)/);
    if (match) {
      setToken(decodeURIComponent(match[1]));
      setCallbackState("ready");
      window.history.replaceState(null, "", window.location.pathname + window.location.search);
    } else {
      setCallbackState("error");
    }
  }, [isCallback]);

  useEffect(() => {
    if (user && !isCallback) navigate("/learn");
  }, [user, isCallback, navigate]);

  const handleRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await requestMagicLink(email);
      setSent(true);
    } catch {
      toast({ title: "Something went wrong", description: "Please try again.", variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleConsume = async () => {
    if (!token) return;
    setCallbackState("working");
    try {
      await consumeToken(token);
      toast({ title: "Signed in", description: "Welcome to SwissSpeak!" });
      navigate("/learn");
    } catch {
      setCallbackState("error");
      toast({ title: "Link invalid or expired", description: "Please request a new sign-in link.", variant: "destructive" });
    }
  };

  if (isCallback) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-subtle">
        <Card className="w-full max-w-md card-swiss text-center">
          <CardHeader>
            <CardTitle className="text-2xl font-bold text-primary">Complete sign-in</CardTitle>
            <CardDescription>
              For your security, finishing sign-in requires one click.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {callbackState === "ready" && (
              <Button className="w-full btn-swiss" onClick={handleConsume}>
                Continue to SwissSpeak
              </Button>
            )}
            {callbackState === "working" && (
              <div className="flex items-center justify-center gap-2 text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin" /> Signing you in…
              </div>
            )}
            {callbackState === "error" && (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">This link is no longer valid.</p>
                <Button variant="outline" className="w-full" onClick={() => navigate("/auth")}>
                  Request a new link
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-subtle">
      <Card className="w-full max-w-md card-swiss">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-primary">Sign in to SwissSpeak</CardTitle>
          <CardDescription>
            No password needed. We'll email you a secure sign-in link.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sent ? (
            <div className="text-center space-y-3 py-4">
              <CheckCircle2 className="h-12 w-12 text-primary mx-auto" />
              <p className="font-semibold">Check your email</p>
              <p className="text-sm text-muted-foreground">
                If an account can be created for <strong>{email}</strong>, a sign-in link is on its way.
                Open it on this device to continue.
              </p>
              <Button variant="ghost" size="sm" onClick={() => setSent(false)}>
                Use a different email
              </Button>
            </div>
          ) : (
            <form onSubmit={handleRequest} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="your@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <Button type="submit" className="w-full btn-swiss" disabled={submitting}>
                {submitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Mail className="h-4 w-4 mr-2" />}
                Send sign-in link
              </Button>
              <p className="text-xs text-muted-foreground text-center">
                Free to learn. We never post anything or share your email.
              </p>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Auth;
