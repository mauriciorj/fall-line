"use client";

import Image from "next/image";
import { Preloaded, usePreloadedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useLanguage } from "@/src/i18n";
import Link from "@/src/i18n/link";
import ArticleMeta from "@/src/features/blog/components/articleMeta";

type Article = {
  slug: string;
  title: string;
  description: string;
  author?: string | null;
  tags: string[];
  publishedAt: number;
  updatedAt: number;
  heroImageUrl?: string | null;
};

export default function BlogList({
  preloadedArticles,
}: {
  preloadedArticles: Preloaded<typeof api.blog.listPublished>;
}) {
  const { t } = useLanguage();
  const articles = usePreloadedQuery(preloadedArticles) as Article[];

  return (
    <main className="min-h-[calc(100vh-73px)] bg-background">
      <section className="border-b border-border bg-muted/30 px-6 py-16">
        <div className="mx-auto max-w-6xl space-y-4">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">{t("blog")}</p>
          <h1 className="font-serif text-4xl font-semibold tracking-tight md:text-6xl">{t("blogTitle")}</h1>
          <p className="max-w-2xl text-lg text-muted-foreground">{t("blogDescription")}</p>
        </div>
      </section>
      <section className="mx-auto max-w-6xl px-6 py-12">
        {articles.length === 0 ? (
          <p className="text-muted-foreground">{t("noArticles")}</p>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <Link key={article.slug} href={`/blog/${article.slug}`} className="group overflow-hidden rounded-xl border border-border bg-card transition-shadow hover:shadow-lg">
                <div className="relative aspect-[16/9] overflow-hidden bg-primary/10">
                  {article.heroImageUrl ? (
                    <Image
                      src={article.heroImageUrl}
                      alt={article.title}
                      fill
                      sizes="(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw"
                      className="object-cover transition-transform duration-500 group-hover:scale-105"
                    />
                  ) : (
                    <div className="h-full w-full bg-gradient-to-br from-primary/30 via-primary/10 to-background" />
                  )}
                </div>
                <div className="space-y-4 p-5">
                  <div className="flex flex-wrap gap-2">
                    {article.tags.map((tag) => <span key={tag} className="rounded-full bg-muted px-2.5 py-1 text-xs text-muted-foreground">{tag}</span>)}
                  </div>
                  <div className="space-y-2">
                    <h2 className="font-serif text-2xl font-semibold group-hover:text-primary">{article.title}</h2>
                    <p className="line-clamp-3 text-sm text-muted-foreground">{article.description}</p>
                  </div>
                  <ArticleMeta
                    author={article.author}
                    publishedAt={article.publishedAt}
                    updatedAt={article.updatedAt}
                    className="text-xs text-muted-foreground"
                  />
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
