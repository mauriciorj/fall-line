import type { Metadata } from "next";
import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import BlogList from "@/src/features/blog/components/blogList";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

export const metadata: Metadata = {
  title: "Ski Stories & Mountain News",
  description:
    "Guides, updates, and stories from Ontario's ski community: resort news, trip planning tips and seasonal conditions.",
  alternates: { canonical: "/blog" },
};

export default async function BlogPage() {
  const preloadedArticles = await preloadQuery(api.blog.listPublished);

  return <BlogList preloadedArticles={preloadedArticles} />;
}
