import { ArrowLeft, MapPin } from "lucide-react";
import { Resort } from "@/types/resort";

const LocationSection = ({ resort }: { resort: Resort }) => {
  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        Location
      </h2>
      <div className="bg-card rounded-lg p-6 border border-border">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-full bg-primary/10">
            <MapPin className="w-5 h-5 text-primary" />
          </div>
          <div className="space-y-1">
            <p className="font-medium text-foreground">
              Address: {resort.address}
            </p>
            <a
              href={resort.googleMapsUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-sm text-primary hover:underline mt-2"
            >
              Get directions
              <ArrowLeft className="w-3 h-3 rotate-[135deg]" />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default LocationSection;
