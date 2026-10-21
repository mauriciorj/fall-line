"use client";

import Link from "next/link";
import { Mountain } from "lucide-react";
import { useLanguage } from "@/src/i18n";
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
  const { t } = useLanguage();

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
                <p className="font-semibold text-foreground">{group.label}</p>
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

        <p className="text-xs text-muted-foreground">© {t("appName")}</p>
      </div>
    </footer>
  );
};

export default SiteFooter;
