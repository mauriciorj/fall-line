"use client";

import Link from "next/link";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useLanguage } from "@/src/i18n";

type Article = {
  slug: string;
  title: string;
  description: string;
  tags: string[];
  publishedAt: number;
  heroImageUrl?: string | null;
};

export default function BlogPage() {
  const { locale, t } = useLanguage();
  const articles = useQuery(api.blog.listPublished) as Article[] | undefined;
  const dateLocale = locale === "fr" ? "fr-CA" : locale === "es" ? "es-ES" : "en-CA";

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
        {articles === undefined ? (
          <p className="text-muted-foreground">{t("loadingArticle")}</p>
        ) : articles.length === 0 ? (
          <p className="text-muted-foreground">{t("noArticles")}</p>
        ) : (
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {articles.map((article) => (
              <Link key={article.slug} href={`/blog/${article.slug}`} className="group overflow-hidden rounded-xl border border-border bg-card transition-shadow hover:shadow-lg">
                <div className="aspect-[16/9] overflow-hidden bg-primary/10">
                  {article.heroImageUrl ? (
                    <img src={article.heroImageUrl} alt={article.title} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" />
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
                  <p className="text-xs text-muted-foreground">{new Intl.DateTimeFormat(dateLocale, { dateStyle: "medium" }).format(new Date(article.publishedAt))}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
