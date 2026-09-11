"use client";

import { CircleDot, GraduationCap } from "lucide-react";
import { useLanguage } from "@/src/i18n";
import { Resort } from "@/types/resort";

const PricingSection = ({ resort }: { resort: Resort }) => {
  const { t } = useLanguage();

  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        {t("pricing")}
      </h2>
      <div className="bg-card rounded-lg border border-border divide-y divide-border">
        {Boolean(resort?.dayTicketPrice && resort.dayTicketPrice > 0) && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">{t("liftPass")}</p>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
        )}
        {Boolean(resort?.skiRentalPrice && resort.skiRentalPrice > 0) && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">{t("skiRental")}</p>
              {/* <p className="text-sm text-muted-foreground">Skis with boots</p> */}
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
        )}
        {Boolean(
          resort?.snowBoardRentalPrice && resort.snowBoardRentalPrice > 0,
        ) && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">{t("snowboardRental")}</p>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.snowBoardRentalPrice}
            </p>
          </div>
        )}
        {Boolean(resort?.lessonsPrice && resort.lessonsPrice > 0) && (
          <div className="flex items-center justify-between p-5">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="font-medium text-foreground">{t("lessons")}</p>
              </div>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.lessonsPrice}
            </p>
          </div>
        )}
        {Boolean(resort?.tubbingPrice && resort.tubbingPrice > 0) && (
          <div className="flex items-center justify-between p-5">
            <div className="flex items-center gap-2">
              <CircleDot className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="font-medium text-foreground">{t("tubbing")}</p>
              </div>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.tubbingPrice}
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default PricingSection;
