"use client";

import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLanguage } from "@/src/i18n";
import Link from "@/src/i18n/link";

// Boundary for notFound() thrown by pages in this tree (e.g. unknown resort).
// Unmatched URLs never reach this segment; they use app/not-found.tsx instead.
export default function NotFound() {
  const { t } = useLanguage();

  return (
    <main className="flex min-h-[calc(100vh-73px)] flex-col items-center justify-center gap-4 px-6 text-center">
      <h1 className="font-serif text-3xl font-semibold">{t("pageNotFound")}</h1>
      <Button asChild variant="ghost">
        <Link href="/">
          <ArrowLeft className="mr-2 h-4 w-4" />
          {t("backAllResorts")}
        </Link>
      </Button>
    </main>
  );
}
