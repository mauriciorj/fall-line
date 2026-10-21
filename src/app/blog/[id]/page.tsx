import { notFound } from "next/navigation";
import {
  fetchQuery,
  preloadQuery,
  preloadedQueryResult,
} from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import BlogArticle from "@/src/features/blog/components/blogArticle";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

export async function generateStaticParams(): Promise<{ id: string }[]> {
  const articles = await fetchQuery(api.blog.listPublished);
  return articles.map((article: { slug: string }) => ({ id: article.slug }));
}

export default async function BlogArticlePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const preloadedArticle = await preloadQuery(api.blog.getPublishedBySlug, {
    slug: id,
  });

  if (!preloadedQueryResult(preloadedArticle)) {
    notFound();
  }

  return <BlogArticle preloadedArticle={preloadedArticle} />;
}
