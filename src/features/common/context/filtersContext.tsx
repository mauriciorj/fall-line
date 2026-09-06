"use client";

import { createContext, useContext, useState, useMemo, ReactNode } from "react";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { FilterState } from "@/src/features/common/components/filter";
import { toResort } from "@/utils/convexResort";
import { Resort } from "@/types/resort";

interface FiltersContextType {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  hoveredResort: string | null;
  setHoveredResort: (id: string | null) => void;
  selectedResort: string | null;
  setSelectedResort: (id: string | null) => void;
  filteredResorts: Resort[];
  isLoading: boolean;
  isFiltersActive: boolean;
  handleClearFilters: () => void;
}

const FiltersContext = createContext<FiltersContextType | undefined>(undefined);

export function FiltersProvider({ children }: { children: ReactNode }) {
  const [hoveredResort, setHoveredResort] = useState<string | null>(null);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);

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

  const dbResorts = useQuery(api.resorts.list);
  const allResorts = useMemo(
    () => (dbResorts ?? []).map(toResort).filter((resort): resort is Resort => resort !== null),
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

  const isLoading = dbResorts === undefined;
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
    throw new Error("useFiltersContext must be used within a FiltersProvider");
  }
  return context;
}
