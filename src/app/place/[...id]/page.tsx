"use client";

import Image from "next/image";
import { useRouter, useParams } from "next/navigation";
import { resorts } from "@/data/resorts";
import { RunBreakdown } from "@/components/runBreakdown";
import {
  ArrowLeft,
  MapPin,
  Ticket,
  Package,
  Mountain,
  Navigation,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const ResortDetail = () => {
  const { id } = useParams();
  const router = useRouter();

  const resort = resorts.find((r) => r.id === id?.[0]);
  console.log("");
  console.log("");
  console.log("");
  console.log("id => ", id);
  console.log("resorts => ", resorts);

  if (!resort) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-serif text-foreground">
            Resort not found
          </h1>
          <Button variant="ghost" onClick={() => router.push("/")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to all resorts
          </Button>
        </div>
      </div>
    );
  }

  const totalRuns = resort.runs.green + resort.runs.blue + resort.runs.black;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border">
        <div className="px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/")}
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm">Back</span>
            </button>
            <div className="h-4 w-px bg-border" />
          </div>
        </div>
      </header>

      {/* Hero Image */}
      <div className="relative h-[40vh] md:h-[50vh] overflow-hidden">
        <Image
          src={resort.image}
          alt={resort.name}
          width={500}
          height={500}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/20 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 md:p-10">
          <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-medium text-foreground">
            {resort.name}
          </h1>
          <div className="flex items-center gap-2 mt-3 text-muted-foreground">
            <MapPin className="w-4 h-4" />
            <span className="text-sm">{resort.distance} km from Toronto</span>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-10 space-y-10">
        {/* Quick Stats */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Ticket className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wide">Day Pass</span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
          <div className="bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Package className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wide">Rental</span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
          <div className="bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Navigation className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wide">Distance</span>
            </div>
            <p className="text-2xl font-medium text-foreground">
              {resort.distance} km
            </p>
          </div>
          <div className="bg-card rounded-lg p-5 border border-border">
            <div className="flex items-center gap-2 text-muted-foreground mb-2">
              <Mountain className="w-4 h-4" />
              <span className="text-xs uppercase tracking-wide">
                Total Runs
              </span>
            </div>
            <p className="text-2xl font-medium text-foreground">{totalRuns}</p>
          </div>
        </section>

        {/* Terrain Breakdown */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Terrain Breakdown
          </h2>
          <div className="bg-card rounded-lg p-6 border border-border space-y-6">
            <RunBreakdown
              green={resort.runs.green}
              blue={resort.runs.blue}
              black={resort.runs.black}
            />

            <div className="grid grid-cols-3 gap-4 pt-4 border-t border-border">
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-green" />
                  <span className="text-sm text-muted-foreground">
                    Beginner
                  </span>
                </div>
                <p className="text-xl font-medium text-foreground">
                  {resort.runs.green} runs
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round((resort.runs.green / totalRuns) * 100)}% of
                  terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-blue" />
                  <span className="text-sm text-muted-foreground">
                    Intermediate
                  </span>
                </div>
                <p className="text-xl font-medium text-foreground">
                  {resort.runs.blue} runs
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round((resort.runs.blue / totalRuns) * 100)}% of terrain
                </p>
              </div>
              <div className="text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className="w-3 h-3 rounded-full bg-run-black" />
                  <span className="text-sm text-muted-foreground">
                    Advanced
                  </span>
                </div>
                <p className="text-xl font-medium text-foreground">
                  {resort.runs.black} runs
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round((resort.runs.black / totalRuns) * 100)}% of
                  terrain
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Details */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Pricing
          </h2>
          <div className="bg-card rounded-lg border border-border divide-y divide-border">
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-medium text-foreground">Day Pass</p>
                <p className="text-sm text-muted-foreground">
                  Full day lift access
                </p>
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.dayTicketPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5">
              <div>
                <p className="font-medium text-foreground">Equipment Rental</p>
                <p className="text-sm text-muted-foreground">
                  Skis or snowboard with boots
                </p>
              </div>
              <p className="text-xl font-medium text-foreground">
                ${resort.skiRentalPrice}
              </p>
            </div>
            <div className="flex items-center justify-between p-5 bg-muted/30">
              <div>
                <p className="font-medium text-foreground">Total Estimated</p>
                <p className="text-sm text-muted-foreground">
                  Day pass + rental
                </p>
              </div>
              <p className="text-xl font-medium text-primary">
                ${resort.dayTicketPrice + resort.skiRentalPrice}
              </p>
            </div>
          </div>
        </section>

        {/* Location */}
        <section className="space-y-4">
          <h2 className="font-serif text-xl font-medium text-foreground">
            Location
          </h2>
          <div className="bg-card rounded-lg p-6 border border-border">
            <div className="flex items-start gap-4">
              <div className="p-3 rounded-full bg-primary/10">
                <MapPin className="w-5 h-5 text-primary" />
              </div>
              <div className="space-y-1">
                <p className="font-medium text-foreground">
                  {resort.distance} km from Toronto
                </p>
                <p className="text-sm text-muted-foreground">
                  Coordinates: {resort.coordinates.lat.toFixed(4)}°N,{" "}
                  {Math.abs(resort.coordinates.lng).toFixed(4)}°W
                </p>
                <a
                  href={`https://www.google.com/maps/dir/?api=1&destination=${resort.coordinates.lat},${resort.coordinates.lng}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-2"
                >
                  Get directions
                  <ArrowLeft className="w-3 h-3 rotate-[135deg]" />
                </a>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default ResortDetail;
