"use client";

import { createContext, useContext, useState, useMemo, ReactNode } from "react";
import { FilterState } from "@/src/features/common/components/filter";
import { resorts as allResorts } from "@/data/resorts";
import { Resort } from "@/types/resort";

interface FiltersContextType {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  hoveredResort: string | null;
  setHoveredResort: (id: string | null) => void;
  selectedResort: string | null;
  setSelectedResort: (id: string | null) => void;
  filteredResorts: Resort[];
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
    activities: null,
  });

  const filteredResorts = useMemo(() => {
    let result = allResorts.filter((resort) => {
      // Activities filter
      if (filters.activities === "tubbing" && resort.hasTubing) {
        return true;
      } else if (filters.activities === "tubbing" && !resort.hasTubing) {
        return false;
      }
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
  }, [filters]);

  const isFiltersActive =
    filters.distanceRange[0] > 0 ||
    filters.distanceRange[1] < 250 ||
    filters.activities !== null;

  const handleClearFilters = () => {
    setFilters({
      sortBy: "price",
      distanceRange: [0, 250],
      activities: null,
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
