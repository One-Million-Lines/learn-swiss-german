import { ExternalLink } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface CreatorCardProps {
  name: string;
  platform: "YouTube" | "TikTok" | "Facebook";
  description: string;
  thumbnail: string;
  link: string;
  dialect?: string;
}

const CreatorCard = ({ name, platform, description, thumbnail, link, dialect }: CreatorCardProps) => {
  const getPlatformEmoji = () => {
    switch (platform) {
      case "YouTube": return "📺";
      case "TikTok": return "🎵";
      case "Facebook": return "👥";
    }
  };

  return (
    <Card className="card-swiss overflow-hidden group">
      <div className="aspect-video bg-muted relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
        <div className="absolute top-3 left-3 bg-card px-2 py-1 rounded-lg text-xs font-semibold">
          {getPlatformEmoji()} {platform}
        </div>
        {dialect && (
          <div className="absolute top-3 right-3 bg-primary text-primary-foreground px-2 py-1 rounded-lg text-xs font-semibold">
            {dialect}
          </div>
        )}
        <div className="absolute inset-0 flex items-center justify-center text-6xl">
          {getPlatformEmoji()}
        </div>
      </div>
      
      <div className="p-4 space-y-3">
        <h3 className="font-bold text-lg">{name}</h3>
        <p className="text-sm text-muted-foreground line-clamp-2">{description}</p>
        
        <Button
          asChild
          variant="outline"
          className="w-full hover:bg-primary hover:text-primary-foreground"
        >
          <a href={link} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center gap-2">
            Watch Content
            <ExternalLink className="h-4 w-4" />
          </a>
        </Button>
      </div>
    </Card>
  );
};

export default CreatorCard;
