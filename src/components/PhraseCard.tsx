import { Volume2, Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useState } from "react";

interface PhraseCardProps {
  swissGerman: string;
  german: string;
  english: string;
  topic?: string;
}

const PhraseCard = ({ swissGerman, german, english, topic }: PhraseCardProps) => {
  const [isFavorite, setIsFavorite] = useState(false);

  const handlePlay = () => {
    // Audio playback would be implemented here
    console.log("Playing audio for:", swissGerman);
  };

  return (
    <Card className="card-swiss">
      {topic && (
        <span className="inline-block mb-3 text-xs font-semibold text-muted-foreground uppercase tracking-wide">
          {topic}
        </span>
      )}
      
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="text-2xl font-bold text-primary mb-2">
              {swissGerman}
            </div>
            <div className="text-lg text-foreground mb-1">
              🇩🇪 {german}
            </div>
            <div className="text-base text-muted-foreground">
              🇬🇧 {english}
            </div>
          </div>
          
          <div className="flex flex-col gap-2">
            <Button
              size="icon"
              variant="outline"
              onClick={handlePlay}
              className="rounded-full hover:bg-primary hover:text-primary-foreground"
            >
              <Volume2 className="h-4 w-4" />
            </Button>
            <Button
              size="icon"
              variant="outline"
              onClick={() => setIsFavorite(!isFavorite)}
              className={`rounded-full ${
                isFavorite
                  ? "bg-primary text-primary-foreground hover:bg-primary/90"
                  : "hover:bg-primary hover:text-primary-foreground"
              }`}
            >
              <Heart className={`h-4 w-4 ${isFavorite ? "fill-current" : ""}`} />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default PhraseCard;
