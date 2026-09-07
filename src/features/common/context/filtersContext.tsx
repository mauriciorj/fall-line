"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  ReactNode,
} from "react";
import { useQuery } from "convex/react";
import { useLoadScript } from "@react-google-maps/api";
import { api } from "@/convex/_generated/api";
import { FilterState } from "@/src/features/common/components/filter";
import { toResort } from "@/utils/convexResort";
import { LocationOption, locationKey } from "@/types/location";
import { Resort } from "@/types/resort";

interface FiltersContextType {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  hoveredResort: string | null;
  setHoveredResort: (id: string | null) => void;
  selectedResort: string | null;
  setSelectedResort: (id: string | null) => void;
  locations: LocationOption[];
  selectedLocation: LocationOption | null;
  setLocation: (location: LocationOption) => void;
  filteredResorts: Resort[];
  isLoading: boolean;
  isFiltersActive: boolean;
  handleClearFilters: () => void;
}

const FiltersContext = createContext<FiltersContextType | undefined>(undefined);
const SELECTED_LOCATION_STORAGE_KEY = "selected-location";

function findLocation(
  locations: LocationOption[],
  country: string,
  region: string,
) {
  const normalizedCountry = country.toLowerCase();
  const normalizedRegion = region.toLowerCase();
  return (
    locations.find(
      (location) =>
        location.country.toLowerCase() === normalizedCountry &&
        location.region.toLowerCase() === normalizedRegion,
    ) ??
    locations.find(
      (location) =>
        location.country.toLowerCase() === normalizedCountry &&
        location.region.toLowerCase() === "unknown",
    ) ??
    locations.find((location) => location.country.toLowerCase() === normalizedCountry)
  );
}

export function FiltersProvider({ children }: { children: ReactNode }) {
  const isGoogleMapsKeyAvailable = Boolean(
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API,
  );
  const { isLoaded: isGoogleMapsLoaded, loadError: googleMapsLoadError } = useLoadScript({
    id: "google-maps-script",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API ?? "",
  });
  const [hoveredResort, setHoveredResort] = useState<string | null>(null);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);
  const [selectedLocation, setSelectedLocation] =
    useState<LocationOption | null>(null);
  const locationInitialized = useRef(false);

  const [filters, setFilters] = useState<FilterState>({
    sortBy: "price",
    distanceRange: [0, 250],
    activities: {
      accommodations: false,
      crosscountry: false,
      lessons: false,
      snowshoeing: false,
      spa: false,
      tubbing: false,
    },
  });

  const dbLocations = useQuery(api.locations.list);
  const locations = useMemo(() => dbLocations ?? [], [dbLocations]);

  useEffect(() => {
    if (
      locationInitialized.current ||
      dbLocations === undefined ||
      locations.length === 0
    ) {
      return;
    }

    const savedKey = window.localStorage.getItem(
      SELECTED_LOCATION_STORAGE_KEY,
    );
    const savedLocation = locations.find(
      (location) => locationKey(location) === savedKey,
    );
    const commitLocation = (location: LocationOption) => {
      locationInitialized.current = true;
      window.localStorage.setItem(
        SELECTED_LOCATION_STORAGE_KEY,
        locationKey(location),
      );
      window.setTimeout(() => setSelectedLocation(location), 0);
    };

    if (savedLocation) {
      commitLocation(savedLocation);
      return;
    }

    const fallbackLocation =
      locations.find(
        (location) =>
          location.country === "Canada" && location.region === "Ontario",
      ) ?? locations[0];

    const selectLocation = commitLocation;

    if (
      !isGoogleMapsKeyAvailable ||
      googleMapsLoadError ||
      !isGoogleMapsLoaded
    ) {
      if (!isGoogleMapsKeyAvailable || googleMapsLoadError) {
        selectLocation(fallbackLocation);
      }
      return;
    }

    if (!navigator.geolocation) {
      selectLocation(fallbackLocation);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        new google.maps.Geocoder().geocode(
          {
            location: { lat: coords.latitude, lng: coords.longitude },
          },
          (results, status) => {
            if (status === "OK" && results?.[0]) {
              const components = results[0].address_components;
              const country = components.find((component) =>
                component.types.includes("country"),
              )?.long_name;
              const region = components.find((component) =>
                component.types.includes("administrative_area_level_1"),
              )?.long_name;
              const detected =
                country && region
                  ? findLocation(locations, country, region)
                  : undefined;
              selectLocation(detected ?? fallbackLocation);
              return;
            }
            selectLocation(fallbackLocation);
          },
        );
      },
      () => selectLocation(fallbackLocation),
      { enableHighAccuracy: false, maximumAge: 300000, timeout: 10000 },
    );
  }, [
    dbLocations,
    googleMapsLoadError,
    isGoogleMapsKeyAvailable,
    isGoogleMapsLoaded,
    locations,
  ]);

  const dbResorts = useQuery(
    api.resorts.list,
    selectedLocation
      ? {
          continent: selectedLocation.continent,
          country: selectedLocation.country,
          region: selectedLocation.region,
        }
      : "skip",
  );
  const allResorts = useMemo(
    () =>
      (dbResorts ?? [])
        .map(toResort)
        .filter((resort): resort is Resort => resort !== null),
    [dbResorts],
  );

  const filteredResorts = useMemo(() => {
    let result = allResorts.filter((resort) => {
      // Activities filter
      const { activities } = filters;

      if (activities.accommodations && !resort.hasAccommodations) return false;
      if (activities.crosscountry && !resort.hasCrossCountry) return false;
      if (activities.lessons && !resort.hasLessons) return false;
      if (activities.snowshoeing && !resort.hasSnowshoeing) return false;
      if (activities.spa && !resort.hasSpa) return false;
      if (activities.tubbing && !resort.hasTubing) return false;

      return true;
    });

    // Sort
    result = [...result].sort((a, b) => {
      if (filters.sortBy === "rating") {
        return b.rating - a.rating;
      }
      return a.dayTicketPrice - b.dayTicketPrice;
    });

    return result;
  }, [allResorts, filters]);

  const isLoading =
    dbLocations === undefined ||
    selectedLocation === null ||
    dbResorts === undefined;
  const isFiltersActive =
    filters.distanceRange[0] > 0 ||
    filters.distanceRange[1] < 250 ||
    filters.activities !== null;

  const handleClearFilters = () => {
    setFilters({
      sortBy: "price",
      distanceRange: [0, 250],
      activities: {
        accommodations: false,
        crosscountry: false,
        lessons: false,
        snowshoeing: false,
        spa: false,
        tubbing: false,
      },
    });
  };

  const value = {
    filters,
    setFilters,
    hoveredResort,
    setHoveredResort,
    selectedResort,
    setSelectedResort,
    locations,
    selectedLocation,
    setLocation: (location: LocationOption) => {
      setSelectedLocation(location);
      window.localStorage.setItem(
        SELECTED_LOCATION_STORAGE_KEY,
        locationKey(location),
      );
    },
    filteredResorts,
    isLoading,
    isFiltersActive,
    handleClearFilters,
  };

  return (
    <FiltersContext.Provider value={value}>{children}</FiltersContext.Provider>
  );
}

export function useFiltersContext() {
  const context = useContext(FiltersContext);
  if (context === undefined) {
    throw new Error("useFiltersContext must be used within FiltersProvider");
  }
  return context;
}
