"use client";

import { useState, useMemo } from "react";
import { HeroSection } from "@/components/heroSection";
import { ResortList } from "@/components/resortList";
import { StaticMap } from "@/components/staticMap";
import { FilterState } from "@/components/filterPopover";
import { resorts as allResorts } from "@/data/resorts";

const Index = () => {
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

  return (
    <div className="min-h-screen bg-background">
      <HeroSection
        filters={filters}
        onFiltersChange={setFilters}
        isFiltersActive={isFiltersActive}
        onClearFilters={handleClearFilters}
      />

      <main className="flex flex-col lg:flex-row h-[calc(100vh-57px)]">
        {/* Resort Cards - Left Side */}
        <section className="w-full lg:w-[480px] xl:w-[520px] flex-shrink-0 border-r border-border flex flex-col">
          <ResortList
            resorts={filteredResorts}
            hoveredResortId={hoveredResortId}
            onHover={setHoveredResortId}
          />
        </section>

        {/* Map - Right Side */}
        <section className="flex-1 hidden lg:block">
          <StaticMap
            resorts={filteredResorts}
            hoveredResortId={hoveredResortId}
            onMarkerHover={setHoveredResortId}
          />
        </section>
      </main>
    </div>
  );
};

export default Index;
