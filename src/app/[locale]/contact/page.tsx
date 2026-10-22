import type { Metadata } from "next";
import Link from "next/link";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import { getSupportEmail, localizedAlternates } from "@/utils/seo";

type ContactParams = Promise<{ locale: Locale }>;

export async function generateMetadata({
  params,
}: {
  params: ContactParams;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = getTranslator(locale);

  return {
    title: t("contactUs"),
    description: t("contactBody"),
    alternates: localizedAlternates("/contact", locale),
  };
}

export default async function ContactPage({
  params,
}: {
  params: ContactParams;
}) {
  const { locale } = await params;
  const t = getTranslator(locale);
  const email = getSupportEmail();

  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <article className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <Link
            href={localizePath("/", locale)}
            className="text-sm text-primary hover:underline"
          >
            {t("backHome")}
          </Link>
          <h1 className="text-4xl font-bold tracking-tight">{t("contactUs")}</h1>
          <p className="text-sm text-muted-foreground">
            {t("contactDescription")}
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">{t("getInTouch")}</h2>
          <p>{t("contactBody")}</p>
          {email && (
            <p>
              {t("email")}:{" "}
              <a className="text-primary hover:underline" href={`mailto:${email}`}>
                {email}
              </a>
            </p>
          )}
          <p>
            <Link
              href={localizePath("/about", locale)}
              className="text-primary hover:underline"
            >
              {t("aboutHeading", { site: t("appName") })}
            </Link>
          </p>
        </section>
      </article>
    </main>
  );
}
