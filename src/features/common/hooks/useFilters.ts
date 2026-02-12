"use client";

import { useState, useMemo, useEffect } from "react";
import { FilterState } from "@/src/features/common/components/filter";
import { resorts as allResorts } from "@/data/resorts";

const useFilters = () => {
  const [hoveredResort, setHoveredResort] = useState<string | null>(null);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);

  const [filters, setFilters] = useState<FilterState>({
    sortBy: "price",
    distanceRange: [0, 250],
    activities: null,
  });

  useEffect(() => {}, []);

  const filteredResorts = useMemo(() => {
    console.log("");
    console.log("");
    console.log("");
    console.log("filters => ", filters);
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

  console.log("");
  console.log("");
  console.log("");
  console.log("filteredResorts => ", filteredResorts);

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

  return {
    filters,
    filteredResorts,
    handleClearFilters,
    hoveredResort,
    isFiltersActive,
    selectedResort,
    setFilters,
    setHoveredResort,
    setSelectedResort,
  };
};

export default useFilters;
