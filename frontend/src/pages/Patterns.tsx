import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { api } from "@/lib/api";

const Patterns = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["patterns"],
    queryFn: api.getPatterns,
  });

  const patterns = data?.patterns ?? [];

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        <h1 className="text-4xl font-bold mb-2">Patterns</h1>
        <p className="text-muted-foreground mb-8">
          Recurring structures that make Swiss German unique. Learn these and you'll recognise them everywhere.
        </p>

        {isLoading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 rounded-xl" />
            ))}
          </div>
        ) : (
          <Accordion type="multiple" className="space-y-4">
            {patterns.map((pattern) => (
              <AccordionItem key={pattern.id} value={pattern.id} className="border rounded-xl px-6">
                <AccordionTrigger className="hover:no-underline">
                  <div className="text-left">
                    <h3 className="text-lg font-bold">{pattern.title}</h3>
                    <p className="text-sm text-muted-foreground font-normal">{pattern.description}</p>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-3 pt-2">
                    {pattern.examples.map((ex, i) => (
                      <div
                        key={i}
                        className="grid grid-cols-1 sm:grid-cols-3 gap-1 sm:gap-4 py-2 border-b border-border last:border-0"
                      >
                        <div>
                          <Badge variant="outline" className="text-xs mb-1">German</Badge>
                          <p>{ex.german}</p>
                        </div>
                        <div>
                          <Badge className="text-xs mb-1">Swiss German</Badge>
                          <p className="font-semibold text-primary">{ex.swissGerman}</p>
                        </div>
                        <div>
                          <Badge variant="secondary" className="text-xs mb-1">English</Badge>
                          <p className="italic text-muted-foreground">{ex.english}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        )}
      </div>
    </div>
  );
};

export default Patterns;
