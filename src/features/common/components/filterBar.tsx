import { cn } from "@/utils/utils";
import { Slider } from "@/components/ui/slider";
import { X } from "lucide-react";

export interface FilterState {
  sortBy: "distance" | "price";
  distanceRange: [number, number];
  difficulty: "beginner" | "intermediate" | "advanced" | null;
}

interface FilterBarProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  isActive: boolean;
  onClear: () => void;
}

export function FilterBar({
  filters,
  onChange,
  isActive,
  onClear,
}: FilterBarProps) {
  const updateFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    onChange({ ...filters, [key]: value });
  };

  return (
    <div className="px-6 py-4 border-b border-border bg-card/50">
      <div className="space-y-4">
        {/* Sort by - Primary control */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-foreground">Sort by</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => updateFilter("sortBy", "distance")}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-full transition-all duration-200",
                  filters.sortBy === "distance"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                Distance
              </button>
              <button
                onClick={() => updateFilter("sortBy", "price")}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-full transition-all duration-200",
                  filters.sortBy === "price"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                Price
              </button>
            </div>
          </div>

          {isActive && (
            <button
              onClick={onClear}
              className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-3 h-3" />
              Clear
            </button>
          )}
        </div>

        {/* Distance slider */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <span className="text-[10px] uppercase tracking-wide text-muted-foreground/70">
              Distance
            </span>
            <span className="text-[11px] text-muted-foreground">
              {filters.distanceRange[0]}–{filters.distanceRange[1]} km
            </span>
          </div>
          <Slider
            value={filters.distanceRange}
            onValueChange={(value: [number, number]) =>
              updateFilter("distanceRange", value)
            }
            min={0}
            max={400}
            step={10}
            className="filter-slider"
          />
        </div>

        {/* Terrain toggles */}
        <div className="flex items-center gap-3">
          <span className="text-[10px] uppercase tracking-wide text-muted-foreground/70">
            Terrain
          </span>
          <div className="flex items-center gap-1.5">
            <DifficultyToggle
              label="Beginner-friendly"
              color="green"
              isActive={filters.difficulty === "beginner"}
              onClick={() =>
                updateFilter(
                  "difficulty",
                  filters.difficulty === "beginner" ? null : "beginner"
                )
              }
            />
            <DifficultyToggle
              label="Balanced terrain"
              color="blue"
              isActive={filters.difficulty === "intermediate"}
              onClick={() =>
                updateFilter(
                  "difficulty",
                  filters.difficulty === "intermediate" ? null : "intermediate"
                )
              }
            />
            <DifficultyToggle
              label="Expert-heavy"
              color="black"
              isActive={filters.difficulty === "advanced"}
              onClick={() =>
                updateFilter(
                  "difficulty",
                  filters.difficulty === "advanced" ? null : "advanced"
                )
              }
            />
          </div>
        </div>

        {/* Timestamp */}
        <div className="pt-1">
          <span className="text-[10px] text-muted-foreground/50">
            Prices last updated Feb 2026
          </span>
        </div>
      </div>
    </div>
  );
}

interface DifficultyToggleProps {
  label: string;
  color: "green" | "blue" | "black";
  isActive: boolean;
  onClick: () => void;
}

function DifficultyToggle({
  label,
  color,
  isActive,
  onClick,
}: DifficultyToggleProps) {
  const colorClasses = {
    green: {
      dot: "bg-run-green",
      active: "ring-run-green/30 bg-run-green/10",
    },
    blue: {
      dot: "bg-run-blue",
      active: "ring-run-blue/30 bg-run-blue/10",
    },
    black: {
      dot: "bg-run-black",
      active: "ring-run-black/20 bg-run-black/5",
    },
  };

  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 px-2 py-1 rounded-full transition-all duration-200 text-[11px]",
        isActive
          ? `${colorClasses[color].active} ring-1 text-foreground`
          : "text-muted-foreground/70 hover:text-muted-foreground"
      )}
    >
      <span
        className={cn("w-1.5 h-1.5 rounded-full", colorClasses[color].dot)}
      />
      {label}
    </button>
  );
}
