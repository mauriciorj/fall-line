"use client";

import { useState } from "react";
import { cn } from "@/utils/utils";
// import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useIsMobile } from "@/hooks/useMobile";
import { SlidersHorizontal, X } from "lucide-react";
import LocationDropdown from "../locationDropdown";
import { LocationOption } from "@/types/location";
import { useLanguage } from "@/src/i18n";

import Toggle from "@/components/filter/toggle";

export interface FilterState {
  sortBy: "price" | "rating" | "distance";
  distanceRange: [number, number];
  activities: {
    accommodations: boolean;
    crosscountry: boolean;
    lessons: boolean;
    snowshoeing: boolean;
    spa: boolean;
    tubbing: boolean;
  };
}

interface FilterProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  isActive: boolean;
  onClear: () => void;
  locations: LocationOption[];
  selectedLocation: LocationOption | null;
  setLocation: (location: LocationOption) => void;
  canSortByDistance: boolean;
}

const Filter = ({
  filters,
  onChange,
  isActive,
  onClear,
  locations,
  selectedLocation,
  setLocation,
  canSortByDistance,
}: FilterProps) => {
  const { t } = useLanguage();
  const isMobile = useIsMobile();

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
      sortBy: "price",
      distanceRange: [0, 250],
      activities: {
        accommodations: false,
        crosscountry: false,
        lessons: false,
        snowshoeing: false,
        spa: false,
        tubbing: false,
      },
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
        className={
          isMobile
            ? "relative z-50"
            : "xs:relative md:fixed top-4 left-[calc(50%-20px)] z-50"
        }
      >
        <Button
          variant="outline"
          className={cn(
            "cursor-pointer flex items-center gap-2 px-4 py-3 rounded-full font-medium transition-all duration-200 border-primary text-primary",
            isActive ? "shadow-sm" : "hover:text-primary hover:bg-muted"
          )}
        >
          <SlidersHorizontal className="w-4 h-4" />
          {t("filters")}
          {isActive && (
            <span className="w-1.5 h-1.5 rounded-full bg-primary-foreground" />
          )}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="font-serif text-xl">
            {t("filterResorts")}
          </DialogTitle>
        </DialogHeader>

        {isMobile && (
          <div className="space-y-3">
            <span className="text-xs font-medium text-foreground">
              {t("location")}
            </span>
            <LocationDropdown
              locations={locations}
              selectedLocation={selectedLocation}
              setLocation={setLocation}
            />
          </div>
        )}

        <div className="space-y-6 py-4">
          {/* Sort by */}
          <div className="space-y-3">
            <span className="text-xs font-medium text-foreground">{t("sortBy")}</span>
            <div className="flex items-center gap-2">
              <button
                onClick={() => updateLocalFilter("sortBy", "price")}
                className={cn(
                  "flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  localFilters.sortBy === "price"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {t("liftPrice")}
              </button>
              <button
                onClick={() => updateLocalFilter("sortBy", "rating")}
                className={cn(
                  "flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                  localFilters.sortBy === "rating"
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                )}
              >
                {t("rating")}
              </button>
              {canSortByDistance && (
                <button
                  onClick={() => updateLocalFilter("sortBy", "distance")}
                  className={cn(
                    "flex-1 px-4 py-2.5 text-sm font-medium rounded-lg transition-all duration-200",
                    localFilters.sortBy === "distance"
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "bg-muted/50 text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  {t("distance")}
                </button>
              )}
            </div>
          </div>

          {/* Distance slider */}
          {/* <div className="space-y-3">
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
          </div> */}

          <div className="space-y-3">
            <span className="text-xs font-medium text-foreground">
              {t("activities")}
            </span>
            <div className="flex flex-wrap gap-2">
              <Toggle
                label={t("accommodations")}
                color="green"
                isActive={localFilters.activities.accommodations}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    accommodations: !localFilters.activities.accommodations,
                  })
                }
              />
              <Toggle
                label={t("crossCountry")}
                color="green"
                isActive={localFilters.activities.crosscountry}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    crosscountry: !localFilters.activities.crosscountry,
                  })
                }
              />
              <Toggle
                label={t("lessons")}
                color="green"
                isActive={localFilters.activities.lessons}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    lessons: !localFilters.activities.lessons,
                  })
                }
              />
              <Toggle
                label={t("snowshoeing")}
                color="green"
                isActive={localFilters.activities.snowshoeing}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    snowshoeing: !localFilters.activities.snowshoeing,
                  })
                }
              />
              <Toggle
                label={t("spa")}
                color="green"
                isActive={localFilters.activities.spa}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    spa: !localFilters.activities.spa,
                  })
                }
              />
              <Toggle
                label={t("tubbing")}
                color="green"
                isActive={localFilters.activities.tubbing}
                onClick={() =>
                  updateLocalFilter("activities", {
                    ...localFilters.activities,
                    tubbing: !localFilters.activities.tubbing,
                  })
                }
              />
            </div>
          </div>

          {/* Timestamp */}
          <div className="pt-2 border-t border-border">
            <span className="text-[10px] text-muted-foreground/50">
              {t("pricesUpdated")}
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
              {t("clearAll")}
            </Button>
          )}
          <div className="flex-1" />
          <Button onClick={handleApply} className="px-6">
            {t("apply")}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Filter;
