import { GoogleMap, useLoadScript, MarkerF } from "@react-google-maps/api";
import { Resort } from "@/types/resort";
import { useMemo } from "react";

function MapPlaceholder({ message }: { message: string }) {
  return (
    <div className="w-full h-full bg-secondary flex items-center justify-center">
      <div className="text-center space-y-3">
        <div className="w-12 h-12 mx-auto rounded-full bg-muted flex items-center justify-center">
          <svg
            className="w-6 h-6 text-muted-foreground"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
            />
          </svg>
        </div>
        <p className="text-sm text-muted-foreground">{message}</p>
      </div>
    </div>
  );
}

interface ResortMapProps {
  resorts: Resort[];
  hoveredResortId: string | null;
  onMarkerHover: (id: string | null) => void;
}

// Desaturated, clean map style
const mapStyles = [
  {
    featureType: "all",
    elementType: "geometry",
    stylers: [{ saturation: -80 }],
  },
  {
    featureType: "all",
    elementType: "labels.text.fill",
    stylers: [{ color: "#666666" }],
  },
  {
    featureType: "water",
    elementType: "geometry.fill",
    stylers: [{ color: "#d4e4ed" }],
  },
  {
    featureType: "landscape",
    elementType: "geometry.fill",
    stylers: [{ color: "#f5f5f2" }],
  },
  {
    featureType: "road",
    elementType: "geometry.fill",
    stylers: [{ color: "#ffffff" }],
  },
  {
    featureType: "road",
    elementType: "geometry.stroke",
    stylers: [{ color: "#e0e0e0" }],
  },
  {
    featureType: "poi",
    elementType: "all",
    stylers: [{ visibility: "off" }],
  },
];

const containerStyle = {
  width: "100%",
  height: "100%",
};

// Center on Ontario
const defaultCenter = {
  lat: 44.5,
  lng: -80.0,
};

export function ResortMap({
  resorts,
  hoveredResortId,
  onMarkerHover,
}: ResortMapProps) {
  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API!, // Will show in demo mode without key
  });

  const options = useMemo(
    () => ({
      // styles: mapStyles,
      disableDefaultUI: true,
      zoomControl: true,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    }),
    [],
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
      {resorts.map((resort) => (
        <MarkerF
          icon={{
            path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z",
            fillColor: hoveredResortId === resort.id ? "#4A6FA5" : "#6B7280",
            fillOpacity: 1,
            strokeColor: "#ffffff",
            strokeWeight: 2,
            scale: hoveredResortId === resort.id ? 1.8 : 1.4,
            anchor: { x: 12, y: 24 } as google.maps.Point,
          }}
          key={resort.id}
          onMouseOver={() => onMarkerHover(resort.id)}
          onMouseOut={() => onMarkerHover(null)}
          position={resort.coordinates}
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
}
