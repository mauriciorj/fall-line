import type { Metadata } from "next";
import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import BlogList from "@/src/features/blog/components/blogList";
import { Locale, getTranslator } from "@/src/i18n/translations";
import { englishOnlyAlternates } from "@/utils/seo";

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

export default async function BlogPage() {
  const preloadedArticles = await preloadQuery(api.blog.listPublished);

  return <BlogList preloadedArticles={preloadedArticles} />;
}
