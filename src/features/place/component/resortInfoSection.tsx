import { useState } from "react";
import { Resort } from "@/types/resort";
import {
  Clock,
  Mail,
  Phone,
  Globe,
  Star,
  StarHalf,
  Snowflake,
  Map,
  ChevronDown,
} from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

interface ResortInfoSectionProps {
  resort: Resort;
}

function StarRating({ rating }: { rating: number }) {
  const fullStars = Math.floor(rating);
  const hasHalf = rating % 1 >= 0.5;
  return (
    <div className="flex items-center gap-1">
      {Array.from({ length: fullStars }).map((_, i) => (
        <Star key={i} className="w-4 h-4 fill-primary text-primary" />
      ))}
      {hasHalf && <StarHalf className="w-4 h-4 fill-primary text-primary" />}
      <span className="ml-1 text-sm font-medium text-foreground">{rating}</span>
    </div>
  );
}

export function ResortInfoSection({ resort }: ResortInfoSectionProps) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        Main Info
      </h2>
      <div className="bg-card rounded-lg border border-border divide-y divide-border">
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger className="w-full flex items-center justify-between p-5 hover:bg-muted/30 transition-colors">
            <div className="flex items-center gap-4">
              <Clock className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
              <div className="text-left">
                <p className="text-sm font-medium text-foreground">
                  Hours of Operation
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {resort?.trackConditions?.length} tracks
                </p>
              </div>
            </div>
            <ChevronDown
              className={`w-4 h-4 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
            />
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="px-5 pb-4 space-y-2">
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Sunday: {resort.hoursOfOperation.sunday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Monday: {resort.hoursOfOperation.monday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Tuesday: {resort.hoursOfOperation.tuesday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Wednesday: {resort.hoursOfOperation.wednesday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Thursday: {resort.hoursOfOperation.thursday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Friday: {resort.hoursOfOperation.friday}
                  </span>
                </div>
              </div>
              <div className="flex items-center justify-between py-2 px-3 rounded-md bg-muted/20">
                <div className="flex items-center gap-2.5">
                  <span className="text-sm text-foreground">
                    Saturday: {resort.hoursOfOperation.saturday}
                  </span>
                </div>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
        <div className="flex items-start gap-4 p-5">
          <Mail className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">Contact</p>
            <a
              href={`mailto:${resort.email}`}
              className="text-sm text-primary hover:underline block"
            >
              {resort.email}
            </a>
            <a
              href={`tel:${resort.phone}`}
              className="flex items-center gap-1 text-sm text-primary hover:underline"
            >
              <Phone className="w-3 h-3" />
              {resort.phone}
            </a>
          </div>
        </div>
        <div className="flex items-start gap-4 p-5">
          <Star className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
          <div>
            <p className="text-sm font-medium text-foreground mb-1">Rating</p>
            <StarRating rating={resort.rating} />
          </div>
        </div>
        <div className="flex items-start gap-4 p-5">
          <Globe className="w-4 h-4 mt-0.5 text-muted-foreground shrink-0" />
          <div>
            <p className="text-sm font-medium text-foreground">Website</p>
            <a
              href={resort.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              {resort.website}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
