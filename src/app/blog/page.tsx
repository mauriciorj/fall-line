import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import BlogList from "@/src/features/blog/components/blogList";

// Convex's fetchQuery forces `cache: "no-store"`; force-static keeps the route
// statically rendered and lets `revalidate` drive ISR.
export const dynamic = "force-static";
export const revalidate = 3600;

export default async function BlogPage() {
  const preloadedArticles = await preloadQuery(api.blog.listPublished);

  return <BlogList preloadedArticles={preloadedArticles} />;
}
