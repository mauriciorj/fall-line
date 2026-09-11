"use client";

import Link from "next/link";
import { ArrowLeft, Mountain } from "lucide-react";
import { usePathname } from "next/navigation";
import Filter from "@/components/filter";
import LocationDropdown from "@/components/locationDropdown";
import { useFiltersContext } from "@/context/filtersContext";
import { useIsMobile } from "@/hooks/useMobile";
import Menu from "@/components/menu";
import { useLanguage } from "@/src/i18n";

const Header = () => {
  const { t } = useLanguage();
  const pathname = usePathname();
  const isMobile = useIsMobile();
  const {
    filters,
    setFilters,
    isFiltersActive,
    handleClearFilters,
    locations,
    selectedLocation,
    setLocation,
    userCoordinates,
  } = useFiltersContext();

  if (isMobile === undefined) {
    return (
      <header className="sticky top-0 z-50 bg-card border-b border-border">
        <div className="px-6 py-4 flex items-center">
          <Link href="/" aria-label={t("backHome")} className="text-primary">
            <Mountain className="w-10 h-10" />
          </Link>
        </div>
      </header>
    );
  }

  if (pathname.startsWith("/blog")) {
    return (
      <header className="sticky top-0 z-50 bg-card border-b border-border">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/blog" className="flex items-center gap-3 text-primary">
            <Mountain className="h-8 w-8" />
            <span className="font-serif text-2xl font-semibold">
              {t("blog")}
            </span>
          </Link>
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <ArrowLeft className="h-4 w-4" />
              {t("backToResorts")}
            </Link>
            <Menu />
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 bg-card border-b border-border">
      <div className="px-6 py-4 flex flex-row items-center justify-between">
        <Link
          href="/"
          aria-label={t("backHome")}
          className="flex items-center gap-2 text-primary"
        >
          <Mountain className="w-10 h-10" />
          <span className="text-2xl pt-2 font-bold tracking-wide uppercase">
            {!isMobile && t("appName")}
          </span>
        </Link>
        {isMobile ? (
          <div className="flex min-w-0 items-center gap-2">
            <Filter
              filters={filters}
              onChange={setFilters}
              isActive={isFiltersActive}
              onClear={handleClearFilters}
              locations={locations}
              selectedLocation={selectedLocation}
              setLocation={setLocation}
              canSortByDistance={Boolean(userCoordinates)}
            />
            <Menu />
          </div>
        ) : (
          <div className="flex flex-row">
            <LocationDropdown
              locations={locations}
              selectedLocation={selectedLocation}
              setLocation={setLocation}
            />
            <Filter
              filters={filters}
              onChange={setFilters}
              isActive={isFiltersActive}
              onClear={handleClearFilters}
              locations={locations}
              selectedLocation={selectedLocation}
              setLocation={setLocation}
              canSortByDistance={Boolean(userCoordinates)}
            />
            <Menu />
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
