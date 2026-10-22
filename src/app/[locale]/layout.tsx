import type { Metadata, Viewport } from "next";
import Script from "next/script";
import { notFound } from "next/navigation";
import { ClerkProvider } from "@clerk/nextjs";
import { Geist, Geist_Mono } from "next/font/google";
import Header from "@/components/header";
import JsonLd from "@/components/jsonLd";
import SiteFooter from "@/components/siteFooter";
import ConvexClientProvider from "../ConvexClientProvider";
import { FiltersProvider } from "@/src/features/common/context/filtersContext";
import { LanguageProvider } from "@/src/i18n";
import { isLocale } from "@/src/i18n/routing";
import { getTranslator, locales } from "@/src/i18n/translations";
import { organizationNode, webSiteNode } from "@/utils/jsonLd";
import {
  groupResortsByRegion,
  listPublishedResorts,
} from "@/utils/publishedResorts";
import { getSiteUrl, openGraphBase } from "@/utils/seo";

import "../globals.css";

// The footer fetches from Convex (`cache: "no-store"`); force-static keeps every
// route statically rendered and `revalidate` drives ISR. Pages may override.
export const dynamic = "force-static";
export const revalidate = 3600;

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

type LocaleParams = Promise<{ locale: string }>;

// Matches manifest.ts; colours the browser UI on mobile.
export const viewport: Viewport = {
  themeColor: "#4A6FA5",
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({
  params,
}: {
  params: LocaleParams;
}): Promise<Metadata> {
  const { locale } = await params;
  if (!isLocale(locale)) return {};
  const t = getTranslator(locale);

  return {
    metadataBase: new URL(getSiteUrl()),
    title: {
      default: t("siteTitle"),
      template: `%s | ${t("appName")}`,
    },
    description: t("siteDescription"),
    applicationName: t("appName"),
    // No title/description here: pages inherit their own via Next's metadata merge.
    openGraph: { ...openGraphBase(locale), type: "website" },
    twitter: { card: "summary_large_image" },
    verification: process.env.GOOGLE_SITE_VERIFICATION
      ? { google: process.env.GOOGLE_SITE_VERIFICATION }
      : undefined,
  };
}

export default async function RootLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: LocaleParams;
}>) {
  const { locale } = await params;
  if (!isLocale(locale)) notFound();
  const footerGroups = groupResortsByRegion(await listPublishedResorts());

  return (
    <html lang={locale}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <JsonLd nodes={[organizationNode(locale), webSiteNode(locale)]} />
        {/* Ads conversion tag: not needed for first paint, so load after window.load. */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=AW-18449858040"
          strategy="lazyOnload"
        />
        <Script id="google-ads-tag" strategy="lazyOnload">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'AW-18449858040');
          `}
        </Script>
        <ClerkProvider>
          <ConvexClientProvider>
            <LanguageProvider locale={locale}>
              <FiltersProvider>
                <div className="min-h-screen bg-background">
                  <Header />
                  {children}
                  <SiteFooter groups={footerGroups} />
                </div>
              </FiltersProvider>
            </LanguageProvider>
          </ConvexClientProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
