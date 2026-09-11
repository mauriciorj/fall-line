"use client";

import ResortList from "@/components/resortList";
import ResortMap from "@/components/resortMap";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "@/components/ui/resizable";
import { useFiltersContext } from "@/context/filtersContext";
import { useIsMobile } from "@/hooks/useMobile";

const Index = () => {
  const isMobile = useIsMobile();

  const {
    filteredResorts,
    isLoading,
    hoveredResort,
    selectedResort,
    userCoordinates,
    setHoveredResort,
    setSelectedResort,
  } = useFiltersContext();

  return (
    <main className="flex flex-col lg:flex-row h-[calc(100vh-57px)]">
      {isMobile ? (
        <ResizablePanelGroup direction="vertical" className="h-full">
          <ResizablePanel defaultSize={50} minSize={15}>
            <ResortMap
              hoveredResort={hoveredResort}
              selectedResort={selectedResort}
              userCoordinates={userCoordinates}
              setHoveredResort={setHoveredResort}
              setSelectedResort={setSelectedResort}
              resorts={filteredResorts}
            />
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={50} minSize={15}>
            <div className="overflow-y-auto h-full">
              <ResortList
                hoveredResort={hoveredResort}
                resorts={filteredResorts}
                selectedResort={selectedResort}
                isLoading={isLoading}
                setHoveredResort={setHoveredResort}
              />
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      ) : (
        <>
          <section className="order-2 lg:order-1 w-full lg:w-[480px] xl:w-[520px] flex-1 lg:flex-none border-t lg:border-t-0 lg:border-r border-border flex flex-col overflow-hidden min-h-0">
            <ResortList
              hoveredResort={hoveredResort}
              resorts={filteredResorts}
              selectedResort={selectedResort}
              isLoading={isLoading}
              setHoveredResort={setHoveredResort}
            />
          </section>

          <section className="order-1 lg:order-2 w-full h-[40%] lg:h-auto flex-none lg:flex-1 relative">
            <ResortMap
              hoveredResort={hoveredResort}
              resorts={filteredResorts}
              selectedResort={selectedResort}
              userCoordinates={userCoordinates}
              setHoveredResort={setHoveredResort}
              setSelectedResort={setSelectedResort}
            />
          </section>
        </>
      )}
    </main>
  );
};

export default Index;
