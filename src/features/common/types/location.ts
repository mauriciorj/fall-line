export interface LocationOption {
  continent: string;
  country: string;
  region: string;
}

export const DEFAULT_LOCATION = { country: "Canada", region: "Ontario" };

export function locationKey(location: LocationOption): string {
  return [location.continent, location.country, location.region].join("|");
}

export function findDefaultLocation(
  locations: LocationOption[],
): LocationOption | undefined {
  return (
    locations.find(
      (location) =>
        location.country === DEFAULT_LOCATION.country &&
        location.region === DEFAULT_LOCATION.region,
    ) ?? locations[0]
  );
}

export function locationLabel(location: LocationOption): string {
  return [location.region, location.country, location.continent].join(", ");
}
