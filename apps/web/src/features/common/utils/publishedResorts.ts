import { cache } from "react";
import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { LocationOption, locationKey } from "@/types/location";
import type { Resort } from "@/types/resort";
import { toResort } from "@/utils/convexResort";
import { groupByRegion } from "@/utils/locationGroups";

// Server-only. Uses the existing public queries so no new Convex functions
// have to be deployed: distinct locations -> published resorts per location.
// Memoized per request so callers can share one fetch.
export const listPublishedResorts = cache(async (): Promise<Resort[]> => {
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

  return resortsByLocation
    .flat()
    .map((resort) => toResort(resort))
    .filter((resort): resort is Resort => resort !== null);
});

export type FooterResort = {
  resortId: string;
  name: string;
  country?: string;
  region?: string;
};

export type FooterGroup = {
  label: string;
  path: string;
  resorts: FooterResort[];
};

// Grouped and sorted on the server so client rendering is deterministic.
export function groupResortsByRegion(resorts: Resort[]): FooterGroup[] {
  return groupByRegion(resorts).map((group) => ({
    label: `${group.region}, ${group.country}`,
    path: group.path,
    resorts: group.resorts.map(({ resortId, name, country, region }) => ({
      resortId,
      name: name || resortId,
      country,
      region,
    })),
  }));
}
