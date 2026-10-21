"use client";

import { Preloaded, usePreloadedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { useLanguage } from "@/src/i18n";
import Link from "@/src/i18n/link";
import RichText from "@/src/features/blog/components/richText";

type Article = {
  title: string;
  description: string;
  body: unknown[];
  tags: string[];
  publishedAt: number;
  heroImageUrl?: string | null;
};

export default function BlogArticle({
  preloadedArticle,
}: {
  preloadedArticle: Preloaded<typeof api.blog.getPublishedBySlug>;
}) {
  const { locale, t } = useLanguage();
  const article = usePreloadedQuery(preloadedArticle) as Article | null;
  const dateLocale = locale === "fr" ? "fr-CA" : locale === "es" ? "es-ES" : "en-CA";

  if (!article) {
    return (
      <main className="flex min-h-[calc(100vh-73px)] flex-col items-center justify-center gap-4 px-6 text-center">
        <h1 className="font-serif text-3xl font-semibold">{t("articleNotFound")}</h1>
        <Link href="/blog" className="text-primary hover:underline">{t("blog")}</Link>
      </main>
    );
  }

  return (
    <main className="min-h-[calc(100vh-73px)] bg-background">
      <article className="mx-auto max-w-4xl px-6 py-10 md:py-16">
        <Link href="/blog" className="text-sm text-primary hover:underline">← {t("blog")}</Link>
        <header className="mt-8 space-y-5">
          <div className="flex flex-wrap gap-2">
            {article.tags.map((tag) => <span key={tag} className="rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">{tag}</span>)}
          </div>
          <h1 className="font-serif text-4xl font-semibold tracking-tight md:text-6xl">{article.title}</h1>
          <p className="text-xl text-muted-foreground">{article.description}</p>
          <p className="text-sm text-muted-foreground">{new Intl.DateTimeFormat(dateLocale, { dateStyle: "long", timeZone: "UTC" }).format(new Date(article.publishedAt))}</p>
        </header>
        {article.heroImageUrl && (
          <img src={article.heroImageUrl} alt={article.title} className="mt-10 aspect-[16/8] w-full rounded-xl object-cover" />
        )}
        <div className="mt-10">
          <RichText blocks={article.body} />
        </div>
      </article>
    </main>
  );
}
