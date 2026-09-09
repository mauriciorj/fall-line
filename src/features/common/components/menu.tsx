"use client";

import {
  FileText,
  List,
  Mail,
  Menu as MenuIcon,
  Newspaper,
  ShieldCheck,
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { localeOptions, useLanguage } from "@/src/i18n";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";

const Menu = () => {
  const { locale, setLocale, t } = useLanguage();

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="default" size="icon" className="h-9 w-9 ml-5">
          <MenuIcon className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px]">
        <SheetHeader>
          <SheetTitle className="text-left">{t("menu")}</SheetTitle>
        </SheetHeader>
        <div className="mt-6 space-y-2">
          <label htmlFor="language-select" className="text-xs font-medium text-muted-foreground">
            {t("language")}
          </label>
          <select
            id="language-select"
            value={locale}
            onChange={(event) => setLocale(event.target.value as "en" | "fr" | "es")}
            className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm text-foreground"
          >
            {localeOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {t(option.labelKey)}
              </option>
            ))}
          </select>
        </div>
        <nav className="mt-6 flex flex-col gap-1">
          <Link
            href="/"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <List className="h-4 w-4 text-muted-foreground" />
            {t("resortList")}
          </Link>
          <Link
            href="/blog"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <Newspaper className="h-4 w-4 text-muted-foreground" />
            {t("blog")}
          </Link>
          <Link
            href="/contact"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <Mail className="h-4 w-4 text-muted-foreground" />
            {t("contactUs")}
          </Link>
          <Link
            href="/terms"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <FileText className="h-4 w-4 text-muted-foreground" />
            {t("terms")}
          </Link>
          <Link
            href="/privacy"
            className="flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-foreground hover:bg-accent transition-colors"
          >
            <ShieldCheck className="h-4 w-4 text-muted-foreground" />
            {t("privacy")}
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  );
};

export default Menu;
