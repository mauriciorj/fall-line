"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { localeFromPathname, localizePath } from "@/src/i18n/routing";
import {
  Locale,
  defaultLocale,
  getTranslator,
} from "@/src/i18n/translations";

import "./globals.css";

// Statically rendered 404s are served from this global route (not the nested
// [locale] tree), so the locale is derived from the URL after mount.
export default function NotFound() {
  const pathname = usePathname();
  const [locale, setLocale] = useState<Locale>(defaultLocale);
  const t = getTranslator(locale);

  useEffect(() => {
    setLocale(localeFromPathname(pathname));
  }, [pathname]);

  return (
    <html lang={locale}>
      <body className="antialiased">
        <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-6 text-center text-foreground">
          <h1 className="font-serif text-3xl font-semibold">
            {t("pageNotFound")}
          </h1>
          <Link
            href={localizePath("/", locale)}
            className="text-primary hover:underline"
          >
            {t("backAllResorts")}
          </Link>
        </main>
      </body>
    </html>
  );
}
