"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const LocationDropdown = ({
  setLocation,
}: {
  setLocation: (location: string) => void;
}) => {
  return (
    <div className="flex flex-row items-center">
      <div>
        <span className="whitespace-nowrap font-medium text-foreground mr-2">
          Your Location
        </span>
      </div>
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
