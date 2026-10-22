"use client";

import { useLanguage } from "@/src/i18n";
import { formatDate } from "@/src/i18n/format";
import { cn } from "@/utils/utils";

// Absolute, zone-fixed dates (not "2 hours ago") so SSR and hydration agree
// and crawlers get a machine-readable <time dateTime>. Optional source link
// cites where the data was collected from.
export default function UpdatedAt({
  timestamp,
  labelKey,
  sourceUrl,
  className,
}: {
  timestamp?: number | null;
  labelKey: string;
  sourceUrl?: string | null;
  className?: string;
}) {
  const { locale, t } = useLanguage();
  if (!timestamp) return null;

  return (
    <span className={cn("text-xs text-muted-foreground", className)}>
      <time dateTime={new Date(timestamp).toISOString()}>
        {t(labelKey, { date: formatDate(timestamp, locale) })}
      </time>
      {sourceUrl && (
        <>
          {" · "}
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-primary"
          >
            {t("source")}
          </a>
        </>
      )}
    </span>
  );
}
