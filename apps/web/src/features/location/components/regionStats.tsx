import { formatCad } from "@/src/i18n/format";
import { Locale, getTranslator } from "@/src/i18n/translations";
import type { regionStats } from "@/utils/locationGroups";

type Stats = ReturnType<typeof regionStats>;

export function priceRangeLabel(stats: Stats, locale: Locale) {
  const t = getTranslator(locale);
  if (stats.minPrice === null || stats.maxPrice === null) return "";
  const min = formatCad(stats.minPrice, locale);
  if (stats.minPrice === stats.maxPrice) return t("priceFrom", { min });
  return t("priceRange", { min, max: formatCad(stats.maxPrice, locale) });
}

export default function RegionStats({
  stats,
  locale,
}: {
  stats: Stats;
  locale: Locale;
}) {
  const t = getTranslator(locale);
  const cells = [
    [t("statResorts"), String(stats.count)],
    [t("statLiftTickets"), priceRangeLabel(stats, locale) || "—"],
    [t("statTotalRuns"), String(stats.totalRuns)],
    [t("statWithTubing"), String(stats.withTubing)],
  ];

  return (
    <dl className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {cells.map(([label, value]) => (
        <div
          key={label}
          className="rounded-lg border border-border bg-card p-5"
        >
          <dt className="text-xs uppercase tracking-wide text-muted-foreground">
            {label}
          </dt>
          <dd className="mt-2 text-2xl font-medium text-foreground">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
