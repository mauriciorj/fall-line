import { Mountain } from "lucide-react";
import { FilterPopover, FilterState } from "./filterPopover";

interface HeroSectionProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  isFiltersActive: boolean;
  onClearFilters: () => void;
}

export function HeroSection({
  filters,
  onFiltersChange,
  isFiltersActive,
  onClearFilters,
}: HeroSectionProps) {
  return (
    <header className="bg-card border-b border-border">
      <div className="px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-primary">
          <Mountain className="w-5 h-5" />
          <span className="text-sm font-medium tracking-wide uppercase">
            Ontario Ski Guide
          </span>
        </div>
        <FilterPopover
          filters={filters}
          onChange={onFiltersChange}
          isActive={isFiltersActive}
          onClear={onClearFilters}
        />
      </div>
    </header>
  );
}
