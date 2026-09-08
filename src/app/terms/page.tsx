import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Service | Ontario Ski Guide",
  description: "Terms of Service for Ontario Ski Guide.",
};

export default function TermsPage() {
  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <article className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <Link href="/" className="text-sm text-primary hover:underline">
            Back to Ontario Ski Guide
          </Link>
          <h1 className="text-4xl font-bold tracking-tight">Terms of Service</h1>
          <p className="text-sm text-muted-foreground">Last updated: September 8, 2026</p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">1. Acceptance</h2>
          <p>
            By using Ontario Ski Guide, you agree to these Terms of Service. If you do not agree,
            do not use the service.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">2. Service purpose</h2>
          <p>
            Ontario Ski Guide provides resort information, conditions, prices, hours, maps, and
            related links for general informational and trip-planning purposes.
          </p>
          <p>
            Resort information can change without notice. Confirm prices, schedules, closures,
            availability, and restrictions with the resort before travelling.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">3. Acceptable use</h2>
          <p>
            Use the service lawfully. Do not interfere with the service, attempt unauthorized
            access, scrape or overload systems, or use displayed information to create safety risks.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">4. Third-party services and links</h2>
          <p>
            The service may display information from resorts and link to third-party websites,
            maps, booking systems, and payment providers. Third-party services have their own
            terms and privacy policies. Ontario Ski Guide does not control or guarantee them.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">5. No warranty</h2>
          <p>
            The service is provided on an as-is and as-available basis. To the extent permitted by
            law, Ontario Ski Guide disclaims warranties about accuracy, availability, suitability,
            or uninterrupted operation.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">6. Limitation of liability</h2>
          <p>
            To the extent permitted by law, Ontario Ski Guide is not responsible for losses,
            injuries, missed reservations, costs, or damages arising from reliance on displayed
            information or use of linked third-party services.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">7. Changes</h2>
          <p>
            These terms may be updated from time to time. The updated version takes effect when it
            is published on this page.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">8. Contact</h2>
          <p>
            Questions about these terms: {" "}
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
