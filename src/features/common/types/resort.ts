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
  hasLessons: boolean;
  hasTubing: boolean;
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
  trailMap: StaticImageData;
  tubingPrice: number;
  website: string;
}
