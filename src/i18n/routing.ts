import { Locale, defaultLocale, locales } from "@/src/i18n/translations";

export function isLocale(value: string | undefined): value is Locale {
  return locales.includes(value as Locale);
}

// Default locale is served unprefixed (/...), others under /<locale>/...
export function localizePath(path: string, locale: Locale) {
  const normalized = path.startsWith("/") ? path : `/${path}`;
  if (locale === defaultLocale) return normalized;
  return normalized === "/" ? `/${locale}` : `/${locale}${normalized}`;
}

// Works for both the public URL (/fr/x, /x) and the rewritten one (/en/x).
export function stripLocale(pathname: string) {
  const [, first, ...rest] = pathname.split("/");
  if (!isLocale(first)) return pathname || "/";
  return `/${rest.join("/")}`;
}

export function localeFromPathname(pathname: string): Locale {
  const [, first] = pathname.split("/");
  return isLocale(first) ? first : defaultLocale;
}

// BCP 47 tags for Intl formatting.
export const intlLocale: Record<Locale, string> = {
  en: "en-CA",
  fr: "fr-CA",
  es: "es-ES",
};

export const ogLocale: Record<Locale, string> = {
  en: "en_CA",
  fr: "fr_CA",
  es: "es_ES",
};
