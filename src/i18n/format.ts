import { intlLocale } from "@/src/i18n/routing";
import type { Locale } from "@/src/i18n/translations";

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
