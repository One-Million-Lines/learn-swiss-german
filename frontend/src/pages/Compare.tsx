import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Volume2, RefreshCw } from "lucide-react";

const Compare = () => {
  const [germanText, setGermanText] = useState("");
  const [swissGermanText, setSwissGermanText] = useState("");
  const [hasConverted, setHasConverted] = useState(false);

  const handleConvert = () => {
    // Simple transformation rules (in production, this would use a proper API)
    const converted = germanText
      .replace(/geht/g, "gaht")
      .replace(/geh/g, "gang")
      .replace(/Guten/g, "Guete")
      .replace(/nicht/g, "nöd")
      .replace(/ein/g, "en")
      .replace(/eine/g, "e")
      .replace(/ch/g, "ch"); // Swiss pronunciation hint
    
    setSwissGermanText(converted || "Enter German text to convert");
    setHasConverted(true);
  };

  const handleReset = () => {
    setGermanText("");
    setSwissGermanText("");
    setHasConverted(false);
  };

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Compare & Transform
            </h1>
            <p className="text-xl text-muted-foreground">
              Enter a German sentence and see how it transforms into Swiss German. 
              Differences are highlighted to help you learn the patterns.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold">🇩🇪 Standard German</h3>
              </div>
              <Textarea
                value={germanText}
                onChange={(e) => setGermanText(e.target.value)}
                placeholder="Wie geht es dir heute?"
                className="min-h-[200px] text-lg resize-none"
              />
            </Card>

            <Card className="p-6 bg-muted/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-primary">🇨🇭 Swiss German</h3>
                {hasConverted && (
                  <Button size="icon" variant="outline" className="rounded-full">
                    <Volume2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
              <div className="min-h-[200px] text-lg p-3 rounded-md bg-card">
                {swissGermanText || "Translation will appear here..."}
              </div>
            </Card>
          </div>

          <div className="flex gap-4 justify-center">
            <Button 
              onClick={handleConvert}
              disabled={!germanText}
              size="lg"
              className="gradient-hero"
            >
              <RefreshCw className="mr-2 h-5 w-5" />
              Convert to Swiss German
            </Button>
            {hasConverted && (
              <Button 
                onClick={handleReset}
                variant="outline"
                size="lg"
              >
                Reset
              </Button>
            )}
          </div>

          <div className="mt-12 card-swiss">
            <h3 className="text-xl font-bold mb-4">💡 Common Patterns</h3>
            <div className="space-y-3 text-muted-foreground">
              <div className="flex items-start gap-3">
                <span className="text-primary font-bold">•</span>
                <p><strong>geht → gaht</strong>: The "e" often becomes "a" in verbs</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-primary font-bold">•</span>
                <p><strong>nicht → nöd</strong>: Negation uses different words</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-primary font-bold">•</span>
                <p><strong>ein/eine → en/e</strong>: Articles are shortened</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-primary font-bold">•</span>
                <p><strong>ch sound</strong>: The "ch" is pronounced more strongly from the throat</p>
              </div>
            </div>
          </div>

          <div className="mt-8 p-6 rounded-2xl bg-gradient-to-r from-secondary/10 to-accent/10 border border-secondary/20">
            <p className="text-center text-sm text-muted-foreground">
              <strong>Note:</strong> Swiss German varies by region (Zürich, Bern, Basel, etc.). 
              This tool uses general patterns. For authentic pronunciation, listen to native speakers in our Resources section.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Compare;
