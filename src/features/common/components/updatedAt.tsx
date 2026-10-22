"use client";

import { useLanguage } from "@/src/i18n";
import { formatDate } from "@/src/i18n/format";
import { cn } from "@/utils/utils";

// Absolute, zone-fixed dates (not "2 hours ago") so SSR and hydration agree
// and crawlers get a machine-readable <time dateTime>.
export default function UpdatedAt({
  timestamp,
  labelKey,
  className,
}: {
  timestamp?: number | null;
  labelKey: string;
  className?: string;
}) {
  const { locale, t } = useLanguage();
  if (!timestamp) return null;

  return (
    <time
      dateTime={new Date(timestamp).toISOString()}
      className={cn("text-xs text-muted-foreground", className)}
    >
      {t(labelKey, { date: formatDate(timestamp, locale) })}
    </time>
  );
}
