import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  fetchQuery,
  preloadQuery,
  preloadedQueryResult,
} from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import ResortDetail from "@/src/features/place/component/resortDetail";
import { LocationOption, locationKey } from "@/types/location";
import {
  getResortHeroImage,
  getResortLocationParams,
  getResortLocationPath,
  toResort,
} from "@/utils/convexResort";
import { baseOpenGraph, resortDescription, resortTitle } from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ResortPageParams = { country: string; region: string; resortId: string };

// Shared between generateMetadata and the page within one render.
const getPreloadedResort = cache((resortId: string) =>
  preloadQuery(api.resorts.getByResortId, { resortId }),
);

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

export async function generateMetadata({
  params,
}: {
  params: Promise<ResortPageParams>;
}): Promise<Metadata> {
  const { resortId } = await params;
  const resort = toResort(
    preloadedQueryResult(await getPreloadedResort(resortId)),
  );

  if (!resort) {
    return { title: "Resort not found", robots: { index: false, follow: false } };
  }

  const title = resortTitle(resort);
  const description = resortDescription(resort);
  const canonical = getResortLocationPath(
    resort.resortId,
    resort.country,
    resort.region,
  );

  return {
    title,
    description,
    alternates: { canonical },
    robots:
      resort.published === false ? { index: false, follow: false } : undefined,
    openGraph: {
      ...baseOpenGraph,
      type: "website",
      title,
      description,
      url: canonical,
      images: [
        {
          url: getResortHeroImage(resort.resortId, resort.country, resort.region),
          alt: resort.name,
        },
      ],
    },
  };
}

export default async function ResortPage({
  params,
}: {
  params: Promise<ResortPageParams>;
}) {
  const { resortId } = await params;
  const [preloadedResort, preloadedResortHours, preloadedWeatherAndStatus] =
    await Promise.all([
      getPreloadedResort(resortId),
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
