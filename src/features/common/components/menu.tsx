"use client";

import {
  FileText,
  List,
  LogOut,
  Mail,
  Menu as MenuIcon,
  Newspaper,
  ShieldCheck,
} from "lucide-react";
import { useClerk, useUser } from "@clerk/nextjs";
import { useQuery } from "convex/react";
import Link from "next/link";
import { api } from "@/convex/_generated/api";
import { Button } from "@/components/ui/button";
import { localeOptions, useLanguage } from "@/src/i18n";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Es, Fr, Us } from "react-flags-select";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Menu = () => {
  const { locale, setLocale, t } = useLanguage();
  const { signOut } = useClerk();
  const { isSignedIn } = useUser();
  const adminStatus = useQuery(api.admin.isAdmin);

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button
          variant="default"
          size="icon"
          className="h-9 w-9 shrink-0 md:ml-5"
        >
          <MenuIcon className="h-4 w-4" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right" className="w-[280px]">
        <SheetHeader>
          <SheetTitle className="text-left">{t("menu")}</SheetTitle>
        </SheetHeader>
        <div className="mx-4 mt-2 space-y-2">
          <label
            htmlFor="language-select"
            className="text-xs font-medium text-foreground"
          >
            {t("language")}
          </label>
          <Select
            value={locale}
            onValueChange={(value) => setLocale(value as "en" | "fr" | "es")}
          >
            <SelectTrigger
              id="language-select"
              className="w-full bg-background text-foreground"
            >
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-background">
              {localeOptions.map((option) => (
                <SelectItem key={option.value} value={option.value}>
                  {option.value === "en" ? (
                    <Us />
                  ) : option.value === "fr" ? (
                    <Fr />
                  ) : (
                    <Es />
                  )}
                  {t(option.labelKey)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
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
          {isSignedIn && adminStatus?.isAdmin && (
            <button
              type="button"
              onClick={() => signOut({ redirectUrl: "/" })}
              className="flex items-center gap-3 rounded-md px-3 py-2.5 text-left text-sm font-medium text-foreground hover:bg-accent transition-colors"
            >
              <LogOut className="h-4 w-4 text-muted-foreground" />
              {t("signOut")}
            </button>
          )}
        </nav>
      </SheetContent>
    </Sheet>
  );
};

export default Menu;
