"use client";

import { useMemo } from "react";
import { GoogleMap, useLoadScript, MarkerF } from "@react-google-maps/api";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

interface ResortMapProps {
  hoveredResort: string | null;
  resorts: Resort[];
  selectedResort: string | null;
  setHoveredResort: (id: string | null) => void;
  setSelectedResort: (id: string | null) => void;
}

const ResortMap = ({
  hoveredResort,
  resorts,
  selectedResort,
  setHoveredResort,
  setSelectedResort,
}: ResortMapProps) => {
  const { t } = useLanguage();
  const { isLoaded, loadError } = useLoadScript({
    id: "google-maps-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API!, // Will show in demo mode without key
  });
  const containerStyle = {
    width: "100%",
    height: "100%",
  };

  // Center on Ontario
  const defaultCenter = {
    lat: 44.5,
    lng: -80.0,
  };

  const options = useMemo(
    () => ({
      // styles: mapStyles,
      disableDefaultUI: true,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    }),
    []
  );

  if (loadError) {
    return <MapPlaceholder message={t("unableLoadMap")} />;
  }

  if (!isLoaded) {
    return <MapPlaceholder message={t("loadingMap")} />;
  }

  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={defaultCenter}
      zoom={8}
      options={options}
    >
      {resorts.filter((resort) => resort.coordinates).map((resort) => (
        <MarkerF
          icon={{
            path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
            fillColor:
              hoveredResort === resort.resortId || selectedResort === resort.resortId
                ? "#4A6FA5"
                : "#6B7280",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: hoveredResort === resort.resortId ? 1.8 : 1.4,
            anchor: { x: 12, y: 24 } as google.maps.Point,
          }}
          key={resort.resortId}
          onClick={() => setSelectedResort(resort.resortId)}
          onMouseOver={() => setHoveredResort(resort.resortId)}
          onMouseOut={() => setHoveredResort(null)}
          position={resort.coordinates!}
          label={{
            text: resort.name,
            color: "#333",
            fontSize: "12px",
            fontWeight: "bold",
          }}
        ></MarkerF>
      ))}
    </GoogleMap>
  );
};

export default ResortMap;
