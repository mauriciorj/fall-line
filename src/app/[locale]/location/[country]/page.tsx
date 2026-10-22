import { cache } from "react";
import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import LocationBreadcrumb from "@/src/features/location/components/locationBreadcrumb";
import { priceRangeLabel } from "@/src/features/location/components/regionStats";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import { getResortLocationPath } from "@/utils/convexResort";
import { groupByCountry, regionStats } from "@/utils/locationGroups";
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

type CountryPageParams = { locale: Locale; country: string };

const getCountry = cache(async (countrySlug: string) => {
  const groups = groupByCountry(await listPublishedResorts());
  return groups.find((group) => group.countrySlug === countrySlug) ?? null;
});

export async function generateStaticParams(): Promise<
  Omit<CountryPageParams, "locale">[]
> {
  const groups = groupByCountry(await listPublishedResorts());
  return groups.map((group) => ({ country: group.countrySlug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<CountryPageParams>;
}): Promise<Metadata> {
  const { locale, country } = await params;
  const group = await getCountry(country);
  if (!group) return {};

  const t = getTranslator(locale);
  const title = t("metaCountryTitle", { country: group.country });
  const description = t("metaCountryDescription", {
    country: group.country,
    regions: group.regions
      .map((region) => {
        const count = region.resorts.length;
        return `${region.region} (${t(count === 1 ? "resortCount" : "resortsCount", { count })})`;
      })
      .join(", "),
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

export default async function CountryPage({
  params,
}: {
  params: Promise<CountryPageParams>;
}) {
  const { locale, country } = await params;
  const group = await getCountry(country);
  if (!group) notFound();

  const t = getTranslator(locale);

  return (
    <main className="mx-auto max-w-6xl space-y-10 px-6 py-10">
      <header className="space-y-4">
        <LocationBreadcrumb
          locale={locale}
          items={[{ label: t("home"), href: "/" }, { label: group.country }]}
        />
        <h1 className="font-serif text-3xl font-semibold tracking-tight md:text-5xl">
          {t("countryHeading", { country: group.country })}
        </h1>
        <p className="max-w-3xl text-lg text-muted-foreground">
          {t("countryIntro", { country: group.country })}
        </p>
      </header>

      <section className="space-y-4">
        <h2 className="font-serif text-2xl font-medium">{t("regions")}</h2>
        <div className="grid gap-6 md:grid-cols-2">
          {group.regions.map((region) => {
            const stats = regionStats(region.resorts);
            const summary = [
              t(stats.count === 1 ? "resortCount" : "resortsCount", {
                count: stats.count,
              }),
              priceRangeLabel(stats, locale),
              stats.totalRuns > 0 &&
                t("metaRuns", { count: stats.totalRuns }),
            ].filter(Boolean);

            return (
              <article
                key={region.path}
                className="space-y-3 rounded-lg border border-border bg-card p-6"
              >
                <h3 className="font-serif text-xl font-medium">
                  <Link
                    href={localizePath(region.path, locale)}
                    className="hover:text-primary hover:underline"
                  >
                    {t("regionHeading", {
                      region: region.region,
                      country: region.country,
                    })}
                  </Link>
                </h3>
                <p className="text-sm text-muted-foreground">
                  {summary.join(" · ")}
                </p>
                <ul className="flex flex-wrap gap-x-3 gap-y-1 text-sm">
                  {region.resorts.map((resort) => (
                    <li key={resort.resortId}>
                      <Link
                        href={localizePath(
                          getResortLocationPath(
                            resort.resortId,
                            resort.country,
                            resort.region,
                          ),
                          locale,
                        )}
                        className="text-foreground hover:text-primary hover:underline"
                      >
                        {resort.name}
                      </Link>
                    </li>
                  ))}
                </ul>
                <Link
                  href={localizePath(region.path, locale)}
                  className="inline-block text-sm font-medium text-primary hover:underline"
                >
                  {t("allResortsIn", { region: region.region })} →
                </Link>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
