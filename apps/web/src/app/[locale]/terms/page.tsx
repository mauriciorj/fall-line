import type { Metadata } from "next";
import Link from "next/link";
import { localizePath } from "@/src/i18n/routing";
import { Locale, defaultLocale, getTranslator } from "@/src/i18n/translations";
import { englishOnlyAlternates, getSupportEmail } from "@/utils/seo";
import LegalSections from "@/components/legalSections";
import { legalUpdated } from "@fall-line/shared/content/legal";

type TermsParams = Promise<{ locale: Locale }>;

// Legal copy exists in English only; localized URLs canonicalize to /terms.
export const metadata: Metadata = {
  title: "Terms of Service",
  description: "Terms of Service for Fall Line.",
  alternates: englishOnlyAlternates("/terms"),
};

export default async function TermsPage({
  params,
}: {
  params: TermsParams;
}) {
  const { locale } = await params;
  const t = getTranslator(locale);
  const email = getSupportEmail();

  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <article lang="en" className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <Link
            href={localizePath("/", locale)}
            className="text-sm text-primary hover:underline"
          >
            {t("backHome")}
          </Link>
          {locale !== defaultLocale && (
            <p lang={locale} className="text-sm text-muted-foreground">
              {t("englishOnly")}
            </p>
          )}
          <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
          <p className="text-sm text-muted-foreground">Last updated: {legalUpdated}</p>
        </header>

        <LegalSections page="terms" />

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">8. Contact</h2>
          <p>
            Questions about these terms:{" "}
            {email ? (
              <a className="text-primary hover:underline" href={`mailto:${email}`}>
                {email}
              </a>
            ) : (
              <Link href={localizePath("/contact", locale)} className="text-primary hover:underline">
                {t("contactUs")}
              </Link>
            )}
            .
          </p>
        </section>
      </article>
    </main>
  );
}
