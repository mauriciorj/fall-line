"use client";

import { useMemo } from "react";
import { ArrowUpRight } from "lucide-react";
import { GoogleMap, MarkerF, useLoadScript } from "@react-google-maps/api";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

const LocationMap = ({ resort }: { resort: Resort }) => {
  const { t } = useLanguage();
  const { isLoaded, loadError } = useLoadScript({
    id: "google-maps-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API ?? "",
  });
  const options = useMemo(
    () => ({
      disableDefaultUI: true,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    }),
    [],
  );

  if (!resort.coordinates) {
    return null;
  }

  if (loadError || !isLoaded) {
    return (
      <section className="space-y-4">
        <h2 className="font-serif text-xl font-medium text-foreground">
          {t("map")}
        </h2>
        <div className="h-80 overflow-hidden rounded-lg border border-border">
          <MapPlaceholder
            message={t(loadError ? "unableLoadMap" : "loadingMap")}
          />
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("map")}
      </h2>
      <div className="relative h-80 overflow-hidden rounded-lg border border-border">
        <GoogleMap
          mapContainerStyle={{ width: "100%", height: "100%" }}
          center={resort.coordinates}
          zoom={13}
          options={options}
        >
          <MarkerF
            position={resort.coordinates}
            title={resort.name}
            icon={{
              path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
              fillColor: "#4A6FA5",
              fillOpacity: 1,
              strokeColor: "#ffffff",
              strokeWeight: 2,
              scale: 1.6,
              anchor: { x: 12, y: 24 } as google.maps.Point,
            }}
          />
        </GoogleMap>
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
