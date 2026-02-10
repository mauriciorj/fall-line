import { StaticImageData } from "next/image";

export interface Resort {
  address: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  dayTicketPrice: number;
  distance: number; // in km
  email: string;
  googleMapsUrl: string;
  hasLessons: boolean;
  hasTubing: boolean;
  hoursOfOperation: {
    monday: string;
    tuesday: string;
    wednesday: string;
    thursday: string;
    friday: string;
    saturday: string;
    sunday: string;
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
  trackConditions?: {
    name: string;
    condition: string;
    difficulty: "black" | "blue" | "double-black" | "green";
  }[];
  trailMap: StaticImageData | string;
  tubbingPrice?: number;
  website: string;
}
