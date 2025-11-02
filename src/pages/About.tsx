import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Heart } from "lucide-react";

const About = () => {
  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              About SwissSpeak
            </h1>
            <p className="text-xl text-muted-foreground">
              Your bridge to Swiss culture through language
            </p>
          </div>

          <Card className="card-swiss mb-8">
            <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              SwissSpeak was created to help German speakers and learners connect with Swiss culture 
              through its unique language. We believe that learning Swiss German opens doors to 
              understanding Swiss life, traditions, and people on a deeper level.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              Unlike traditional language learning apps, we focus on contrastive learning—showing you 
              how Swiss German relates to Standard German, making it easier to understand the patterns 
              and speak naturally.
            </p>
          </Card>

          <Card className="card-swiss mb-8">
            <h2 className="text-2xl font-bold mb-4">How It Works</h2>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">
                  1
                </div>
                <div>
                  <h3 className="font-bold mb-2">Compare Side-by-Side</h3>
                  <p className="text-muted-foreground">
                    See Standard German and Swiss German together with English translations
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-secondary text-secondary-foreground flex items-center justify-center font-bold">
                  2
                </div>
                <div>
                  <h3 className="font-bold mb-2">Listen & Practice</h3>
                  <p className="text-muted-foreground">
                    Hear authentic pronunciation and practice with interactive exercises
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-accent text-accent-foreground flex items-center justify-center font-bold">
                  3
                </div>
                <div>
                  <h3 className="font-bold mb-2">Learn from Real People</h3>
                  <p className="text-muted-foreground">
                    Watch curated content from native Swiss German speakers
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <Card className="card-swiss mb-8">
            <h2 className="text-2xl font-bold mb-4">Why Swiss German?</h2>
            <p className="text-muted-foreground leading-relaxed mb-4">
              Swiss German (Schweizerdeutsch) isn't just a dialect—it's a family of Alemannic dialects 
              spoken by over 5 million people in Switzerland. Each region has its own variation, from 
              Zürich to Bern to Basel.
            </p>
            <p className="text-muted-foreground leading-relaxed">
              While Standard German is used in formal settings, Swiss German is the language of daily 
              life, friendship, and culture. Learning it helps you truly connect with Swiss people and 
              understand their unique identity.
            </p>
          </Card>

          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🇨🇭</div>
              <h3 className="font-bold mb-2">Culturally Authentic</h3>
              <p className="text-sm text-muted-foreground">
                Content curated by Swiss natives and culture experts
              </p>
            </Card>

            <Card className="p-6 text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="font-bold mb-2">Focused Learning</h3>
              <p className="text-sm text-muted-foreground">
                Lessons designed for German speakers learning Swiss German
              </p>
            </Card>
          </div>

          <div className="bg-gradient-to-r from-primary to-secondary text-white rounded-2xl p-8 text-center">
            <Heart className="h-12 w-12 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-4">
              Ready to Start Your Journey?
            </h2>
            <p className="text-white/90 mb-6 max-w-2xl mx-auto">
              Join our community of learners discovering Swiss German and culture
            </p>
            <Link to="/learn">
              <Button 
                size="lg" 
                variant="outline"
                className="bg-white text-primary hover:bg-white/90 border-0"
              >
                Begin Learning
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
