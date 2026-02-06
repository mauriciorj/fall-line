"use client";

import { useState, useMemo } from "react";
import { Header } from "@/components/header";
import { ResortList } from "@/components/resortList";
import { ResortMap } from "@/components/resortMap";
import { FilterState } from "@/components/filterPopover";
import { resorts as allResorts } from "@/data/resorts";
import { useIsMobile } from "@/hooks/useMobile";
// import { Group, Panel } from "react-resizable-panels";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Drawer, DrawerContent } from "@/components/ui/drawer";

const Index = () => {
  const isMobile = useIsMobile();

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
      <Header
        filters={filters}
        onFiltersChange={setFilters}
        isFiltersActive={isFiltersActive}
        onClearFilters={handleClearFilters}
      />

      <main className="flex flex-col lg:flex-row h-[calc(100vh-57px)]">
        {isMobile ? (
          <ResizablePanelGroup orientation="vertical" className="h-full">
            <ResizablePanel defaultSize={50} minSize={15}>
              <ResortMap
                resorts={filteredResorts}
                hoveredResortId={hoveredResortId}
                onMarkerHover={setHoveredResortId}
              />
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={50} minSize={15}>
              <div className="overflow-y-auto h-full">
                <ResortList
                  resorts={filteredResorts}
                  hoveredResortId={hoveredResortId}
                  onHover={setHoveredResortId}
                />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        ) : (
          <>
            <section className="order-2 lg:order-1 w-full lg:w-[480px] xl:w-[520px] flex-1 lg:flex-none border-t lg:border-t-0 lg:border-r border-border flex flex-col overflow-hidden min-h-0">
              <ResortList
                resorts={filteredResorts}
                hoveredResortId={hoveredResortId}
                onHover={setHoveredResortId}
              />
            </section>

            <section className="order-1 lg:order-2 w-full h-[40%] lg:h-auto flex-none lg:flex-1 relative">
              <ResortMap
                resorts={filteredResorts}
                hoveredResortId={hoveredResortId}
                onMarkerHover={setHoveredResortId}
              />
            </section>
          </>
        )}
      </main>
    </div>
  );
};

export default Index;
