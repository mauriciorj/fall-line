import { useState } from "react";
import { cn } from "@/utils/utils";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { SlidersHorizontal, X } from "lucide-react";

export interface FilterState {
  sortBy: "distance" | "price";
  distanceRange: [number, number];
  difficulty: "beginner" | "intermediate" | "advanced" | null;
}

interface FilterPopoverProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  isActive: boolean;
  onClear: () => void;
}

export function FilterPopover({
  filters,
  onChange,
  isActive,
  onClear,
}: FilterPopoverProps) {
  const [open, setOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState<FilterState>(filters);

  const updateLocalFilter = <K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    setLocalFilters({ ...localFilters, [key]: value });
  };

  const handleApply = () => {
    onChange(localFilters);
    setOpen(false);
  };

  const handleClear = () => {
    const clearedFilters: FilterState = {
      sortBy: "distance",
      distanceRange: [0, 250],
      difficulty: null,
    };
    setLocalFilters(clearedFilters);
    onClear();
  };

  const handleOpenChange = (isOpen: boolean) => {
    setOpen(isOpen);
    if (isOpen) {
      setLocalFilters(filters);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger
        asChild
        className="xs:relative md:fixed top-3 left-[calc(50%-20px)] z-50"
      >
        <button
          className={cn(
            "cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200",
            isActive
              ? "bg-primary text-primary-foreground shadow-sm"
              : "bg-primary text-primary-foreground hover:text-foreground hover:bg-muted"
          )}
        >
          <SlidersHorizontal className="w-4 h-4" />
          Filters
          {isActive && (
            <span className="w-1.5 h-1.5 rounded-full bg-primary-foreground" />
          )}
        </button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="font-serif text-xl">
            Filter Resorts
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Sort by */}
          <div className="space-y-3">
            <span className="text-xs font-medium text-foreground">Sort by</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => updateLocalFilter("sortBy", "distance")}
                className={cn(
                  "flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  localFilters.sortBy === "distance"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                Distance
              </button>
              <button
                onClick={() => updateLocalFilter("sortBy", "price")}
                className={cn(
                  "flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  localFilters.sortBy === "price"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                Price
              </button>
            </div>
          </div>

          {/* Distance slider */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-foreground">
                Distance
              </span>
              <span className="text-sm text-muted-foreground">
                {localFilters.distanceRange[0]}–{localFilters.distanceRange[1]}{" "}
                km
              </span>
            </div>
            <Slider
              value={localFilters.distanceRange}
              onValueChange={(value: [number, number]) =>
                updateLocalFilter("distanceRange", value)
              }
              min={0}
              max={400}
              step={10}
              className="filter-slider"
            />
          </div>

          {/* Terrain toggles */}
          <div className="space-y-3">
            <span className="text-xs font-medium text-foreground">Terrain</span>
            <div className="flex flex-wrap gap-2">
              <DifficultyToggle
                label="Beginner-friendly"
                color="green"
                isActive={localFilters.difficulty === "beginner"}
                onClick={() =>
                  updateLocalFilter(
                    "difficulty",
                    localFilters.difficulty === "beginner" ? null : "beginner"
                  )
                }
              />
              <DifficultyToggle
                label="Balanced terrain"
                color="blue"
                isActive={localFilters.difficulty === "intermediate"}
                onClick={() =>
                  updateLocalFilter(
                    "difficulty",
                    localFilters.difficulty === "intermediate"
                      ? null
                      : "intermediate"
                  )
                }
              />
              <DifficultyToggle
                label="Expert-heavy"
                color="black"
                isActive={localFilters.difficulty === "advanced"}
                onClick={() =>
                  updateLocalFilter(
                    "difficulty",
                    localFilters.difficulty === "advanced" ? null : "advanced"
                  )
                }
              />
            </div>
          </div>

          {/* Timestamp */}
          <div className="pt-2 border-t border-border">
            <span className="text-[10px] text-muted-foreground/50">
              Prices last updated Feb 2026
            </span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-2">
          {isActive && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="text-muted-foreground"
            >
              <X className="w-3.5 h-3.5 mr-1.5" />
              Clear all
            </Button>
          )}
          <div className="flex-1" />
          <Button onClick={handleApply} className="px-6">
            Apply
          </Button>
        </div>
      </DialogContent>
    </Dialog>
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
        "flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 text-sm",
        isActive
          ? `${colorClasses[color].active} ring-1 text-foreground`
          : "bg-muted/30 text-muted-foreground hover:text-foreground hover:bg-muted/50"
      )}
    >
      <span className={cn("w-2 h-2 rounded-full", colorClasses[color].dot)} />
      {label}
    </button>
  );
}
