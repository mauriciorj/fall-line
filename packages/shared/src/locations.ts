import type { Resort } from "./types/resort";
import {
  getCountryPath,
  getRegionPath,
  toAssetSegment,
} from "./resorts";

export type RegionGroup<Image = string> = {
  country: string;
  region: string;
  countrySlug: string;
  regionSlug: string;
  path: string;
  resorts: Resort<Image>[];
};

export type CountryGroup<Image = string> = {
  country: string;
  countrySlug: string;
  path: string;
  regions: RegionGroup<Image>[];
};

const byName = (a: { name: string }, b: { name: string }) =>
  a.name.localeCompare(b.name);

// Resorts without a country/region can't have a hub page and are dropped here.
export function groupByRegion<Image>(resorts: Resort<Image>[]): RegionGroup<Image>[] {
  const groups = new Map<string, RegionGroup<Image>>();
  for (const resort of resorts) {
    if (!resort.country || !resort.region) continue;
    const path = getRegionPath(resort.country, resort.region);
    const group = groups.get(path) ?? {
      country: resort.country,
      region: resort.region,
      countrySlug: toAssetSegment(resort.country),
      regionSlug: toAssetSegment(resort.region),
      path,
      resorts: [],
    };
    group.resorts.push(resort);
    groups.set(path, group);
  }

  return [...groups.values()]
    .map((group) => ({ ...group, resorts: group.resorts.sort(byName) }))
    .sort(
      (a, b) =>
        a.country.localeCompare(b.country) || a.region.localeCompare(b.region),
    );
}

export function groupByCountry<Image>(resorts: Resort<Image>[]): CountryGroup<Image>[] {
  const countries = new Map<string, CountryGroup<Image>>();
  for (const region of groupByRegion(resorts)) {
    const path = getCountryPath(region.country);
    const group = countries.get(path) ?? {
      country: region.country,
      countrySlug: region.countrySlug,
      path,
      regions: [],
    };
    group.regions.push(region);
    countries.set(path, group);
  }
  return [...countries.values()];
}

export function regionStats<Image>(resorts: Resort<Image>[]) {
  const prices = resorts
    .map((resort) => resort.dayTicketPrice)
    .filter((price) => price > 0);
  const totalRuns = resorts.reduce(
    (sum, { runs }) =>
      sum +
      runs.green +
      runs.blue +
      runs.black +
      runs.doubleBlack +
      (runs.freeStyle ?? 0),
    0,
  );

  const updatedAt = resorts.reduce<number | null>(
    (latest, resort) =>
      resort.updatedAt ? Math.max(latest ?? 0, resort.updatedAt) : latest,
    null,
  );

  return {
    count: resorts.length,
    minPrice: prices.length ? Math.min(...prices) : null,
    maxPrice: prices.length ? Math.max(...prices) : null,
    totalRuns,
    withTubing: resorts.filter((resort) => resort.hasTubing).length,
    withLessons: resorts.filter((resort) => resort.hasLessons).length,
    updatedAt,
  };
}
