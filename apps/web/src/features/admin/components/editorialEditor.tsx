"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Locale, locales } from "@/src/i18n/translations";
import type { FaqItem, LocalizedFaq, LocalizedStrings, LocalizedText } from "@/types/resort";

export type EditorialDraft = {
  description: Partial<Record<Locale, string>>;
  // One highlight per line while editing.
  highlights: Partial<Record<Locale, string>>;
  faq: Partial<Record<Locale, FaqItem[]>>;
};

export const emptyEditorial: EditorialDraft = { description: {}, highlights: {}, faq: {} };

export function toEditorialDraft(resort: {
  description?: LocalizedText;
  highlights?: LocalizedStrings;
  faq?: LocalizedFaq;
}): EditorialDraft {
  return {
    description: { ...resort.description },
    highlights: Object.fromEntries(
      locales.map((locale) => [locale, (resort.highlights?.[locale] ?? []).join("\n")]),
    ),
    faq: Object.fromEntries(locales.map((locale) => [locale, resort.faq?.[locale] ?? []])),
  };
}

// Convex drops `undefined` object fields, so empty locales simply disappear.
export function fromEditorialDraft(draft: EditorialDraft) {
  const clean = (value?: string) => value?.trim() || undefined;
  return {
    description: Object.fromEntries(locales.map((locale) => [locale, clean(draft.description[locale])])),
    highlights: Object.fromEntries(
      locales.map((locale) => {
        const items = (draft.highlights[locale] ?? "").split("\n").map((line) => line.trim()).filter(Boolean);
        return [locale, items.length ? items : undefined];
      }),
    ),
    faq: Object.fromEntries(
      locales.map((locale) => {
        const items = (draft.faq[locale] ?? [])
          .map((item) => ({ question: item.question.trim(), answer: item.answer.trim() }))
          .filter((item) => item.question && item.answer);
        return [locale, items.length ? items : undefined];
      }),
    ),
  };
}

export default function EditorialEditor({
  value,
  onChange,
}: {
  value: EditorialDraft;
  onChange: (value: EditorialDraft) => void;
}) {
  const updateFaq = (locale: Locale, items: FaqItem[]) =>
    onChange({ ...value, faq: { ...value.faq, [locale]: items } });

  return (
    <div className="space-y-6 md:col-span-2">
      {locales.map((locale) => {
        const faq = value.faq[locale] ?? [];
        return (
          <fieldset key={locale} className="space-y-3 rounded-lg border border-border p-4">
            <legend className="px-1 text-sm font-semibold uppercase tracking-wide">{locale}</legend>
            <label className="block text-sm">
              Description
              <Textarea
                className="mt-1"
                rows={6}
                value={value.description[locale] ?? ""}
                placeholder="Editorial description (blank line = new paragraph). 150–400 words."
                onChange={(event) =>
                  onChange({ ...value, description: { ...value.description, [locale]: event.target.value } })
                }
              />
            </label>
            <label className="block text-sm">
              Highlights (one per line)
              <Textarea
                className="mt-1"
                rows={4}
                value={value.highlights[locale] ?? ""}
                onChange={(event) =>
                  onChange({ ...value, highlights: { ...value.highlights, [locale]: event.target.value } })
                }
              />
            </label>
            <div className="space-y-2">
              <p className="text-sm">FAQ</p>
              {faq.map((item, index) => (
                <div key={index} className="grid gap-2 rounded-md border border-border p-3">
                  <Input
                    placeholder="Question"
                    value={item.question}
                    onChange={(event) =>
                      updateFaq(locale, faq.map((entry, i) => (i === index ? { ...entry, question: event.target.value } : entry)))
                    }
                  />
                  <Textarea
                    placeholder="Answer"
                    rows={3}
                    value={item.answer}
                    onChange={(event) =>
                      updateFaq(locale, faq.map((entry, i) => (i === index ? { ...entry, answer: event.target.value } : entry)))
                    }
                  />
                  <Button type="button" variant="outline" size="sm" onClick={() => updateFaq(locale, faq.filter((_, i) => i !== index))}>
                    Remove question
                  </Button>
                </div>
              ))}
              <Button type="button" variant="outline" size="sm" onClick={() => updateFaq(locale, [...faq, { question: "", answer: "" }])}>
                Add question
              </Button>
            </div>
          </fieldset>
        );
      })}
    </div>
  );
}
