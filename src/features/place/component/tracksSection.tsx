import Image from "next/image";
import { useState } from "react";
import { Resort } from "@/types/resort";
import { Snowflake, Map, ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface TracksSectionProps {
  resort: Resort;
}

const difficultyColor = {
  green: "bg-run-green",
  blue: "bg-run-blue",
  black: "bg-run-black",
  "double-black": "bg-run-black",
};

const difficultyLabel = {
  green: "Beginner",
  blue: "Intermediate",
  black: "Advanced",
  "double-black": "Expert",
};

export function TracksSection({ resort }: TracksSectionProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getFileType = (url: string) => {
    if (/\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url)) return "image";
    if (/\.pdf$/i.test(url)) return "pdf";
    return null;
  };

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">Tracks</h2>
      <div className="bg-card rounded-lg border border-border divide-y divide-border">
        {/* Track Conditions - Collapsible */}
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger className="w-full flex items-center justify-between p-5 hover:bg-muted/30 transition-colors">
            <div className="flex items-center gap-4">
              <Snowflake className="w-4 h-4 text-muted-foreground shrink-0" />
              <div className="text-left">
                <p className="text-sm font-medium text-foreground">
                  Track Conditions
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {resort?.trackConditions?.length} tracks
                </p>
              </div>
            </div>
            <ChevronDown
              className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
            />
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-5 pb-4 space-y-2">
              {resort?.trackConditions?.map((track, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20"
                >
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`w-2.5 h-2.5 rounded-full ${difficultyColor[track.difficulty]}`}
                    />
                    <span className="text-sm text-foreground">
                      {track.name}
                    </span>
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {track.condition}
                  </span>
                </div>
              ))}
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Trail Map - Dialog */}
        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-4">
            <Map className="w-4 h-4 text-muted-foreground shrink-0" />
            <p className="text-sm font-medium text-foreground">Trail Map</p>
          </div>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                View Map
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-3xl max-h-[85vh] overflow-auto">
              <DialogHeader>
                <DialogTitle className="font-serif">
                  {resort.name} — Trail Map
                </DialogTitle>
              </DialogHeader>
              {/* <div className="mt-2">
                {getFileType(resort?.trailMap) === "pdf" && (
                  <iframe
                    src={resort.trailMap}
                    className="w-full h-[70vh] rounded-md border border-border"
                  />
                )}
                {getFileType(resort?.trailMap) === "image" && (
                  <Image
                    src={resort.trailMap}
                    alt={`${resort.name} trail map`}
                    className="w-full rounded-md"
                  />
                )}
              </div> */}
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </section>
  );
}
