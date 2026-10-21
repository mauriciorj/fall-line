import type { FilterState } from "@/components/filter";
import type { Coordinates, Resort } from "@/types/resort";
import { calculateDistanceKm } from "@/utils/distance";

export const defaultFilters: FilterState = {
  sortBy: "price",
  distanceRange: [0, 250],
  activities: {
    accommodations: false,
    crosscountry: false,
    lessons: false,
    iceSkating: false,
    snowshoeing: false,
    spa: false,
    tubbing: false,
  },
};

export function applyResortFilters(
  resorts: Resort[],
  filters: FilterState,
  userCoordinates: Coordinates | null,
): Resort[] {
  const result = resorts.filter((resort) => {
    // Activities filter
    const { activities } = filters;

    if (activities.accommodations && !resort.hasAccommodations) return false;
    if (activities.crosscountry && !resort.hasCrossCountry) return false;
    if (activities.lessons && !resort.hasLessons) return false;
    if (activities.iceSkating && !resort.hasIceSkate) return false;
    if (activities.snowshoeing && !resort.hasSnowshoeing) return false;
    if (activities.spa && !resort.hasSpa) return false;
    if (activities.tubbing && !resort.hasTubing) return false;

    return true;
  });

  // Sort
  return result.sort((a, b) => {
    if (filters.sortBy === "rating") {
      return b.rating - a.rating;
    }

    if (filters.sortBy === "distance" && userCoordinates) {
      const distanceA = a.coordinates
        ? calculateDistanceKm(userCoordinates, a.coordinates)
        : Number.POSITIVE_INFINITY;
      const distanceB = b.coordinates
        ? calculateDistanceKm(userCoordinates, b.coordinates)
        : Number.POSITIVE_INFINITY;
      return distanceA - distanceB;
    }

    return a.dayTicketPrice - b.dayTicketPrice;
  });
}
