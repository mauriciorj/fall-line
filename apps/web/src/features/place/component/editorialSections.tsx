"use client";

import { useLanguage } from "@/src/i18n";
import { pickLocalized } from "@/src/i18n/localized";
import { Resort } from "@/types/resort";

// Editorial content is authored per locale in the admin; missing locales fall
// back to English and are marked with `lang` so the fallback is honest.
export function AboutSection({ resort }: { resort: Resort }) {
  const { locale, t } = useLanguage();
  const description = pickLocalized(resort.description, locale);
  if (!description) return null;

  const paragraphs = description.value
    .split(/\n\s*\n/)
    .map((paragraph) => paragraph.trim())
    .filter(Boolean);

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("aboutTitle", { name: resort.name })}
      </h2>
      <div
        lang={description.lang === locale ? undefined : description.lang}
        className="space-y-3 text-foreground/90 leading-relaxed"
      >
        {paragraphs.map((paragraph, index) => (
          <p key={index}>{paragraph}</p>
        ))}
      </div>
    </section>
  );
}

export function HighlightsSection({ resort }: { resort: Resort }) {
  const { locale, t } = useLanguage();
  const highlights = pickLocalized(resort.highlights, locale);
  if (!highlights) return null;

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("highlightsTitle")}
      </h2>
      <ul
        lang={highlights.lang === locale ? undefined : highlights.lang}
        className="grid gap-2 rounded-lg border border-border bg-card p-6 sm:grid-cols-2"
      >
        {highlights.value.map((highlight) => (
          <li key={highlight} className="flex gap-2 text-sm text-foreground">
            <span aria-hidden="true" className="text-primary">
              •
            </span>
            {highlight}
          </li>
        ))}
      </ul>
    </section>
  );
}

// Questions and answers stay visible (no accordion): required for FAQ rich
// results and for crawlers that don't execute JavaScript.
export function FaqSection({ resort }: { resort: Resort }) {
  const { locale, t } = useLanguage();
  const faq = pickLocalized(resort.faq, locale);
  if (!faq) return null;

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("faqTitle")}
      </h2>
      <dl
        lang={faq.lang === locale ? undefined : faq.lang}
        className="divide-y divide-border rounded-lg border border-border bg-card"
      >
        {faq.value.map((item) => (
          <div key={item.question} className="space-y-2 p-5">
            <dt className="font-medium text-foreground">{item.question}</dt>
            <dd className="text-sm leading-relaxed text-foreground/90">
              {item.answer}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
