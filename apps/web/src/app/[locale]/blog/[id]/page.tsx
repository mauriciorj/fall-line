import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  fetchQuery,
  preloadQuery,
  preloadedQueryResult,
} from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import JsonLd from "@/components/jsonLd";
import BlogArticle from "@/src/features/blog/components/blogArticle";
import { Locale, defaultLocale, getTranslator } from "@/src/i18n/translations";
import {
  BlogArticleSummary,
  blogPostingNode,
  breadcrumbNode,
} from "@/utils/jsonLd";
import {
  DEFAULT_OG_IMAGE,
  absoluteUrl,
  englishOnlyAlternates,
  openGraphBase,
} from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ArticleSummary = BlogArticleSummary;

// Shared between generateMetadata and the page within one render.
const getPreloadedArticle = cache((slug: string) =>
  preloadQuery(api.blog.getPublishedBySlug, { slug }),
);

export async function generateStaticParams(): Promise<{ id: string }[]> {
  const articles = await fetchQuery(api.blog.listPublished);
  return articles.map((article: { slug: string }) => ({ id: article.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ locale: Locale; id: string }>;
}): Promise<Metadata> {
  const { locale, id } = await params;
  const article = preloadedQueryResult(
    await getPreloadedArticle(id),
  ) as ArticleSummary | null;

  if (!article) {
    return { title: "Article not found", robots: { index: false, follow: false } };
  }

  // Articles are stored in English only, so localized copies canonicalize to EN.
  const canonical = `/blog/${article.slug}`;

  return {
    title: article.title,
    description: article.description,
    alternates: englishOnlyAlternates(canonical),
    openGraph: {
      ...openGraphBase(locale),
      type: "article",
      title: article.title,
      description: article.description,
      url: canonical,
      publishedTime: new Date(article.publishedAt).toISOString(),
      modifiedTime: new Date(article.updatedAt).toISOString(),
      tags: article.tags,
      images: [
        { url: article.heroImageUrl ?? DEFAULT_OG_IMAGE, alt: article.title },
      ],
    },
  };
}

export default async function BlogArticlePage({
  params,
}: {
  params: Promise<{ locale: Locale; id: string }>;
}) {
  const { locale, id } = await params;
  const preloadedArticle = await getPreloadedArticle(id);
  const article = preloadedQueryResult(preloadedArticle) as ArticleSummary | null;

  if (!article) {
    notFound();
  }

  const t = getTranslator(locale);
  // Canonical lives on the EN URL (see generateMetadata), so the entity does too.
  const pageUrl = absoluteUrl(`/blog/${article.slug}`);

  return (
    <>
      <JsonLd
        nodes={[
          blogPostingNode(article, pageUrl),
          breadcrumbNode(
            [
              { name: t("home"), path: "/" },
              { name: t("blog"), path: "/blog" },
              { name: article.title, path: `/blog/${article.slug}` },
            ],
            defaultLocale,
          ),
        ]}
      />
      <BlogArticle preloadedArticle={preloadedArticle} />
    </>
  );
}
