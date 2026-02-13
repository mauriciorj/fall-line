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
    <div className="flex flex-row flex-wrap">
      {resort.hasAccommodations && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[10px] font-medium gap-1 px-2 py-0.5"
          >
            <Hotel className="w-3 h-3" />
            Accommodations
          </Badge>
        </div>
      )}
      {resort.hasCrossCountry && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[10px] font-medium gap-1 px-2 py-0.5"
          >
            <Trees className="w-3 h-3" />
            Cross Country
          </Badge>
        </div>
      )}
      {resort.hasLessons && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[10px] font-medium gap-1 px-2 py-0.5"
          >
            <GraduationCap className="w-3 h-3" />
            Lessons
          </Badge>
        </div>
      )}
      {resort.hasSnowshoeing && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[10px] font-medium gap-1 px-2 py-0.5"
          >
            <Footprints className="w-3 h-3" />
            Snowshoeing
          </Badge>
        </div>
      )}
      {resort.hasSpa && (
        <div className="ml-1">
          <Badge
            variant="secondary"
            className="text-[10px] font-medium gap-1 px-2 py-0.5"
          >
            <Sparkles className="w-3 h-3" />
            Spa
          </Badge>
        </div>
      )}
    </div>
  );
}
