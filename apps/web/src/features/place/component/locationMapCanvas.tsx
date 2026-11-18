"use client";

import { useMemo } from "react";
import { GoogleMap, MarkerF, useLoadScript } from "@react-google-maps/api";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

// Loaded via next/dynamic from LocationMap once the section is near the
// viewport: this is the only place on the resort page that pulls in
// @react-google-maps/api and the Google Maps script.
export default function LocationMapCanvas({ resort }: { resort: Resort }) {
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

  if (loadError || !isLoaded || !resort.coordinates) {
    return (
      <MapPlaceholder message={t(loadError ? "unableLoadMap" : "loadingMap")} />
    );
  }

  return (
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
  );
}
