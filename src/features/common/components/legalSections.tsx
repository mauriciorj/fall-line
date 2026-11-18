import { privacySections, termsSections } from "@fall-line/shared/content/legal";

export default function LegalSections({ page }: { page: "privacy" | "terms" }) {
  const sections = page === "privacy" ? privacySections("web") : termsSections;
  return sections.map((section) => (
    <section key={section.heading} className="space-y-3">
      <h2 className="text-2xl font-semibold">{section.heading}</h2>
      {section.paragraphs?.map((text) => <p key={text}>{text}</p>)}
      {section.items && (
        <ul className="list-disc space-y-2 pl-6">
          {section.items.map((text) => <li key={text}>{text}</li>)}
        </ul>
      )}
    </section>
  ));
}
