import type { Metadata } from "next";
import Link from "next/link";
import JsonLd from "@/components/jsonLd";
import LocationBreadcrumb from "@/src/features/location/components/locationBreadcrumb";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import { aboutPageNode, breadcrumbNode } from "@/utils/jsonLd";
import { absoluteUrl, localizedAlternates } from "@/utils/seo";

type AboutParams = Promise<{ locale: Locale }>;

export async function generateMetadata({
  params,
}: {
  params: AboutParams;
}): Promise<Metadata> {
  const { locale } = await params;
  const t = getTranslator(locale);
  const site = t("appName");

  // Short label: the layout template appends the site name.
  return {
    title: t("aboutPage"),
    description: t("aboutMetaDescription", { site }),
    alternates: localizedAlternates("/about", locale),
  };
}

export default async function AboutPage({ params }: { params: AboutParams }) {
  const { locale } = await params;
  const t = getTranslator(locale);
  const site = t("appName");
  const heading = t("aboutHeading", { site });
  const sections = [
    ["aboutDataHeading", "aboutDataBody"],
    ["aboutAccuracyHeading", "aboutAccuracyBody"],
    ["aboutLanguagesHeading", "aboutLanguagesBody"],
  ] as const;

  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <JsonLd
        nodes={[
          aboutPageNode(locale, {
            url: absoluteUrl(localizePath("/about", locale)),
            name: heading,
            description: t("aboutMetaDescription", { site }),
          }),
          breadcrumbNode(
            [
              { name: t("home"), path: "/" },
              { name: t("aboutPage"), path: "/about" },
            ],
            locale,
          ),
        ]}
      />
      <article className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <LocationBreadcrumb
            locale={locale}
            items={[{ label: t("home"), href: "/" }, { label: t("aboutPage") }]}
          />
          <h1 className="text-4xl font-bold tracking-tight">{heading}</h1>
          <p className="text-lg text-muted-foreground">{t("aboutIntro", { site })}</p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">{t("aboutTeamHeading")}</h2>
          <p>{t("aboutTeamBody", { site, team: t("teamName") })}</p>
        </section>

        {sections.map(([headingKey, bodyKey]) => (
          <section key={headingKey} className="space-y-3">
            <h2 className="text-2xl font-semibold">{t(headingKey)}</h2>
            <p>{t(bodyKey)}</p>
          </section>
        ))}

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">{t("contact")}</h2>
          <p>
            {t("aboutContactBody")}{" "}
            <Link
              href={localizePath("/contact", locale)}
              className="text-primary hover:underline"
            >
              {t("contactUs")}
            </Link>
          </p>
        </section>
      </article>
    </main>
  );
}
