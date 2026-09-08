import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy | Ontario Ski Guide",
  description: "Privacy Policy for Ontario Ski Guide.",
};

export default function PrivacyPage() {
  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <article className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <Link href="/" className="text-sm text-primary hover:underline">
            Back to Ontario Ski Guide
          </Link>
          <h1 className="text-4xl font-bold tracking-tight">Privacy Policy</h1>
          <p className="text-sm text-muted-foreground">Last updated: September 8, 2026</p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">1. Scope</h2>
          <p>
            This Privacy Policy explains how Ontario Ski Guide handles information when you use
            the website.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">2. Information handled</h2>
          <ul className="list-disc space-y-2 pl-6">
            <li>
              Resort and location data retrieved from the application database to display search
              results.
            </li>
            <li>
              Your selected location stored in your browser&apos;s local storage so the site can
              preserve that preference.
            </li>
            <li>
              Approximate location information only when you grant browser location permission.
              This is used to suggest a nearby region.
            </li>
            <li>
              Information you choose to send when contacting support or providing feedback.
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">3. How information is used</h2>
          <p>
            Information is used to operate the resort directory, filter and sort results, suggest
            a location, respond to messages, protect the service, and improve reliability.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">4. Service providers</h2>
          <p>
            The website uses infrastructure and map services to provide its features. Those
            providers may process information under their own privacy policies. External resort,
            map, booking, and payment links are governed by the policies of the linked service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">5. Your choices</h2>
          <ul className="list-disc space-y-2 pl-6">
            <li>Decline browser location permission and choose a location manually.</li>
            <li>Clear the site&apos;s local storage through your browser settings.</li>
            <li>Contact support about a privacy request or question.</li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">6. Retention and security</h2>
          <p>
            Local preferences remain in your browser until you remove them. Information sent to
            support is retained only as needed to respond and maintain records. Reasonable
            safeguards are used, but no online service can guarantee absolute security.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">7. Children</h2>
          <p>
            The service is not directed to children under 13, and we do not knowingly collect
            personal information from children under 13.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">8. Policy changes</h2>
          <p>
            This policy may be updated as the service changes. The current version is always
            available on this page.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">9. Contact</h2>
          <p>
            Privacy questions: {" "}
            <a className="text-primary hover:underline" href="mailto:support@mywebsite.com">
              support@mywebsite.com
            </a>
            .
          </p>
        </section>
      </article>
    </main>
  );
}
