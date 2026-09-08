"use client";

import {
  Footprints,
  GraduationCap,
  Hotel,
  Sparkles,
  Trees,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Resort } from "@/types/resort";
import { useLanguage } from "@/src/i18n";

interface ActivitiesListProps {
  resort: Resort;
}

const ActivitiesList = ({ resort }: ActivitiesListProps) => {
  const { t } = useLanguage();

  return (
    <div className="flex flex-row flex-wrap gap-1">
      {resort.hasAccommodations && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <Hotel className="w-4 h-4" />
            {t("accommodations")}
          </Badge>
        </div>
      )}
      {resort.hasCrossCountry && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <Trees className="w-4 h-4" />
            {t("crossCountry")}
          </Badge>
        </div>
      )}
      {resort.hasLessons && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <GraduationCap className="w-4 h-4" />
            {t("lessons")}
          </Badge>
        </div>
      )}
      {resort.hasSnowshoeing && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <Footprints className="w-4 h-4" />
            {t("snowshoeing")}
          </Badge>
        </div>
      )}
      {resort.hasSpa && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <Sparkles className="w-4 h-4" />
            {t("spa")}
          </Badge>
        </div>
      )}
    </div>
  );
};

export default ActivitiesList;
