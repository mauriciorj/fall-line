import type { MetadataRoute } from "next";
import { intlLocale } from "@/src/i18n/routing";
import { defaultLocale, getTranslator } from "@/src/i18n/translations";

export default function manifest(): MetadataRoute.Manifest {
  const t = getTranslator(defaultLocale);

  return {
    name: t("appName"),
    short_name: t("appName"),
    description: t("siteDescription"),
    lang: intlLocale[defaultLocale],
    start_url: "/",
    display: "minimal-ui",
    background_color: "#ffffff",
    theme_color: "#4A6FA5",
    icons: [
      { src: "/icons/icon-192.png", sizes: "192x192", type: "image/png" },
      { src: "/icons/icon-512.png", sizes: "512x512", type: "image/png" },
      {
        src: "/icons/icon-512-maskable.png",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
