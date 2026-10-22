import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { preloadQuery, preloadedQueryResult } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import JsonLd from "@/components/jsonLd";
import ResortDetail from "@/src/features/place/component/resortDetail";
import { pickLocalized, summarize } from "@/src/i18n/localized";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import {
  getCountryPath,
  getRegionPath,
  getResortHeroImage,
  getResortLocationParams,
  getResortLocationPath,
  toResort,
} from "@/utils/convexResort";
import {
  breadcrumbNode,
  faqNode,
  skiResortNode,
  webPageNode,
} from "@/utils/jsonLd";
import { listPublishedResorts } from "@/utils/publishedResorts";
import {
  absoluteUrl,
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
  // Editorial copy in the page's own language beats the generated summary;
  // an English-only description is not used for FR/ES metadata.
  const editorial = pickLocalized(resort.description, locale);
  const description =
    editorial && editorial.lang === locale
      ? summarize(editorial.value)
      : resortDescription(resort, locale);
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
  const { locale, resortId } = await params;
  const [preloadedResort, preloadedResortHours, preloadedWeatherAndStatus] =
    await Promise.all([
      getPreloadedResort(resortId),
      preloadQuery(api.resortHours.getByResort, { resortId }),
      preloadQuery(api.weatherAndStatus.getByResort, { resortId }),
    ]);

  const resort = toResort(preloadedQueryResult(preloadedResort));
  if (!resort) {
    notFound();
  }

  const t = getTranslator(locale);
  const path = getResortLocationPath(
    resort.resortId,
    resort.country,
    resort.region,
  );
  // Mirrors what the page displays: editorial copy (with EN fallback) or the data summary.
  const faq = pickLocalized(resort.faq, locale);
  const pageUrl = absoluteUrl(localizePath(path, locale));
  const hoursDoc = preloadedQueryResult(preloadedResortHours);
  const conditionsDoc = preloadedQueryResult(preloadedWeatherAndStatus);
  const dateModified = Math.max(
    resort.updatedAt ?? 0,
    resort.contentUpdatedAt ?? 0,
    hoursDoc?.updatedAt ?? 0,
    conditionsDoc?.updatedAt ?? 0,
  );
  const structuredData = [
    webPageNode(locale, {
      url: pageUrl,
      name: resortTitle(resort, locale),
      mainEntityId: `${pageUrl}#resort`,
      dateModified: dateModified || null,
    }),
    skiResortNode(resort, locale, {
      pageUrl,
      description:
        pickLocalized(resort.description, locale)?.value ??
        resortDescription(resort, locale),
      hours: hoursDoc?.hours ?? [],
    }),
    breadcrumbNode(
      [
        { name: t("home"), path: "/" },
        ...(resort.country
          ? [{ name: resort.country, path: getCountryPath(resort.country) }]
          : []),
        ...(resort.country && resort.region
          ? [{ name: resort.region, path: getRegionPath(resort.country, resort.region) }]
          : []),
        { name: resort.name, path },
      ],
      locale,
    ),
    ...(faq ? [faqNode(faq.value)] : []),
  ];

  return (
    <>
      <JsonLd nodes={structuredData} />
      <ResortDetail
        preloadedResort={preloadedResort}
        preloadedResortHours={preloadedResortHours}
        preloadedWeatherAndStatus={preloadedWeatherAndStatus}
      />
    </>
  );
}
