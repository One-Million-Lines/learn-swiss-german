import { Button } from "@/components/ui/button";
import { ArrowRight, Play } from "lucide-react";
import { Link } from "react-router-dom";
import PhraseCard from "@/components/PhraseCard";
import heroImage from "@/assets/hero-mountains.jpg";

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 z-0"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/50 to-background" />
        </div>
        
        <div className="container relative z-10 mx-auto px-4 pt-20 pb-32 md:pt-32 md:pb-40">
          <div className="max-w-3xl">
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight">
              Grüezi! 🇨🇭
            </h1>
            <p className="text-xl md:text-2xl text-white/90 mb-8 leading-relaxed">
              Learn Swiss German through real conversations and cultural connections. 
              Start speaking like a local today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/learn">
                <Button size="lg" className="gradient-hero w-full sm:w-auto group">
                  Start Learning
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              <Link to="/resources">
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="w-full sm:w-auto bg-white/10 backdrop-blur-sm text-white border-white/20 hover:bg-white/20"
                >
                  <Play className="mr-2 h-5 w-5" />
                  Watch Real Speakers
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Daily Phrase Section */}
      <section className="py-16 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <span className="text-4xl">☀️</span>
              <h2 className="text-3xl font-bold">Today's Phrase</h2>
            </div>
            
            <PhraseCard
              swissGerman="Wie gaht's dir?"
              german="Wie geht es dir?"
              english="How are you?"
              topic="Greetings"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Why SwissSpeak?
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card-swiss text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-bold mb-3">Contrastive Learning</h3>
              <p className="text-muted-foreground">
                Compare German and Swiss German side-by-side to understand the differences naturally
              </p>
            </div>
            
            <div className="card-swiss text-center">
              <div className="text-4xl mb-4">🎵</div>
              <h3 className="text-xl font-bold mb-3">Real Speakers</h3>
              <p className="text-muted-foreground">
                Learn from authentic content creators who speak Swiss German daily
              </p>
            </div>
            
            <div className="card-swiss text-center">
              <div className="text-4xl mb-4">🏔️</div>
              <h3 className="text-xl font-bold mb-3">Cultural Context</h3>
              <p className="text-muted-foreground">
                Immerse yourself in Swiss culture while learning the language
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-primary to-secondary text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to speak Swiss German?
          </h2>
          <p className="text-xl mb-8 text-white/90 max-w-2xl mx-auto">
            Join learners who are discovering Swiss culture through language
          </p>
          <Link to="/learn">
            <Button 
              size="lg" 
              variant="outline"
              className="bg-white text-primary hover:bg-white/90 border-0"
            >
              Get Started Free
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
