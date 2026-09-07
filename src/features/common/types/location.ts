export interface LocationOption {
  continent: string;
  country: string;
  region: string;
}

export function locationKey(location: LocationOption): string {
  return [location.continent, location.country, location.region].join("|");
}

export function locationLabel(location: LocationOption): string {
  return [location.region, location.country, location.continent].join(", ");
}
