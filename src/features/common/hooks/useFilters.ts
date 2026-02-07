"use client";

import { useState, useMemo } from "react";
import { FilterState } from "@/components/filterPopover";
import { resorts as allResorts } from "@/data/resorts";

const useFilters = () => {
  const [hoveredResortId, setHoveredResortId] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    sortBy: "distance",
    distanceRange: [0, 250],
    difficulty: null,
  });

  const filteredResorts = useMemo(() => {
    let result = allResorts.filter((resort) => {
      // Distance filter
      if (
        resort.distance < filters.distanceRange[0] ||
        resort.distance > filters.distanceRange[1]
      ) {
        return false;
      }
      // Difficulty emphasis filter
      if (filters.difficulty) {
        const total = resort.runs.green + resort.runs.blue + resort.runs.black;
        const greenRatio = resort.runs.green / total;
        const blueRatio = resort.runs.blue / total;
        const blackRatio = resort.runs.black / total;

        if (filters.difficulty === "beginner" && greenRatio < 0.25)
          return false;
        if (filters.difficulty === "intermediate" && blueRatio < 0.3)
          return false;
        if (filters.difficulty === "advanced" && blackRatio < 0.15)
          return false;
      }
      return true;
    });

    // Sort
    result = [...result].sort((a, b) => {
      if (filters.sortBy === "distance") {
        return a.distance - b.distance;
      }
      return a.dayTicketPrice - b.dayTicketPrice;
    });

    return result;
  }, [filters]);

  const isFiltersActive =
    filters.distanceRange[0] > 0 ||
    filters.distanceRange[1] < 250 ||
    filters.difficulty !== null;

  const handleClearFilters = () => {
    setFilters({
      sortBy: "distance",
      distanceRange: [0, 250],
      difficulty: null,
    });
  };

  return {
    hoveredResortId,
    setHoveredResortId,
    filters,
    setFilters,
    filteredResorts,
    isFiltersActive,
    handleClearFilters,
  };
};

export default useFilters;
