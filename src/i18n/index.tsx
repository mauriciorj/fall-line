"use client";

import { createContext, useContext, useMemo, type ReactNode } from "react";
import {
  Locale,
  Translator,
  getTranslator,
} from "@/src/i18n/translations";

export type { Locale } from "@/src/i18n/translations";

interface LanguageContextValue {
  locale: Locale;
  t: Translator;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

// The locale comes from the URL segment (see app/[locale]/layout.tsx); switching
// language is a navigation, so server and client always agree on `lang`.
export function LanguageProvider({
  locale,
  children,
}: {
  locale: Locale;
  children: ReactNode;
}) {
  const value = useMemo<LanguageContextValue>(
    () => ({ locale, t: getTranslator(locale) }),
    [locale],
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}

export const localeOptions: Array<{
  value: Locale;
  labelKey: string;
  flag: string;
}> = [
  { value: "en", labelKey: "english", flag: "US" },
  { value: "fr", labelKey: "french", flag: "FR" },
  { value: "es", labelKey: "spanish", flag: "ES" },
];
