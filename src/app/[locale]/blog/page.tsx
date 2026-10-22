import type { Metadata } from "next";
import { preloadQuery, preloadedQueryResult } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import JsonLd from "@/components/jsonLd";
import BlogList from "@/src/features/blog/components/blogList";
import { Locale, defaultLocale, getTranslator } from "@/src/i18n/translations";
import { BlogArticleSummary, blogNode, breadcrumbNode } from "@/utils/jsonLd";
import { absoluteUrl, englishOnlyAlternates } from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

// Articles are stored in English only, so localized copies canonicalize to /blog.
export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: Locale }>;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = getTranslator(locale);

  return {
    title: t("blogTitle"),
    description: t("blogDescription"),
    alternates: englishOnlyAlternates("/blog"),
  };
}

export default async function BlogPage({
  params,
}: {
  params: Promise<{ locale: Locale }>;
}) {
  const { locale } = await params;
  const preloadedArticles = await preloadQuery(api.blog.listPublished);
  const articles = preloadedQueryResult(preloadedArticles) as BlogArticleSummary[];
  const t = getTranslator(defaultLocale);

  return (
    <>
      <JsonLd
        nodes={[
          blogNode(articles, {
            url: absoluteUrl("/blog"),
            name: t("blogTitle"),
            description: t("blogDescription"),
          }),
          breadcrumbNode(
            [
              { name: getTranslator(locale)("home"), path: "/" },
              { name: getTranslator(locale)("blog"), path: "/blog" },
            ],
            locale,
          ),
        ]}
      />
      <BlogList preloadedArticles={preloadedArticles} />
    </>
  );
}
