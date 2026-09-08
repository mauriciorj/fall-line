"use client";

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

type TrackDifficulty = NonNullable<Resort["trackConditions"]>[number]["difficulty"];

type TrackSummary = {
  name: string;
  difficulty: TrackDifficulty;
  count: number;
};

const difficultyColor = {
  green: "bg-run-green",
  blue: "bg-run-blue",
  black: "bg-run-black",
  "double-black": "bg-run-black",
  "free-style": "bg-run-free-style",
};

const difficultyLabel = {
  green: "Beginner",
  blue: "Intermediate",
  black: "Advanced",
  "double-black": "Expert",
  "free-style": "Freestyle",
};

const TracksSection = ({ resort }: TracksSectionProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const trackConditions = resort.trackConditions ?? [];
  const summaryTracks: TrackSummary[] = [
    {
      name: difficultyLabel.green,
      difficulty: "green" as const,
      count: resort.runs.green,
    },
    {
      name: difficultyLabel.blue,
      difficulty: "blue" as const,
      count: resort.runs.blue,
    },
    {
      name: difficultyLabel.black,
      difficulty: "black" as const,
      count: resort.runs.black,
    },
    {
      name: difficultyLabel["double-black"],
      difficulty: "double-black" as const,
      count: resort.runs.doubleBlack,
    },
    {
      name: difficultyLabel["free-style"],
      difficulty: "free-style" as const,
      count: resort.runs.freeStyle ?? 0,
    },
  ].filter((track) => track.count > 0);
  const trackCount = trackConditions.length || summaryTracks.reduce(
    (total, track) => total + track.count,
    0,
  );

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
                  {trackCount} tracks
                </p>
              </div>
            </div>
            <ChevronDown
              className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
            />
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-5 pb-4 space-y-2">
              {trackConditions.length > 0
                ? [...trackConditions]
                    .sort((a, b) => {
                      const difficultyOrder: Record<string, number> = {
                        green: 1,
                        blue: 2,
                        black: 3,
                        "double-black": 4,
                        "free-style": 5,
                      };
                      const diff =
                        (difficultyOrder[a.difficulty] || 99) -
                        (difficultyOrder[b.difficulty] || 99);
                      if (diff !== 0) return diff;
                      return a.name.localeCompare(b.name);
                    })
                    .map((track, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between py-2 px-3 rounded-md"
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
                    ))
                : summaryTracks.map((track) => (
                    <div
                      key={track.difficulty}
                      className="flex items-center justify-between py-2 px-3 rounded-md"
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
                        {track.count} tracks
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
            <DialogContent className="w-full max-h-[85vh] overflow-auto">
              <DialogHeader>
                <DialogTitle className="font-serif">
                  {resort.name} — Trail Map
                </DialogTitle>
              </DialogHeader>
              <div className="mt-2">
                <Image
                  src={resort.trailMap}
                  alt={`${resort.name} trail map`}
                  width={1200}
                  height={800}
                  className="w-full h-auto rounded-md"
                />
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </section>
  );
};

export default TracksSection;
