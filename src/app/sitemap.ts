import type { MetadataRoute } from "next";
import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { localizePath } from "@/src/i18n/routing";
import { defaultLocale, locales } from "@/src/i18n/translations";
import { getResortLocationPath } from "@/utils/convexResort";
import { groupByCountry } from "@/utils/locationGroups";
import { listPublishedResorts } from "@/utils/publishedResorts";
import { absoluteUrl, languageAlternates } from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ArticleSummary = { slug: string; updatedAt: number };

function lastModified(timestamp?: number) {
  return timestamp ? { lastModified: new Date(timestamp) } : {};
}

// Translated pages: one entry per locale, each carrying the full hreflang set.
function localizedEntries(
  path: string,
  extra: Partial<MetadataRoute.Sitemap[number]> = {},
): MetadataRoute.Sitemap {
  const alternates = { languages: languageAlternates(path, absoluteUrl) };
  return locales.map((locale) => ({
    url: absoluteUrl(localizePath(path, locale)),
    alternates,
    ...extra,
  }));
}

// English-only content: the localized copies canonicalize here, so list once.
function englishEntry(
  path: string,
  extra: Partial<MetadataRoute.Sitemap[number]> = {},
): MetadataRoute.Sitemap[number] {
  return { url: absoluteUrl(localizePath(path, defaultLocale)), ...extra };
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [resorts, articles] = await Promise.all([
    listPublishedResorts(),
    fetchQuery(api.blog.listPublished) as Promise<ArticleSummary[]>,
  ]);
  // Conditions are the most frequently updated content on a resort page.
  const conditions = await Promise.all(
    resorts.map((resort) =>
      fetchQuery(api.weatherAndStatus.getByResort, {
        resortId: resort.resortId,
      }),
    ),
  );

  const hubEntries = groupByCountry(resorts).flatMap((country) => [
    ...localizedEntries(country.path),
    ...country.regions.flatMap((region) => localizedEntries(region.path)),
  ]);
  const resortEntries = resorts.flatMap((resort, index) =>
    localizedEntries(
      getResortLocationPath(resort.resortId, resort.country, resort.region),
      lastModified(
        Math.max(conditions[index]?.updatedAt ?? 0, resort.contentUpdatedAt ?? 0),
      ),
    ),
  );
  const articleEntries = articles.map((article) =>
    englishEntry(`/blog/${article.slug}`, lastModified(article.updatedAt)),
  );
  const latestArticleUpdate = articles.reduce(
    (latest, article) => Math.max(latest, article.updatedAt),
    0,
  );

  return [
    ...localizedEntries("/"),
    ...localizedEntries("/contact"),
    englishEntry("/blog", lastModified(latestArticleUpdate)),
    englishEntry("/privacy"),
    englishEntry("/terms"),
    ...hubEntries,
    ...resortEntries,
    ...articleEntries,
  ];
}
