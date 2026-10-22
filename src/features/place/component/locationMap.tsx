"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import { ArrowUpRight } from "lucide-react";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

// Code-split and mounted only when the section is near the viewport, so the
// page's LCP/INP never pay for a below-the-fold map.
const LocationMapCanvas = dynamic(
  () => import("@/src/features/place/component/locationMapCanvas"),
  { ssr: false },
);

const LocationMap = ({ resort }: { resort: Resort }) => {
  const { t } = useLanguage();
  const containerRef = useRef<HTMLDivElement>(null);
  const [isNearViewport, setIsNearViewport] = useState(false);

  useEffect(() => {
    const element = containerRef.current;
    if (!element || isNearViewport) return;
    if (typeof IntersectionObserver === "undefined") {
      const timer = window.setTimeout(() => setIsNearViewport(true), 0);
      return () => window.clearTimeout(timer);
    }
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setIsNearViewport(true);
          observer.disconnect();
        }
      },
      { rootMargin: "600px 0px" },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, [isNearViewport]);

  if (!resort.coordinates) {
    return null;
  }

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("map")}
      </h2>
      <div
        ref={containerRef}
        className="relative h-80 overflow-hidden rounded-lg border border-border"
      >
        {isNearViewport ? (
          <LocationMapCanvas resort={resort} />
        ) : (
          <MapPlaceholder message={t("loadingMap")} />
        )}
        {resort.googleMapsUrl && (
          <a
            href={resort.googleMapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="absolute top-3 right-3 z-10 inline-flex items-center gap-2 rounded-md bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg ring-1 ring-black/10 transition-colors hover:bg-primary/90"
          >
            {t("getDirections")}
            <ArrowUpRight className="h-4 w-4" />
          </a>
        )}
      </div>
    </section>
  );
};

export default LocationMap;
