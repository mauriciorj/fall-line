import { StaticImageData } from "next/image";

export interface Resort {
  address: string;
  coordinates?: {
    lat: number;
    lng: number;
  };
  crawlerUrls?: {
    dayTicketPriceUrl?: string;
    equipmentRentalsUrl?: string;
    hoursOfOperationUrl?: string;
    lessonsUrl?: string;
    trackConditionsUrl?: string;
    tubbing?: string;
  };
  dayTicketPrice: number;
  email: string;
  googleMapsUrl: string;
  hasAccommodations: boolean;
  hasCrossCountry: boolean;
  hasLessons: boolean;
  hasSnowshoeing: boolean;
  hasSpa: boolean;
  hasTubing: boolean;
  hasZipline?: boolean;
  hoursOfOperation: {
    sunday: string;
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
  };
  id: string;
  image: StaticImageData | string;
  lessonsPrice: number;
  name: string;
  phone: string;
  rating: number;
  snowBoardRentalPrice: number;
  skiRentalPrice: number;
  runs: {
    black: number;
    blue: number;
    doubleBlack: number;
    freeStyle?: number;
    green: number;
  };
  ticketUrl?: string;
  tollFree?: string;
  trackConditions?: {
    name: string;
    condition: string;
    difficulty: "black" | "blue" | "double-black" | "free-style" | "green";
  }[];
  trailMap: StaticImageData | string;
  tubbingPrice?: number;
  website: string;
}
