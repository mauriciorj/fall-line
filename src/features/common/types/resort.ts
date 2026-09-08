import { StaticImageData } from "next/image";

export interface ResortHourRow {
  day: string;
  time: string;
}

export interface ResortHourActivity {
  name: string;
  hours: ResortHourRow[];
}

export interface ResortHourSection {
  name: string;
  activities?: ResortHourActivity[];
  hours?: ResortHourRow[];
}

export interface Resort {
  address: string;
  coordinates?: {
    lat: number;
    lng: number;
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
  resortId: string;
  continent?: string;
  country?: string;
  region?: string;
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
