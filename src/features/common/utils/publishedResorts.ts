import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { LocationOption, locationKey } from "@/types/location";

export type PublishedResort = {
  resortId: string;
  name?: string;
  country?: string;
  region?: string;
};

export type FooterResort = {
  resortId: string;
  name: string;
  country?: string;
  region?: string;
};

export type FooterGroup = { label: string; resorts: FooterResort[] };

// Grouped and sorted on the server so client rendering is deterministic.
export function groupResortsByRegion(
  resorts: PublishedResort[],
): FooterGroup[] {
  const groups = new Map<string, FooterResort[]>();
  for (const { resortId, name, country, region } of resorts) {
    const label = [region, country].filter(Boolean).join(", ") || "Other";
    groups.set(label, [
      ...(groups.get(label) ?? []),
      { resortId, name: name ?? resortId, country, region },
    ]);
  }

  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([label, items]) => ({
      label,
      resorts: items.sort((a, b) => a.name.localeCompare(b.name)),
    }));
}

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
