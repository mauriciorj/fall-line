import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Contact Us | Ontario Ski Guide",
  description: "Contact Ontario Ski Guide for questions, feedback, and support.",
};

export default function ContactPage() {
  return (
    <main className="min-h-[calc(100vh-57px)] bg-background px-6 py-10">
      <article className="mx-auto max-w-3xl space-y-8 text-foreground">
        <header className="space-y-3">
          <Link href="/" className="text-sm text-primary hover:underline">
            Back to Ontario Ski Guide
          </Link>
          <h1 className="text-4xl font-bold tracking-tight">Contact Us</h1>
          <p className="text-sm text-muted-foreground">Questions, feedback, or support.</p>
        </header>

        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Get in touch</h2>
          <p>
            Contact us about resort information, corrections, feedback, or help using Ontario Ski
            Guide.
          </p>
          <p>
            Email: {" "}
            <a className="text-primary hover:underline" href="mailto:support@mywebsite.com">
              support@mywebsite.com
            </a>
          </p>
        </section>
      </article>
    </main>
  );
}
