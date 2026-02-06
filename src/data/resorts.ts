import { Resort } from "@/types/resort";

import lakeridgeSkiResortImg from "@/assets/lakeridge-ski-resort.webp";
import lakeridgeSkiResortTrailmap from "@/assets/lakeridge-ski-resort-trail-map.jpg";

export const resorts: Resort[] = [
  {
    address: "790 Chalk Lake Rd, Uxbridge, ON L9P 1R4",
    coordinates: { lat: 44.04597402067868, lng: -79.06573258279116 },
    dayTicketPrice: 67.47, // not update
    distance: 148, // not update
    email: "josborne@lakeridgeresort.ca",
    id: "Lakeridge Ski Resort",
    image: lakeridgeSkiResortImg, // not update
    hasLessons: true,
    hasTubing: true,
    lessonsPrice: 123.12,
    name: "Lakeridge Ski Resort",
    phone: "(905) 644-7467",
    rating: 4.3,
    skiRentalPrice: 55,
    snowBoardRentalPrice: 66,
    runs: { green: 6, blue: 4, black: 7 },
    trailMap: lakeridgeSkiResortTrailmap,
    tubingPrice: 30,
    website: "http://www.ski-lakeridge.com/",
  },
  {
    address: "1220 Lake Ridge Rd, Uxbridge, ON L9L 1V7",
    coordinates: { lat: 44.02314189216543, lng: -79.04741821453386 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Dagmar Ski Resort",
    image: lakeridgeSkiResortImg, // not update
    name: "Dagmar Ski Resort",
    phone: "(905) 644-7467", // not update
    rating: 4.2,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://www.skidagmar.com/",
  },
  {
    address: "4098 Regional Road 9, Orono, ON L0B 1M0",
    coordinates: { lat: 44.06901178082853, lng: -78.5731371079196 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Brimacombe",
    image: lakeridgeSkiResortImg, // not update
    name: "Brimacombe",
    phone: "(905) 644-7467", // not update
    rating: 4.2,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://www.skidagmar.com/",
  },
  {
    address: "2632 Vespra Valley Rd, Minesing, ON L9X 0G8",
    coordinates: { lat: 44.46119110037171, lng: -79.7835534199466 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Snow Valley Ski Resort",
    image: lakeridgeSkiResortImg, // not update
    name: "Snow Valley Ski Resort",
    phone: "(705) 721-7669", // not update
    rating: 4.3,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://www.skisnowvalley.com/",
  },
  {
    address: "1101 Horseshoe Valley Rd W, Barrie, ON L4M 4Y8",
    coordinates: { lat: 44.59429988048484, lng: -79.68125046375664 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Horseshoe Valley Resort",
    image: lakeridgeSkiResortImg, // not update
    name: "Horseshoe Valley Resort",
    phone: "(705) 721-7669", // not update
    rating: 4.1,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://horseshoeresort.com/",
  },
  {
    address: "190 Gord Canning Dr, The Blue Mountains, ON L9Y 1C2",
    coordinates: { lat: 44.55091707586931, lng: -80.31056434810445 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Blue Mountain",
    image: lakeridgeSkiResortImg, // not update
    name: "Blue Mountain",
    phone: "(705) 721-7669", // not update
    rating: 4.4,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "https://www.bluemountain.ca/",
  },
  {
    address: "5234 Kelso Rd, Milton, ON L9T 2X7",
    coordinates: { lat: 43.55418055900003, lng: -79.93414693948958 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Glen Eden",
    image: lakeridgeSkiResortImg, // not update
    name: "Glen Eden",
    phone: "(705) 721-7669", // not update
    rating: 4.2,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "https://gleneden.on.ca/",
  },
  {
    address: "396 Morrison Road, Kitchener, ON N2A 2Z6",
    coordinates: { lat: 43.50150295771778, lng: -80.42101373098909 },
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Chicopee",
    image: lakeridgeSkiResortImg, // not update
    name: "Chicopee",
    phone: "(705) 721-7669", // not update
    rating: 4.2,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://www.discoverchicopee.com/",
  },
  {
    address: "17431 Mississauga Rd, Caledon, ON L7K 0E9",
    coordinates: { lat: 43.856306447577786, lng: -80.00755054550318 }, //
    dayTicketPrice: 72, // not update
    distance: 112, // not update
    id: "Caledon Ski Club",
    image: lakeridgeSkiResortImg, // not update
    name: "Caledon Ski Club",
    phone: "(705) 721-7669", // not update
    rating: 4.6,
    rentalPrice: 55, // not update
    runs: { green: 8, blue: 14, black: 7 }, // not update
    website: "http://caledonskiclub.com/",
  },
];
