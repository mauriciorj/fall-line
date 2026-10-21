import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { LocationOption, locationKey } from "@/types/location";

export type PublishedResort = {
  resortId: string;
  country?: string;
  region?: string;
};

// Server-only. Uses the existing public queries so no new Convex functions
// have to be deployed: distinct locations -> published resorts per location.
export async function listPublishedResorts(): Promise<PublishedResort[]> {
  const resortLocations = await fetchQuery(api.resorts.listLocations);
  const locations = new Map<string, LocationOption>();
  for (const { continent, country, region } of resortLocations) {
    if (!continent || !country || !region) continue;
    const location = { continent, country, region };
    locations.set(locationKey(location), location);
  }

  const resortsByLocation = await Promise.all(
    [...locations.values()].map((location) =>
      fetchQuery(api.resorts.list, location),
    ),
  );

  return resortsByLocation.flat();
}
