"use client";

import { ExternalLink } from "lucide-react";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

const AccommodationsSection = ({ resort }: { resort: Resort }) => {
  const { t } = useLanguage();

  if (!resort.resort_accommodations) return null;

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("accommodations")}
      </h2>
      <div className="bg-card rounded-lg p-6 border border-border">
        <a
          href={resort.resort_accommodations}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
        >
          {t("accommodations")}
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
    </section>
  );
};

export default AccommodationsSection;
