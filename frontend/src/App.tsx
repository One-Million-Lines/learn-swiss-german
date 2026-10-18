import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useParams, Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { AuthProvider } from "./contexts/AuthContext";
import { ProgressProvider } from "./contexts/ProgressContext";
import Navigation from "./components/Navigation";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import Topics from "./pages/Topics";
import TopicDetail from "./pages/TopicDetail";
import SubtopicPage from "./pages/Conversation";
import Patterns from "./pages/Patterns";
import Vocabulary from "./pages/Vocabulary";
import Auth from "./pages/Auth";
import Learn from "./pages/Learn";
import LessonRunner from "./pages/LessonRunner";
import NotFound from "./pages/NotFound";
import { api } from "./lib/api";

const queryClient = new QueryClient();

/**
 * Legacy `/conversations/:conversationId` links resolve a dialogue by its legacy
 * id and redirect to the canonical subtopic route.
 */
const ConversationRedirect = () => {
  const { conversationId } = useParams<{ conversationId: string }>();
  const [target, setTarget] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (!conversationId) return;
    api
      .getDialogue(conversationId)
      .then(() => {
        const sub = conversationId.replace(/-\d+$/, "");
        setTarget(`/subtopics/${sub}`);
      })
      .catch(() => setFailed(true));
  }, [conversationId]);

  if (failed) return <Navigate to="/topics" replace />;
  if (!target) return null;
  return <Navigate to={target} replace />;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <AuthProvider>
        <ProgressProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter basename={import.meta.env.BASE_URL}>
            <div className="flex flex-col min-h-screen">
              <Navigation />
              <main className="flex-1">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/topics" element={<Topics />} />
                  <Route path="/topics/:topicId" element={<TopicDetail />} />
                  <Route path="/conversations/:conversationId" element={<ConversationRedirect />} />
                  <Route path="/subtopics/:subtopicId" element={<SubtopicPage />} />
                  <Route path="/dialogues/:subtopicId" element={<SubtopicPage />} />
                  <Route path="/patterns" element={<Patterns />} />
                  <Route path="/vocabulary" element={<Vocabulary />} />
                  <Route path="/learn" element={<Learn />} />
                  <Route path="/learn/lessons/:lessonId" element={<LessonRunner />} />
                  <Route path="/auth" element={<Auth />} />
                  <Route path="/auth/callback" element={<Auth />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </main>
              <Footer />
            </div>
          </BrowserRouter>
        </ProgressProvider>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
