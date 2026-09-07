import { useMemo } from "react";
import { GoogleMap, useLoadScript, MarkerF } from "@react-google-maps/api";
import MapPlaceholder from "@/components/resortMap/mapPlaceholder";
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
  const { isLoaded, loadError } = useLoadScript({
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
    return <MapPlaceholder message="Unable to load map" />;
  }

  if (!isLoaded) {
    return <MapPlaceholder message="Loading map..." />;
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
              hoveredResort === resort.sourceId || selectedResort === resort.sourceId
                ? "#4A6FA5"
                : "#6B7280",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: hoveredResort === resort.sourceId ? 1.8 : 1.4,
            anchor: { x: 12, y: 24 } as google.maps.Point,
          }}
          key={resort.sourceId}
          onClick={() => setSelectedResort(resort.sourceId)}
          onMouseOver={() => setHoveredResort(resort.sourceId)}
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
