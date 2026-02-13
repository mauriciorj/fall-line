import { Resort } from "@/types/resort";
import {
  Hotel,
  Trees,
  Sparkles,
  GraduationCap,
  Footprints,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ActivitiesListProps {
  resort: Resort;
}

export function ActivitiesList({ resort }: ActivitiesListProps) {
  return (
    <div className="flex flex-row flex-wrap gap-1">
      {resort.hasAccommodations && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[12px] font-medium gap-1 px-2 py-0.5"
          >
            <Hotel className="w-4 h-4" />
            Accommodations
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
            Cross Country
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
            Lessons
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
            Snowshoeing
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
            Spa
          </Badge>
        </div>
      )}
    </div>
  );
}
