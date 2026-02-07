"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useIsMobile } from "@/hooks/useMobile";

const LocationDropdown = ({
  setLocation,
}: {
  setLocation: (location: string) => void;
}) => {
  const isMobile = useIsMobile();
  return (
    <div className="flex flex-row items-center">
      {!isMobile && (
        <div>
          <span className="whitespace-nowrap text-foreground mr-2">
            Current Location
          </span>
        </div>
      )}
      <Select
        value="ontario"
        onValueChange={(value: string) => setLocation(value)}
      >
        <SelectTrigger className="w-full bg-background min-w-[150px]">
          <SelectValue placeholder="Select your location" />
        </SelectTrigger>
        <SelectContent className="bg-background z-50">
          <SelectItem value="ontario">Ontario</SelectItem>
          {/* <SelectItem value="british-columbia">British Columbia</SelectItem>
          <SelectItem value="quebec">Quebec</SelectItem> */}
        </SelectContent>
      </Select>
    </div>
  );
};

export default LocationDropdown;
