import { Resort } from "@/types/resort";
import { ResortCard } from "./resortCard";

interface ResortListProps {
  resorts: Resort[];
  hoveredResortId: string | null;
  onHover: (id: string | null) => void;
}

export function ResortList({
  resorts,
  hoveredResortId,
  onHover,
}: ResortListProps) {
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
            key={resort.id}
            className="animate-fade-in"
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <ResortCard
              resort={resort}
              isHovered={hoveredResortId === resort.id}
              onHover={onHover}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
