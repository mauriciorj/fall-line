"use client";

import { useEffect, useMemo, useState } from "react";
import { GoogleMap, useLoadScript, MarkerF } from "@react-google-maps/api";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
import { useLanguage } from "@/src/i18n";
import { Coordinates, Resort } from "@/types/resort";

const DEFAULT_CENTER: Coordinates = { lat: 44.5, lng: -80.0 };
const MAX_FIT_ZOOM = 11;
const FIT_PADDING = 50;

interface ResortMapProps {
  hoveredResort: string | null;
  userCoordinates: Coordinates | null;
  resorts: Resort[];
  selectedResort: string | null;
  setHoveredResort: (id: string | null) => void;
  setSelectedResort: (id: string | null) => void;
}

const ResortMap = ({
  hoveredResort,
  userCoordinates,
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

  // Initial view only; later view changes come from fitting the resort markers.
  const [initialCenter] = useState<Coordinates>(
    () => userCoordinates ?? DEFAULT_CENTER,
  );
  const [map, setMap] = useState<google.maps.Map | null>(null);

  const mappedResorts = useMemo(
    () => resorts.filter((resort) => resort.coordinates),
    [resorts],
  );
  const mappedResortsKey = mappedResorts
    .map((resort) => resort.resortId)
    .join("|");

  useEffect(() => {
    if (!map || mappedResorts.length === 0) return;

    if (mappedResorts.length === 1) {
      map.setCenter(mappedResorts[0].coordinates!);
      map.setZoom(MAX_FIT_ZOOM);
      return;
    }

    const bounds = new google.maps.LatLngBounds();
    mappedResorts.forEach((resort) => bounds.extend(resort.coordinates!));
    map.fitBounds(bounds, FIT_PADDING);
    const listener = google.maps.event.addListenerOnce(
      map,
      "idle",
      () => {
        if ((map.getZoom() ?? 0) > MAX_FIT_ZOOM) map.setZoom(MAX_FIT_ZOOM);
      },
    );
    return () => listener.remove();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [map, mappedResortsKey]);

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
      center={initialCenter}
      zoom={8}
      options={options}
      onLoad={setMap}
      onUnmount={() => setMap(null)}
    >
      {userCoordinates && (
        <MarkerF
          position={userCoordinates}
          title={t("yourLocation")}
          icon={{
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: "#2563eb",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: 8,
          }}
        />
      )}
      {mappedResorts.map((resort) => (
        <MarkerF
          icon={{
            path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
            fillColor:
              hoveredResort === resort.resortId || selectedResort === resort.resortId
                ? "#4A6FA5"
                : "#8fb7f2",
            fillOpacity: 1,
            strokeColor: "#086bfc",
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
