import { Locale, defaultLocale } from "@/src/i18n/translations";

const isEmpty = (value: unknown) =>
  value === undefined ||
  value === null ||
  (typeof value === "string" && value.trim() === "") ||
  (Array.isArray(value) && value.length === 0);

// Returns the requested locale's value, else the default locale's, with the
// language it actually resolved to so callers can mark fallbacks with `lang`.
export function pickLocalized<T>(
  value: Partial<Record<Locale, T>> | undefined,
  locale: Locale,
): { value: T; lang: Locale } | null {
  if (!value) return null;
  for (const lang of [locale, defaultLocale]) {
    const candidate = value[lang];
    if (!isEmpty(candidate)) return { value: candidate as T, lang };
  }
  return null;
}

// First sentences of `text` that fit in `max` characters; word-boundary cut otherwise.
export function summarize(text: string, max = 155) {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (normalized.length <= max) return normalized;

  const sentences = normalized.match(/[^.!?]+[.!?]+(\s|$)/g) ?? [];
  let summary = "";
  for (const sentence of sentences) {
    if ((summary + sentence).trim().length > max) break;
    summary += sentence;
  }
  if (summary.trim()) return summary.trim();

  const cut = normalized.slice(0, max - 1);
  return `${cut.slice(0, cut.lastIndexOf(" "))}…`;
}
