import { StaticImageData } from "next/image";

export interface Resort {
  id: string;
  name: string;
  image: StaticImageData;
  runs: {
    green: number;
    blue: number;
    black: number;
  };
  dayTicketPrice: number;
  rentalPrice: number;
  distance: number; // in km
  coordinates: {
    lat: number;
    lng: number;
  };
}
