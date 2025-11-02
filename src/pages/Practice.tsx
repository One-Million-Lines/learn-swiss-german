import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Trophy, Target, Flame, Star } from "lucide-react";

const Practice = () => {
  const [score, setScore] = useState(0);
  const totalPhrases = 23;

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Practice & Progress
            </h1>
            <p className="text-xl text-muted-foreground">
              Test your knowledge and track your learning journey
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid md:grid-cols-4 gap-4 mb-12">
            <Card className="p-6 text-center">
              <div className="text-3xl mb-2">🎯</div>
              <div className="text-2xl font-bold text-primary mb-1">{totalPhrases}</div>
              <div className="text-sm text-muted-foreground">Phrases Learned</div>
            </Card>

            <Card className="p-6 text-center">
              <div className="text-3xl mb-2">🔥</div>
              <div className="text-2xl font-bold text-primary mb-1">7</div>
              <div className="text-sm text-muted-foreground">Day Streak</div>
            </Card>

            <Card className="p-6 text-center">
              <div className="text-3xl mb-2">⭐</div>
              <div className="text-2xl font-bold text-primary mb-1">85%</div>
              <div className="text-sm text-muted-foreground">Accuracy</div>
            </Card>

            <Card className="p-6 text-center">
              <div className="text-3xl mb-2">🏆</div>
              <div className="text-2xl font-bold text-primary mb-1">5</div>
              <div className="text-sm text-muted-foreground">Lessons Done</div>
            </Card>
          </div>

          {/* Progress Section */}
          <Card className="card-swiss mb-8">
            <h2 className="text-2xl font-bold mb-4">Your Progress</h2>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-semibold">Greetings</span>
                  <span className="text-muted-foreground">100%</span>
                </div>
                <Progress value={100} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-semibold">Food & Drink</span>
                  <span className="text-muted-foreground">75%</span>
                </div>
                <Progress value={75} className="h-2" />
              </div>
              
              <div>
                <div className="flex justify-between mb-2">
                  <span className="font-semibold">Daily Life</span>
                  <span className="text-muted-foreground">40%</span>
                </div>
                <Progress value={40} className="h-2" />
              </div>
            </div>
          </Card>

          {/* Quick Quiz */}
          <Card className="card-swiss">
            <div className="flex items-center gap-3 mb-6">
              <div className="bg-gradient-to-r from-primary to-secondary p-3 rounded-xl">
                <Trophy className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold">Daily Challenge</h2>
                <p className="text-muted-foreground">Test your knowledge with today's quiz</p>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div className="p-4 rounded-xl bg-muted/50">
                <p className="font-semibold mb-3">What does "Wie gaht's?" mean?</p>
                <div className="space-y-2">
                  <Button variant="outline" className="w-full justify-start">
                    A) Good morning
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    B) How are you?
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    C) Goodbye
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    D) Thank you
                  </Button>
                </div>
              </div>
            </div>

            <Button className="w-full gradient-hero" size="lg">
              Start Daily Challenge
            </Button>
          </Card>

          {/* Achievements */}
          <div className="mt-12">
            <h2 className="text-2xl font-bold mb-6">Achievements</h2>
            <div className="grid md:grid-cols-3 gap-4">
              <Card className="p-6 text-center opacity-50">
                <div className="text-4xl mb-3">🥉</div>
                <div className="font-bold mb-1">First Steps</div>
                <div className="text-sm text-muted-foreground">Learn 10 phrases</div>
              </Card>

              <Card className="p-6 text-center">
                <div className="text-4xl mb-3">🥈</div>
                <div className="font-bold mb-1">Getting Started</div>
                <div className="text-sm text-muted-foreground">Learn 25 phrases</div>
              </Card>

              <Card className="p-6 text-center opacity-50">
                <div className="text-4xl mb-3">🥇</div>
                <div className="font-bold mb-1">Swiss Speaker</div>
                <div className="text-sm text-muted-foreground">Learn 50 phrases</div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Practice;
