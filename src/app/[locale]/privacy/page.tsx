import type { Metadata } from "next";
import Link from "next/link";
import { localizePath } from "@/src/i18n/routing";
import { Locale, defaultLocale, getTranslator } from "@/src/i18n/translations";
import { englishOnlyAlternates, getSupportEmail } from "@/utils/seo";
import LegalSections from "@/components/legalSections";
import { legalUpdated } from "@fall-line/shared/content/legal";

type PrivacyParams = Promise<{ locale: Locale }>;

// Legal copy exists in English only; localized URLs canonicalize to /privacy.
export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy for Fall Line.",
  alternates: englishOnlyAlternates("/privacy"),
};

export default async function PrivacyPage({
  params,
}: {
  params: PrivacyParams;
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
          <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
          <p className="text-sm text-muted-foreground">Last updated: {legalUpdated}</p>
        </header>

        <LegalSections page="privacy" />

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">9. Contact</h2>
          <p>
            Privacy questions:{" "}
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
