"use client";

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useIsMobile } from "@/hooks/useMobile";
import { LocationOption, locationKey } from "@/types/location";
import { useLanguage } from "@/src/i18n";

const LocationDropdown = ({
  locations,
  selectedLocation,
  setLocation,
}: {
  locations: LocationOption[];
  selectedLocation: LocationOption | null;
  setLocation: (location: LocationOption) => void;
}) => {
  const { t } = useLanguage();
  const isMobile = useIsMobile();
  const selectedValue = selectedLocation ? locationKey(selectedLocation) : "";
  const groupedLocations = locations.reduce<
    Record<string, Record<string, LocationOption[]>>
  >((groups, location) => {
    groups[location.continent] ??= {};
    groups[location.continent][location.country] ??= [];
    groups[location.continent][location.country].push(location);
    return groups;
  }, {});

  return (
    <div className="flex flex-row items-center">
      {!isMobile && (
        <div>
          <span className="whitespace-nowrap text-foreground mr-2">
            {t("location")}
          </span>
        </div>
      )}
      <Select
        value={selectedValue}
        onValueChange={(value) => {
          const location = locations.find((item) => locationKey(item) === value);
          if (location) setLocation(location);
        }}
      >
        <SelectTrigger className="w-full bg-background min-w-[150px]">
          <SelectValue placeholder={t("selectLocation")} />
        </SelectTrigger>
        <SelectContent className="bg-background z-50">
          {Object.entries(groupedLocations).map(([continent, countries]) => (
            <SelectGroup key={continent}>
              <SelectLabel className="font-semibold text-foreground">
                {continent}
              </SelectLabel>
              {Object.entries(countries).map(([country, regions]) => (
                <SelectGroup key={`${continent}-${country}`}>
                  <SelectLabel className="pl-4 text-foreground">
                    - {country}
                  </SelectLabel>
                  {regions.map((location) => (
                    <SelectItem
                      key={locationKey(location)}
                      value={locationKey(location)}
                      className="pl-8"
                    >
                      -- {location.region}
                    </SelectItem>
                  ))}
                </SelectGroup>
              ))}
            </SelectGroup>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
};

export default LocationDropdown;
