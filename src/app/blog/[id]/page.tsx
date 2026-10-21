import { cache } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  fetchQuery,
  preloadQuery,
  preloadedQueryResult,
} from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import BlogArticle from "@/src/features/blog/components/blogArticle";
import { DEFAULT_OG_IMAGE, baseOpenGraph } from "@/utils/seo";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

type ArticleSummary = {
  slug: string;
  title: string;
  description: string;
  tags: string[];
  publishedAt: number;
  updatedAt: number;
  heroImageUrl?: string | null;
};

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
  params: Promise<{ id: string }>;
}): Promise<Metadata> {
  const { id } = await params;
  const article = preloadedQueryResult(
    await getPreloadedArticle(id),
  ) as ArticleSummary | null;

  if (!article) {
    return { title: "Article not found", robots: { index: false, follow: false } };
  }

  const canonical = `/blog/${article.slug}`;

  return {
    title: article.title,
    description: article.description,
    alternates: { canonical },
    openGraph: {
      ...baseOpenGraph,
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
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const preloadedArticle = await getPreloadedArticle(id);

  if (!preloadedQueryResult(preloadedArticle)) {
    notFound();
  }

  return <BlogArticle preloadedArticle={preloadedArticle} />;
}
