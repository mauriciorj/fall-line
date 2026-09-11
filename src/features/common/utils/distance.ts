import { Coordinates } from "@/types/resort";

const EARTH_RADIUS_KM = 6371;

export function calculateDistanceKm(
  first: Coordinates,
  second: Coordinates,
) {
  const toRadians = (degrees: number) => (degrees * Math.PI) / 180;
  const latitudeDelta = toRadians(second.lat - first.lat);
  const longitudeDelta = toRadians(second.lng - first.lng);
  const firstLatitude = toRadians(first.lat);
  const secondLatitude = toRadians(second.lat);
  const haversine =
    Math.sin(latitudeDelta / 2) ** 2 +
    Math.sin(longitudeDelta / 2) ** 2 *
      Math.cos(firstLatitude) *
      Math.cos(secondLatitude);

  return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(haversine));
}
