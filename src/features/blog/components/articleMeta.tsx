"use client";

import { useLanguage } from "@/src/i18n";
import { formatDate } from "@/src/i18n/format";

// Byline + machine-readable dates. "Updated" only when it falls on a later
// calendar day than publication, so same-day edits don't add noise.
export default function ArticleMeta({
  author,
  publishedAt,
  updatedAt,
  dateStyle = "medium",
  className,
}: {
  author?: string | null;
  publishedAt: number;
  updatedAt?: number;
  dateStyle?: "medium" | "long";
  className?: string;
}) {
  const { locale, t } = useLanguage();
  const published = formatDate(publishedAt, locale, dateStyle);
  const updated =
    updatedAt && formatDate(updatedAt, locale, dateStyle) !== published
      ? formatDate(updatedAt, locale, dateStyle)
      : null;

  return (
    <p className={className}>
      {author && <span>{t("byAuthor", { author })} · </span>}
      <time dateTime={new Date(publishedAt).toISOString()}>
        {t("publishedOn", { date: published })}
      </time>
      {updated && updatedAt && (
        <>
          {" · "}
          <time dateTime={new Date(updatedAt).toISOString()}>
            {t("updatedOn", { date: updated })}
          </time>
        </>
      )}
    </p>
  );
}
