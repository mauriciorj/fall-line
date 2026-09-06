"use client";

import Image from "next/image";
import { useRouter, useParams } from "next/navigation";
import { useQuery } from "convex/react";
import { ArrowLeft, Ticket } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/convex/_generated/api";
import { toResort } from "@/utils/convexResort";
import InfoSection from "@/src/features/place/component/infoSection";
import LocationSection from "@/src/features/place/component/locationSection";
import PricingSection from "@/src/features/place/component/pricingSection";
import TerrainSection from "@/src/features/place/component/terrainSection";
import TracksSection from "@/place/component/tracksSection";

const ResortDetail = () => {
  const { id } = useParams();
  const router = useRouter();
  const resortId = Array.isArray(id) ? id[0] : id;
  const dbResort = useQuery(
    api.resorts.getById,
    resortId ? { id: resortId } : "skip",
  );
  const resort = toResort(dbResort);

  if (dbResort === undefined) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Loading resort...</p>
      </div>
    );
  }

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

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Image */}
      <div className="relative h-[40vh] md:h-[50vh] overflow-hidden">
        <Image
          src={resort.image}
          alt={resort.name}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/20 to-transparent" />
        <div className="absolute bottom-10 left-0 right-0 p-6 md:p-10">
          <h1 className="font-serif text-3xl md:text-4xl lg:text-5xl font-medium text-foreground">
            {resort.name}
          </h1>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-4xl mx-auto mb-20 px-6 py-10 space-y-10">
        {/* Buy Tickets CTA - Sticky on mobile */}
        {resort?.ticketUrl && (
          <div className="sticky top-16 z-30 bg-background/95 backdrop-blur-sm px-6 py-3">
            <a
              href={resort.ticketUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block"
            >
              <Button
                className="w-full h-12 text-base font-semibold shadow-lg"
                size="lg"
              >
                <Ticket className="w-5 h-5 mr-2" />
                Buy Tickets — from ${resort.dayTicketPrice}
              </Button>
            </a>
          </div>
        )}

        {/* Main Info */}
        <InfoSection resort={resort} />

        {/* Tracks */}
        <TracksSection resort={resort} />

        <TerrainSection resort={resort} />
        {/* Terrain Breakdown */}

        {/* Pricing Details */}
        <PricingSection resort={resort} />

        {/* Location */}
        <LocationSection resort={resort} />
      </main>
    </div>
  );
};

export default ResortDetail;
