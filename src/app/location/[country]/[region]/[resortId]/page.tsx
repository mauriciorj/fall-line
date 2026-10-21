import { notFound } from "next/navigation";
import {
  fetchQuery,
  preloadQuery,
  preloadedQueryResult,
} from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import ResortDetail from "@/src/features/place/component/resortDetail";
import { LocationOption, locationKey } from "@/types/location";
import { getResortLocationParams } from "@/utils/convexResort";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ResortPageParams = { country: string; region: string; resortId: string };

export async function generateStaticParams(): Promise<ResortPageParams[]> {
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
    .map((resort) =>
      getResortLocationParams(resort.resortId, resort.country, resort.region),
    );
}

export default async function ResortPage({
  params,
}: {
  params: Promise<ResortPageParams>;
}) {
  const { resortId } = await params;
  const [preloadedResort, preloadedResortHours, preloadedWeatherAndStatus] =
    await Promise.all([
      preloadQuery(api.resorts.getByResortId, { resortId }),
      preloadQuery(api.resortHours.getByResort, { resortId }),
      preloadQuery(api.weatherAndStatus.getByResort, { resortId }),
    ]);

  if (!preloadedQueryResult(preloadedResort)) {
    notFound();
  }

  return (
    <ResortDetail
      preloadedResort={preloadedResort}
      preloadedResortHours={preloadedResortHours}
      preloadedWeatherAndStatus={preloadedWeatherAndStatus}
    />
  );
}
