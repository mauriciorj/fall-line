import { Resort } from "@/types/resort";
import blueMountainImg from "@/assets/resort-blue-mountain.jpg";
import horseshoeImg from "@/assets/resort-horseshoe.jpg";
import mountStLouisImg from "@/assets/resort-mount-st-louis.jpg";
import searchmontImg from "@/assets/resort-searchmont.jpg";

export const resorts: Resort[] = [
  {
    id: "blue-mountain",
    name: "Blue Mountain Resort",
    image: blueMountainImg,
    runs: { green: 14, blue: 18, black: 10 },
    dayTicketPrice: 89,
    rentalPrice: 65,
    distance: 148,
    coordinates: { lat: 44.5015, lng: -80.3155 },
  },
  {
    id: "horseshoe",
    name: "Horseshoe Resort",
    image: horseshoeImg,
    runs: { green: 8, blue: 14, black: 7 },
    dayTicketPrice: 72,
    rentalPrice: 55,
    distance: 112,
    coordinates: { lat: 44.4742, lng: -79.6339 },
  },
  {
    id: "mount-st-louis",
    name: "Mount St. Louis Moonstone",
    image: mountStLouisImg,
    runs: { green: 12, blue: 20, black: 8 },
    dayTicketPrice: 78,
    rentalPrice: 58,
    distance: 125,
    coordinates: { lat: 44.5612, lng: -79.5467 },
  },
  {
    id: "searchmont",
    name: "Searchmont Resort",
    image: searchmontImg,
    runs: { green: 6, blue: 10, black: 5 },
    dayTicketPrice: 55,
    rentalPrice: 45,
    distance: 342,
    coordinates: { lat: 47.0167, lng: -84.1 },
  },
];
