"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  ReactNode,
} from "react";
import { useQuery } from "convex/react";
import dynamic from "next/dynamic";
import { api } from "@/convex/_generated/api";
import { FilterState } from "@/src/features/common/components/filter";
import { toResort } from "@/utils/convexResort";
import {
  applyResortFilters,
  defaultFilters,
} from "@/utils/resortFilters";
import {
  LocationOption,
  findDefaultLocation,
  locationKey,
} from "@/types/location";
import { Coordinates, Resort } from "@/types/resort";

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
  userCoordinates: Coordinates | null;
  filteredResorts: Resort[];
  // Newest resort-data write in the current list (null until data carries it).
  dataUpdatedAt: number | null;
  isLoading: boolean;
  isFiltersActive: boolean;
  handleClearFilters: () => void;
}

const FiltersContext = createContext<FiltersContextType | undefined>(undefined);

// Code-split: pulls in @react-google-maps/api only when a detection is pending.
const RegionDetector = dynamic(() => import("@/components/regionDetector"), {
  ssr: false,
});
const SELECTED_LOCATION_STORAGE_KEY = "selected-location";

export function FiltersProvider({ children }: { children: ReactNode }) {
  const isGoogleMapsKeyAvailable = Boolean(
    process.env.NEXT_PUBLIC_GOOGLE_MAPS_JAVASCRIPT_API,
  );
  const [hoveredResort, setHoveredResort] = useState<string | null>(null);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);
  const [selectedLocation, setSelectedLocation] =
    useState<LocationOption | null>(null);
  const [userCoordinates, setUserCoordinates] = useState<Coordinates | null>(
    null,
  );
  // Coordinates awaiting reverse geocoding (first visit, no saved location).
  const [pendingDetection, setPendingDetection] = useState<Coordinates | null>(
    null,
  );
  const locationInitialized = useRef(false);

  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  const dbLocations = useQuery(api.locations.list);
  const locations = useMemo(() => dbLocations ?? [], [dbLocations]);
  const fallbackLocation = useMemo(
    () => findDefaultLocation(locations),
    [locations],
  );

  const commitLocation = useCallback((location: LocationOption) => {
    locationInitialized.current = true;
    window.localStorage.setItem(
      SELECTED_LOCATION_STORAGE_KEY,
      locationKey(location),
    );
    window.setTimeout(() => setSelectedLocation(location), 0);
  }, []);

  useEffect(() => {
    if (
      locationInitialized.current ||
      dbLocations === undefined ||
      !fallbackLocation
    ) {
      return;
    }

    const savedKey = window.localStorage.getItem(
      SELECTED_LOCATION_STORAGE_KEY,
    );
    const savedLocation = locations.find(
      (location) => locationKey(location) === savedKey,
    );
    const hasSavedLocation = Boolean(savedLocation);

    if (savedLocation) {
      commitLocation(savedLocation);
    }

    if (!navigator.geolocation) {
      if (!hasSavedLocation) {
        commitLocation(fallbackLocation);
      }
      return;
    }

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const coordinates = {
          lat: coords.latitude,
          lng: coords.longitude,
        };
        setUserCoordinates(coordinates);

        if (hasSavedLocation) {
          return;
        }

        if (!isGoogleMapsKeyAvailable) {
          commitLocation(fallbackLocation);
          return;
        }

        // Defer to RegionDetector, which loads Google Maps only now.
        setPendingDetection(coordinates);
      },
      () => {
        if (!hasSavedLocation) {
          commitLocation(fallbackLocation);
        }
      },
      { enableHighAccuracy: false, maximumAge: 300000, timeout: 10000 },
    );
  }, [
    commitLocation,
    dbLocations,
    fallbackLocation,
    isGoogleMapsKeyAvailable,
    locations,
  ]);

  const handleDetected = useCallback(
    (location: LocationOption | null) => {
      setPendingDetection(null);
      const resolved = location ?? fallbackLocation;
      if (resolved) commitLocation(resolved);
    },
    [commitLocation, fallbackLocation],
  );

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
        .map((resort) => toResort(resort))
        .filter((resort): resort is Resort => resort !== null),
    [dbResorts],
  );

  const filteredResorts = useMemo(
    () => applyResortFilters(allResorts, filters, userCoordinates),
    [allResorts, filters, userCoordinates],
  );
  const dataUpdatedAt = useMemo(
    () =>
      allResorts.reduce<number | null>(
        (latest, resort) =>
          resort.updatedAt ? Math.max(latest ?? 0, resort.updatedAt) : latest,
        null,
      ),
    [allResorts],
  );

  const isLoading =
    dbLocations === undefined ||
    selectedLocation === null ||
    dbResorts === undefined;
  const isFiltersActive =
    filters.distanceRange[0] > 0 ||
    filters.distanceRange[1] < 250 ||
    filters.activities !== null;

  const handleClearFilters = () => {
    setFilters(defaultFilters);
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
    userCoordinates,
    filteredResorts,
    dataUpdatedAt,
    isLoading,
    isFiltersActive,
    handleClearFilters,
  };

  return (
    <FiltersContext.Provider value={value}>
      {pendingDetection && (
        <RegionDetector
          coordinates={pendingDetection}
          locations={locations}
          onResolved={handleDetected}
        />
      )}
      {children}
    </FiltersContext.Provider>
  );
}

export function useFiltersContext() {
  const context = useContext(FiltersContext);
  if (context === undefined) {
    throw new Error("useFiltersContext must be used within FiltersProvider");
  }
  return context;
}
