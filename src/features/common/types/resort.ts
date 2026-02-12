import { StaticImageData } from "next/image";

export interface Resort {
  address: string;
  coordinates: {
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
  hasLessons: boolean;
  hasTubing: boolean;
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
  image: StaticImageData;
  lessonsPrice: number;
  name: string;
  phone: string;
  rating: number;
  snowBoardRentalPrice: number;
  skiRentalPrice: number;
  runs: {
    green: number;
    blue: number;
    black: number;
  };
  ticketUrl?: string;
  tollFree?: string;
  trackConditions?: {
    name: string;
    condition: string;
    difficulty: "black" | "blue" | "double-black" | "green";
  }[];
  trailMap: StaticImageData | string;
  tubbingPrice?: number;
  website: string;
}
