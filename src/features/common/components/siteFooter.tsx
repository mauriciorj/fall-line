"use client";

import NextLink from "next/link";
import { usePathname } from "next/navigation";
import { Mountain } from "lucide-react";
import { localeOptions, useLanguage } from "@/src/i18n";
import Link from "@/src/i18n/link";
import { localizePath, stripLocale } from "@/src/i18n/routing";
import { getTranslator } from "@/src/i18n/translations";
import type { FooterGroup } from "@/utils/publishedResorts";
import { getResortLocationPath } from "@/utils/convexResort";

const navLinks = [
  { href: "/", labelKey: "resortList" },
  { href: "/blog", labelKey: "blog" },
  { href: "/contact", labelKey: "contactUs" },
  { href: "/terms", labelKey: "terms" },
  { href: "/privacy", labelKey: "privacy" },
];

const SiteFooter = ({ groups }: { groups: FooterGroup[] }) => {
  const { locale, t } = useLanguage();
  const basePath = stripLocale(usePathname());

  return (
    <footer className="border-t border-border bg-card text-sm">
      <div className="mx-auto max-w-6xl space-y-10 px-6 py-12">
        <div className="flex flex-col gap-8 md:flex-row md:items-start md:justify-between">
          <div className="max-w-sm space-y-2">
            <Link href="/" className="flex items-center gap-2 text-primary">
              <Mountain className="h-7 w-7" />
              <span className="text-lg font-bold uppercase tracking-wide">
                {t("appName")}
              </span>
            </Link>
            <p className="text-muted-foreground">{t("tagline")}</p>
          </div>
          <nav aria-label={t("footerNav")}>
            <ul className="flex flex-wrap gap-x-6 gap-y-2">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="font-medium text-foreground hover:text-primary hover:underline"
                  >
                    {t(link.labelKey)}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {groups.length > 0 && (
          <nav aria-label={t("footerResorts")} className="space-y-6">
            {groups.map((group) => (
              <div key={group.label} className="space-y-2">
                <p className="font-semibold">
                  <Link
                    href={group.path}
                    className="text-foreground hover:text-primary hover:underline"
                  >
                    {group.label}
                  </Link>
                </p>
                <ul className="flex flex-wrap gap-x-4 gap-y-1.5">
                  {group.resorts.map((resort) => (
                    <li key={resort.resortId}>
                      <Link
                        href={getResortLocationPath(
                          resort.resortId,
                          resort.country,
                          resort.region,
                        )}
                        className="text-muted-foreground hover:text-primary hover:underline"
                      >
                        {resort.name}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        )}

        {/* Crawlable links between language versions (complements hreflang). */}
        <nav aria-label={t("language")}>
          <ul className="flex flex-wrap gap-x-4 gap-y-1.5">
            {localeOptions.map((option) => (
              <li key={option.value}>
                <NextLink
                  href={localizePath(basePath, option.value)}
                  hrefLang={option.value}
                  lang={option.value}
                  aria-current={option.value === locale ? "true" : undefined}
                  className={
                    option.value === locale
                      ? "font-medium text-foreground"
                      : "text-muted-foreground hover:text-primary hover:underline"
                  }
                >
                  {getTranslator(option.value)(option.labelKey)}
                </NextLink>
              </li>
            ))}
          </ul>
        </nav>

        <p className="text-xs text-muted-foreground">© {t("appName")}</p>
      </div>
    </footer>
  );
};

export default SiteFooter;
