"use client";

import { Mountain } from "lucide-react";
import { FilterPopover } from "./filterPopover";
import LocationDropdown from "./locationDropdown";
import useFilters from "@/hooks/useFilters";
import { useIsMobile } from "@/hooks/useMobile";
import Menu from "@/components/menu";

export function Header() {
  const isMobile = useIsMobile();

  const { filters, setFilters, isFiltersActive, handleClearFilters } =
    useFilters();

  return (
    <header className="sticky top-0 z-50 bg-card border-b border-border">
      <div className="px-6 py-4 flex flex-row items-center justify-between">
        <div className="flex items-center gap-2 text-primary">
          <Mountain className="w-10 h-10" />
          <span className="text-2xl pt-2 font-bold tracking-wide uppercase">
            {!isMobile && "Ontario Ski Guide"}
          </span>
        </div>
        {isMobile ? (
          <>
            <FilterPopover
              filters={filters}
              onChange={setFilters}
              isActive={isFiltersActive}
              onClear={handleClearFilters}
              setLocation={() => {}}
            />
            <Menu />
          </>
        ) : (
          <div className="flex flex-row">
            <LocationDropdown setLocation={() => {}} />
            <FilterPopover
              filters={filters}
              onChange={setFilters}
              isActive={isFiltersActive}
              onClear={handleClearFilters}
              setLocation={() => {}}
            />
            <Menu />
          </div>
        )}
      </div>
    </header>
  );
}
