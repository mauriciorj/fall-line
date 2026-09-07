import { useEffect, useRef } from "react";
import { Resort } from "@/types/resort";
import ResortCard from "@/components/resortCard";

interface ResortListProps {
  hoveredResort: string | null;
  resorts: Resort[];
  selectedResort: string | null;
  isLoading?: boolean;
  setHoveredResort: (id: string | null) => void;
}

const ResortList = ({
  hoveredResort,
  resorts,
  selectedResort,
  isLoading = false,
  setHoveredResort,
}: ResortListProps) => {
  const itemRefs = useRef<Record<string, HTMLDivElement | null>>({});

  useEffect(() => {
    if (selectedResort && itemRefs.current[selectedResort]) {
      itemRefs.current[selectedResort]?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [selectedResort]);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <p className="text-muted-foreground text-sm">Loading resorts...</p>
      </div>
    );
  }

  if (resorts.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center space-y-2">
          <p className="text-muted-foreground text-sm">
            No resorts match your filters
          </p>
          <p className="text-xs text-muted-foreground/70">
            Try adjusting your criteria
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-minimal">
      <div className="p-6 space-y-5">
        {resorts.map((resort, index) => (
          <div
            key={resort.sourceId}
            ref={(el) => {
              if (el) itemRefs.current[resort.sourceId] = el;
            }}
            className="animate-fade-in scroll-mt-7"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <ResortCard
              resort={resort}
              isResortHoveredOrSelected={
                hoveredResort === resort.sourceId || selectedResort === resort.sourceId
              }
              setHoveredResort={setHoveredResort}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResortList;
