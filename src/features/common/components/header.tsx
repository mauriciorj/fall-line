"use client";

import Link from "next/link";
import { Mountain } from "lucide-react";
import Filter from "@/components/filter";
import LocationDropdown from "@/components/locationDropdown";
import { useFiltersContext } from "@/context/filtersContext";
import { useIsMobile } from "@/hooks/useMobile";
import Menu from "@/components/menu";

const Header = () => {
  const isMobile = useIsMobile();

  const { filters, setFilters, isFiltersActive, handleClearFilters } =
    useFiltersContext();

  return (
    <header className="sticky top-0 z-50 bg-card border-b border-border">
      <div className="px-6 py-4 flex flex-row items-center justify-between">
        <Link
          href="/"
          aria-label="Go to Ontario Ski Guide home"
          className="flex items-center gap-2 text-primary"
        >
          <Mountain className="w-10 h-10" />
          <span className="text-2xl pt-2 font-bold tracking-wide uppercase">
            {!isMobile && "Ontario Ski Guide"}
          </span>
        </Link>
        {isMobile ? (
          <>
            <Filter
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
            <Filter
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
};

export default Header;
