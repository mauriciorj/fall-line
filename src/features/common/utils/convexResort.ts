import { Resort } from "@/types/resort";

type DbResort = Partial<Resort> & {
  id?: string;
  location?: {
    address?: string;
  };
  rate?: number;
  contact?: string;
};

const emptyHours = {
  sunday: "",
  monday: "",
  tuesday: "",
  wednesday: "",
  thursday: "",
  friday: "",
  saturday: "",
};

const emptyRuns = {
  black: 0,
  blue: 0,
  doubleBlack: 0,
  freeStyle: 0,
  green: 0,
};

export function toResort(value: unknown): Resort | null {
  if (!value || typeof value !== "object") return null;

  const document = value as DbResort;
  if (!document.id || !document.name) return null;

  return {
    ...document,
    id: document.id,
    name: document.name,
    address: document.address ?? document.location?.address ?? "",
    coordinates: document.coordinates,
    dayTicketPrice: document.dayTicketPrice ?? document.rate ?? 0,
    email: document.email ?? "",
    googleMapsUrl: document.googleMapsUrl ?? "",
    hasAccommodations: document.hasAccommodations ?? false,
    hasCrossCountry: document.hasCrossCountry ?? false,
    hasLessons: document.hasLessons ?? false,
    hasSnowshoeing: document.hasSnowshoeing ?? false,
    hasSpa: document.hasSpa ?? false,
    hasTubing: document.hasTubing ?? false,
    hoursOfOperation: document.hoursOfOperation ?? emptyHours,
    image: document.image ?? "/assets/lakeridge-ski-resort.webp",
    lessonsPrice: document.lessonsPrice ?? 0,
    phone: document.phone ?? document.contact ?? "",
    rating: document.rating ?? 0,
    runs: document.runs ?? emptyRuns,
    skiRentalPrice: document.skiRentalPrice ?? 0,
    snowBoardRentalPrice: document.snowBoardRentalPrice ?? 0,
    trailMap: document.trailMap ?? "/assets/lakeridge-ski-resort-trail-map.jpg",
    website: document.website ?? "",
  };
}
