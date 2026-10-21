import type { MetadataRoute } from "next";
import { fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { getResortLocationPath } from "@/utils/convexResort";
import { listPublishedResorts } from "@/utils/publishedResorts";
import { getSiteUrl } from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ArticleSummary = { slug: string; updatedAt: number };

function lastModified(timestamp?: number) {
  return timestamp ? { lastModified: new Date(timestamp) } : {};
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = getSiteUrl();
  const absolute = (path: string) => new URL(path, siteUrl).toString();

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

  const resortEntries = resorts.map((resort, index) => ({
    url: absolute(
      getResortLocationPath(resort.resortId, resort.country, resort.region),
    ),
    ...lastModified(conditions[index]?.updatedAt),
  }));
  const articleEntries = articles.map((article) => ({
    url: absolute(`/blog/${article.slug}`),
    ...lastModified(article.updatedAt),
  }));
  const latestArticleUpdate = articles.reduce(
    (latest, article) => Math.max(latest, article.updatedAt),
    0,
  );

  return [
    { url: absolute("/") },
    { url: absolute("/blog"), ...lastModified(latestArticleUpdate) },
    { url: absolute("/contact") },
    { url: absolute("/privacy") },
    { url: absolute("/terms") },
    ...resortEntries,
    ...articleEntries,
  ];
}
