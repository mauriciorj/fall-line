"use client";

import { useEffect, useRef } from "react";
import { useLoadScript } from "@react-google-maps/api";
import { LocationOption, matchLocation } from "@/types/location";
import type { Coordinates } from "@/types/resort";

// Mounted only for a first visit with geolocation granted and no saved
// location, so the Google Maps script is loaded on demand instead of on every
// page. Renders nothing; reports the matched location (or null) once.
export default function RegionDetector({
  coordinates,
  locations,
  onResolved,
}: {
  coordinates: Coordinates;
  locations: LocationOption[];
  onResolved: (location: LocationOption | null) => void;
}) {
  const { isLoaded, loadError } = useLoadScript({
    id: "google-maps-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API ?? "",
  });
  const resolved = useRef(false);

  useEffect(() => {
    if (resolved.current) return;
    if (loadError) {
      resolved.current = true;
      onResolved(null);
      return;
    }
    if (!isLoaded) return;

    resolved.current = true;
    new google.maps.Geocoder().geocode(
      { location: coordinates },
      (results, status) => {
        if (status !== "OK" || !results?.[0]) {
          onResolved(null);
          return;
        }
        const components = results[0].address_components;
        const country = components.find((component) =>
          component.types.includes("country"),
        )?.long_name;
        const region = components.find((component) =>
          component.types.includes("administrative_area_level_1"),
        )?.long_name;
        onResolved(
          country && region
            ? (matchLocation(locations, country, region) ?? null)
            : null,
        );
      },
    );
  }, [coordinates, isLoaded, loadError, locations, onResolved]);

  return null;
}
