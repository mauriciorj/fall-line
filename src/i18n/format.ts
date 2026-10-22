import { intlLocale } from "@/src/i18n/routing";
import type { Locale } from "@/src/i18n/translations";

// Fixed zone: the audience is Ontario/Québec and server/client output must match.
export const SITE_TIME_ZONE = "America/Toronto";

export function formatDate(
  timestamp: number,
  locale: Locale,
  dateStyle: "medium" | "long" = "medium",
) {
  return new Intl.DateTimeFormat(intlLocale[locale], {
    dateStyle,
    timeZone: SITE_TIME_ZONE,
  }).format(new Date(timestamp));
}

// Prices are CAD everywhere; "$67" (en), "67 $" (fr/es). Whole dollars stay whole.
export function formatCad(amount: number, locale: Locale) {
  return new Intl.NumberFormat(intlLocale[locale], {
    style: "currency",
    currency: "CAD",
    currencyDisplay: "narrowSymbol",
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}
