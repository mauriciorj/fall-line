import type { Metadata } from "next";
import Script from "next/script";
import { ClerkProvider } from "@clerk/nextjs";
import { Geist, Geist_Mono } from "next/font/google";
import Header from "@/components/header";
import ConvexClientProvider from "./ConvexClientProvider";
import { FiltersProvider } from "@/src/features/common/context/filtersContext";
import { LanguageProvider } from "@/src/i18n";
import {
  SITE_DESCRIPTION,
  SITE_NAME,
  SITE_TITLE,
  baseOpenGraph,
  getSiteUrl,
} from "@/utils/seo";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(getSiteUrl()),
  title: {
    default: SITE_TITLE,
    template: `%s | ${SITE_NAME}`,
  },
  description: SITE_DESCRIPTION,
  applicationName: SITE_NAME,
  // No title/description here: pages inherit their own via Next's metadata merge.
  openGraph: { ...baseOpenGraph, type: "website" },
  twitter: { card: "summary_large_image" },
  verification: process.env.GOOGLE_SITE_VERIFICATION
    ? { google: process.env.GOOGLE_SITE_VERIFICATION }
    : undefined,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=AW-18449858040"
          strategy="afterInteractive"
        />
        <Script id="google-ads-tag" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'AW-18449858040');
          `}
        </Script>
        <ClerkProvider>
          <ConvexClientProvider>
            <LanguageProvider>
              <FiltersProvider>
                <div className="min-h-screen bg-background">
                  <Header />
                  {children}
                </div>
              </FiltersProvider>
            </LanguageProvider>
          </ConvexClientProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
