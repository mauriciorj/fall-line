import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import JsonLd from "@/components/jsonLd";
import LocationBreadcrumb from "@/src/features/location/components/locationBreadcrumb";
import RegionStats, {
  priceRangeLabel,
} from "@/src/features/location/components/regionStats";
import RegionTable from "@/src/features/location/components/regionTable";
import { formatDate } from "@/src/i18n/format";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import { getResortLocationPath } from "@/utils/convexResort";
import { breadcrumbNode, itemListNode } from "@/utils/jsonLd";
import { groupByRegion, regionStats } from "@/utils/locationGroups";
import { listPublishedResorts } from "@/utils/publishedResorts";
import {
  DEFAULT_OG_IMAGE,
  localizedAlternates,
  openGraphBase,
} from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type RegionPageParams = { locale: Locale; country: string; region: string };

const getRegion = cache(async (countrySlug: string, regionSlug: string) => {
  const groups = groupByRegion(await listPublishedResorts());
  return (
    groups.find(
      (group) =>
        group.countrySlug === countrySlug && group.regionSlug === regionSlug,
    ) ?? null
  );
});

export async function generateStaticParams(): Promise<
  Omit<RegionPageParams, "locale">[]
> {
  const groups = groupByRegion(await listPublishedResorts());
  return groups.map((group) => ({
    country: group.countrySlug,
    region: group.regionSlug,
  }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<RegionPageParams>;
}): Promise<Metadata> {
  const { locale, country, region } = await params;
  const group = await getRegion(country, region);
  if (!group) return {};

  const t = getTranslator(locale);
  const stats = regionStats(group.resorts);
  const title = t("metaRegionTitle", { region: group.region });
  const description = t("metaRegionDescription", {
    count: stats.count,
    region: group.region,
    country: group.country,
    priceRange: priceRangeLabel(stats, locale),
  });

  return {
    title,
    description,
    alternates: localizedAlternates(group.path, locale),
    openGraph: {
      ...openGraphBase(locale),
      type: "website",
      title,
      description,
      url: localizePath(group.path, locale),
      images: [{ url: DEFAULT_OG_IMAGE, alt: t("appName") }],
    },
  };
}

export default async function RegionPage({
  params,
}: {
  params: Promise<RegionPageParams>;
}) {
  const { locale, country, region } = await params;
  const group = await getRegion(country, region);
  if (!group) notFound();

  const t = getTranslator(locale);
  const stats = regionStats(group.resorts);
  const heading = t("regionHeading", { region: group.region, country: group.country });

  return (
    <main className="mx-auto max-w-6xl space-y-10 px-6 py-10">
      <JsonLd
        nodes={[
          breadcrumbNode(
            [
              { name: t("home"), path: "/" },
              { name: group.country, path: `/location/${group.countrySlug}` },
              { name: group.region, path: group.path },
            ],
            locale,
          ),
          itemListNode(
            heading,
            group.resorts.map((resort) => ({
              name: resort.name,
              path: getResortLocationPath(resort.resortId, resort.country, resort.region),
            })),
            locale,
          ),
        ]}
      />
      <header className="space-y-4">
        <LocationBreadcrumb
          locale={locale}
          items={[
            { label: t("home"), href: "/" },
            { label: group.country, href: `/location/${group.countrySlug}` },
            { label: group.region },
          ]}
        />
        <h1 className="font-serif text-3xl font-semibold tracking-tight md:text-5xl">
          {heading}
        </h1>
        <p className="max-w-3xl text-lg text-muted-foreground">
          {t("regionIntro", {
            count: stats.count,
            region: group.region,
            country: group.country,
          })}
        </p>
      </header>

      <RegionStats stats={stats} locale={locale} />

      <section className="space-y-4">
        <h2 className="font-serif text-2xl font-medium">{t("compareResorts")}</h2>
        <RegionTable resorts={group.resorts} locale={locale} />
        {stats.updatedAt && (
          <time
            dateTime={new Date(stats.updatedAt).toISOString()}
            className="block text-xs text-muted-foreground"
          >
            {t("dataUpdatedOn", { date: formatDate(stats.updatedAt, locale) })}
          </time>
        )}
      </section>
    </main>
  );
}
