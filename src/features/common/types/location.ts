export interface LocationOption {
  continent: string;
  country: string;
  region: string;
}

export const DEFAULT_LOCATION = { country: "Canada", region: "Ontario" };

export function locationKey(location: LocationOption): string {
  return [location.continent, location.country, location.region].join("|");
}

// Geocoder output -> known location: exact region, then the country's
// "Unknown" bucket, then any location in that country.
export function matchLocation(
  locations: LocationOption[],
  country: string,
  region: string,
): LocationOption | undefined {
  const normalizedCountry = country.toLowerCase();
  const normalizedRegion = region.toLowerCase();
  return (
    locations.find(
      (location) =>
        location.country.toLowerCase() === normalizedCountry &&
        location.region.toLowerCase() === normalizedRegion,
    ) ??
    locations.find(
      (location) =>
        location.country.toLowerCase() === normalizedCountry &&
        location.region.toLowerCase() === "unknown",
    ) ??
    locations.find(
      (location) => location.country.toLowerCase() === normalizedCountry,
    )
  );
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
