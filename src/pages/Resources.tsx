import CreatorCard from "@/components/CreatorCard";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Plus } from "lucide-react";

const Resources = () => {
  const creators = [
    {
      name: "Swiss German 101",
      platform: "YouTube" as const,
      description: "Daily Swiss German lessons with Zürich dialect focus",
      thumbnail: "",
      link: "https://youtube.com",
      dialect: "Zürich"
    },
    {
      name: "Schwiizerdütsch Daily",
      platform: "TikTok" as const,
      description: "Quick Swiss German tips and funny cultural moments",
      thumbnail: "",
      link: "https://tiktok.com",
      dialect: "Bern"
    },
    {
      name: "Learn Swiss German",
      platform: "YouTube" as const,
      description: "Comprehensive lessons from a native Basel speaker",
      thumbnail: "",
      link: "https://youtube.com",
      dialect: "Basel"
    },
    {
      name: "Swiss Life Stories",
      platform: "Facebook" as const,
      description: "Real conversations and cultural insights in Swiss German",
      thumbnail: "",
      link: "https://facebook.com",
      dialect: "Zürich"
    },
    {
      name: "Grüezi From Switzerland",
      platform: "YouTube" as const,
      description: "Swiss culture and language through travel vlogs",
      thumbnail: "",
      link: "https://youtube.com",
      dialect: "Various"
    },
    {
      name: "SwissGerman Tips",
      platform: "TikTok" as const,
      description: "30-second daily phrases and pronunciation guides",
      thumbnail: "",
      link: "https://tiktok.com",
      dialect: "Zürich"
    }
  ];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-6xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Learn from Real People
            </h1>
            <p className="text-xl text-muted-foreground mb-6">
              Discover authentic Swiss German content from native speakers and cultural creators
            </p>
            
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm">All Dialects</Button>
              <Button variant="outline" size="sm">🏔️ Zürich</Button>
              <Button variant="outline" size="sm">🐻 Bern</Button>
              <Button variant="outline" size="sm">🦁 Basel</Button>
              <Button variant="outline" size="sm">📺 YouTube</Button>
              <Button variant="outline" size="sm">🎵 TikTok</Button>
              <Button variant="outline" size="sm">👥 Facebook</Button>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {creators.map((creator, index) => (
              <CreatorCard key={index} {...creator} />
            ))}
          </div>

          <Card className="card-swiss text-center">
            <div className="max-w-2xl mx-auto">
              <h3 className="text-2xl font-bold mb-4">Know a great creator?</h3>
              <p className="text-muted-foreground mb-6">
                Help us grow our community by suggesting Swiss German content creators
              </p>
              <Button className="gradient-hero">
                <Plus className="mr-2 h-5 w-5" />
                Suggest a Creator
              </Button>
            </div>
          </Card>

          <div className="mt-12 p-6 rounded-2xl bg-gradient-to-r from-secondary/10 to-accent/10 border border-secondary/20">
            <h3 className="font-bold mb-2">💡 Pro Tip</h3>
            <p className="text-muted-foreground">
              Watch creators from different regions to understand dialect variations. 
              Zürich Swiss German differs from Bern or Basel, but they're all mutually intelligible!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Resources;
