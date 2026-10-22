import type { JsonLdNode } from "@/components/jsonLd";
import { intlLocale, localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import type { FaqItem, Resort, ResortHourSection } from "@/types/resort";
import { getResortHeroImage } from "@/utils/convexResort";
import { DEFAULT_OG_IMAGE, absoluteUrl, getSiteUrl } from "@/utils/seo";

const ORGANIZATION_ID = () => `${getSiteUrl()}/#organization`;

const countryCodes: Record<string, string> = {
  Canada: "CA",
  "United States": "US",
};

export function organizationNode(locale: Locale): JsonLdNode {
  const t = getTranslator(locale);
  return {
    "@type": "Organization",
    "@id": ORGANIZATION_ID(),
    name: t("appName"),
    url: getSiteUrl(),
    logo: {
      "@type": "ImageObject",
      url: absoluteUrl(DEFAULT_OG_IMAGE),
      width: 1200,
      height: 630,
    },
  };
}

export function webSiteNode(locale: Locale): JsonLdNode {
  const t = getTranslator(locale);
  return {
    "@type": "WebSite",
    "@id": `${getSiteUrl()}/#website`,
    url: absoluteUrl(localizePath("/", locale)),
    name: t("appName"),
    description: t("siteDescription"),
    inLanguage: intlLocale[locale],
    publisher: { "@id": ORGANIZATION_ID() },
  };
}

// Freshness lives on the page node: Place types have no dateModified.
export function webPageNode(
  locale: Locale,
  options: { url: string; name: string; mainEntityId: string; dateModified?: number | null },
): JsonLdNode {
  return {
    "@type": "WebPage",
    "@id": options.url,
    url: options.url,
    name: options.name,
    inLanguage: intlLocale[locale],
    isPartOf: { "@id": `${getSiteUrl()}/#website` },
    mainEntity: { "@id": options.mainEntityId },
    ...(options.dateModified
      ? { dateModified: new Date(options.dateModified).toISOString() }
      : {}),
  };
}

export function breadcrumbNode(
  items: { name: string; path?: string }[],
  locale: Locale,
): JsonLdNode {
  return {
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      ...(item.path ? { item: absoluteUrl(localizePath(item.path, locale)) } : {}),
    })),
  };
}

export function itemListNode(
  name: string,
  items: { name: string; path: string }[],
  locale: Locale,
): JsonLdNode {
  return {
    "@type": "ItemList",
    name,
    numberOfItems: items.length,
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      url: absoluteUrl(localizePath(item.path, locale)),
    })),
  };
}

export function faqNode(faq: FaqItem[]): JsonLdNode {
  return {
    "@type": "FAQPage",
    mainEntity: faq.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: { "@type": "Answer", text: item.answer },
    })),
  };
}

const weekdays: Record<string, string> = {
  monday: "Monday",
  tuesday: "Tuesday",
  wednesday: "Wednesday",
  thursday: "Thursday",
  friday: "Friday",
  saturday: "Saturday",
  sunday: "Sunday",
};

function to24h(hour: string, minute: string | undefined, meridiem: string | undefined) {
  let value = Number(hour);
  const suffix = meridiem?.toLowerCase();
  if (suffix === "pm" && value < 12) value += 12;
  if (suffix === "am" && value === 12) value = 0;
  if (value > 23) return null;
  return `${String(value).padStart(2, "0")}:${minute ?? "00"}`;
}

// Emits only rows that parse unambiguously; anything else is left out rather
// than guessed. "closed" uses Google's 00:00–00:00 convention.
export function openingHoursNodes(sections: ResortHourSection[]): JsonLdNode[] {
  const rows =
    sections.find((section) => section.hours?.length)?.hours ?? [];
  const range =
    /^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*(?:-|–|to|à|a)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$/i;

  return rows.flatMap((row) => {
    const dayOfWeek = weekdays[row.day.trim().toLowerCase()];
    if (!dayOfWeek) return [];
    const time = row.time.trim().toLowerCase();
    if (time === "closed" || time === "fermé" || time === "cerrado") {
      return [{ "@type": "OpeningHoursSpecification", dayOfWeek, opens: "00:00", closes: "00:00" }];
    }
    const match = time.match(range);
    if (!match) return [];
    const [, h1, m1, md1, h2, m2, md2] = match;
    // "9 - 4 pm": a missing first meridiem inherits the second one.
    const opens = to24h(h1, m1, md1 ?? md2);
    const closes = to24h(h2, m2, md2);
    if (!opens || !closes) return [];
    return [{ "@type": "OpeningHoursSpecification", dayOfWeek, opens, closes }];
  });
}

export function skiResortNode(
  resort: Resort,
  locale: Locale,
  options: { pageUrl: string; description: string; hours: ResortHourSection[] },
): JsonLdNode {
  const t = getTranslator(locale);
  const offer = (name: string, price: number, url?: string) =>
    price > 0
      ? { "@type": "Offer", name, price, priceCurrency: "CAD", ...(url ? { url } : {}) }
      : null;
  const amenities: [boolean, string][] = [
    [resort.hasTubing, "tubbing"],
    [resort.hasLessons, "lessons"],
    [resort.hasAccommodations, "accommodations"],
    [resort.hasCrossCountry, "crossCountry"],
    [resort.hasIceSkate, "iceSkating"],
    [resort.hasSnowshoeing, "snowshoeing"],
    [resort.hasSpa, "spa"],
  ];
  const totalRuns =
    resort.runs.green +
    resort.runs.blue +
    resort.runs.black +
    resort.runs.doubleBlack +
    (resort.runs.freeStyle ?? 0);
  const hours = openingHoursNodes(options.hours);
  const sameAs = [resort.website, resort.googleMapsUrl].filter(Boolean);

  // No aggregateRating on purpose: the stored rating is scraped and has no review count.
  return {
    "@type": "SkiResort",
    "@id": `${options.pageUrl}#resort`,
    name: resort.name,
    description: options.description,
    url: resort.website || options.pageUrl,
    mainEntityOfPage: options.pageUrl,
    image: absoluteUrl(getResortHeroImage(resort.resortId, resort.country, resort.region)),
    ...(resort.phone ? { telephone: resort.phone } : {}),
    ...(resort.email ? { email: resort.email } : {}),
    ...(resort.address
      ? {
          address: {
            "@type": "PostalAddress",
            streetAddress: resort.address,
            ...(resort.region ? { addressRegion: resort.region } : {}),
            ...(resort.country
              ? { addressCountry: countryCodes[resort.country] ?? resort.country }
              : {}),
          },
        }
      : {}),
    ...(resort.coordinates
      ? {
          geo: {
            "@type": "GeoCoordinates",
            latitude: resort.coordinates.lat,
            longitude: resort.coordinates.lng,
          },
        }
      : {}),
    ...(resort.googleMapsUrl ? { hasMap: resort.googleMapsUrl } : {}),
    ...(sameAs.length ? { sameAs } : {}),
    ...(hours.length ? { openingHoursSpecification: hours } : {}),
    makesOffer: [
      offer(t("liftPass"), resort.dayTicketPrice, resort.ticketUrl),
      offer(t("skiRental"), resort.skiRentalPrice),
      offer(t("snowboardRental"), resort.snowBoardRentalPrice),
      offer(t("lessons"), resort.lessonsPrice),
      offer(t("tubbing"), resort.tubbingPrice ?? 0),
    ].filter(Boolean),
    amenityFeature: amenities
      .filter(([enabled]) => enabled)
      .map(([, key]) => ({
        "@type": "LocationFeatureSpecification",
        name: t(key),
        value: true,
      })),
    additionalProperty: [
      totalRuns > 0 && { "@type": "PropertyValue", name: t("totalRuns"), value: totalRuns },
      resort.height && { "@type": "PropertyValue", name: t("height"), value: resort.height },
      resort.elevation && { "@type": "PropertyValue", name: t("elevation"), value: resort.elevation },
    ].filter(Boolean),
  };
}

export function blogPostingNode(
  article: {
    title: string;
    description: string;
    tags: string[];
    publishedAt: number;
    updatedAt: number;
    heroImageUrl?: string | null;
  },
  pageUrl: string,
): JsonLdNode {
  return {
    "@type": "BlogPosting",
    "@id": `${pageUrl}#article`,
    headline: article.title,
    description: article.description,
    image: article.heroImageUrl ?? absoluteUrl(DEFAULT_OG_IMAGE),
    datePublished: new Date(article.publishedAt).toISOString(),
    dateModified: new Date(article.updatedAt).toISOString(),
    // Articles are authored in English only (see blog metadata).
    inLanguage: "en-CA",
    mainEntityOfPage: pageUrl,
    ...(article.tags.length ? { keywords: article.tags.join(", ") } : {}),
    author: { "@id": ORGANIZATION_ID() },
    publisher: { "@id": ORGANIZATION_ID() },
  };
}
