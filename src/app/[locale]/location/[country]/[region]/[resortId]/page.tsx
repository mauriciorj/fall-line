import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { preloadQuery, preloadedQueryResult } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import ResortDetail from "@/src/features/place/component/resortDetail";
import { localizePath } from "@/src/i18n/routing";
import type { Locale } from "@/src/i18n/translations";
import {
  getResortHeroImage,
  getResortLocationParams,
  getResortLocationPath,
  toResort,
} from "@/utils/convexResort";
import { listPublishedResorts } from "@/utils/publishedResorts";
import {
  localizedAlternates,
  openGraphBase,
  resortDescription,
  resortTitle,
} from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ResortPageParams = {
  locale: Locale;
  country: string;
  region: string;
  resortId: string;
};

// Shared between generateMetadata and the page within one render.
const getPreloadedResort = cache((resortId: string) =>
  preloadQuery(api.resorts.getByResortId, { resortId }),
);

// Runs once per locale from the parent segment, so pages are built per locale.
export async function generateStaticParams(): Promise<
  Omit<ResortPageParams, "locale">[]
> {
  const resorts = await listPublishedResorts();
  return resorts.map((resort) =>
    getResortLocationParams(resort.resortId, resort.country, resort.region),
  );
}

export async function generateMetadata({
  params,
}: {
  params: Promise<ResortPageParams>;
}): Promise<Metadata> {
  const { locale, resortId } = await params;
  const resort = toResort(
    preloadedQueryResult(await getPreloadedResort(resortId)),
  );

  if (!resort) {
    return { title: "Resort not found", robots: { index: false, follow: false } };
  }

  const title = resortTitle(resort, locale);
  const description = resortDescription(resort, locale);
  const path = getResortLocationPath(
    resort.resortId,
    resort.country,
    resort.region,
  );

  return {
    title,
    description,
    alternates: localizedAlternates(path, locale),
    robots:
      resort.published === false ? { index: false, follow: false } : undefined,
    openGraph: {
      ...openGraphBase(locale),
      type: "website",
      title,
      description,
      url: localizePath(path, locale),
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
