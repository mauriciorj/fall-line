import { Resort } from "@/types/resort";
import { MapPin } from "lucide-react";
import { cn } from "@/utils/utils";

interface StaticMapProps {
  resorts: Resort[];
  hoveredResort: string | null;
  onMarkerHover: (id: string | null) => void;
}

// Simple static map visualization without Google Maps API
export function StaticMap({
  resorts,
  hoveredResort,
  onMarkerHover,
}: StaticMapProps) {
  // Convert lat/lng to approximate pixel positions
  // Ontario roughly spans lat 42-51, lng -95 to -74
  const latToY = (lat: number) => {
    const minLat = 42;
    const maxLat = 51;
    return ((maxLat - lat) / (maxLat - minLat)) * 100;
  };

  const lngToX = (lng: number) => {
    const minLng = -95;
    const maxLng = -74;
    return ((lng - minLng) / (maxLng - minLng)) * 100;
  };

  return (
    <div className="w-full h-full bg-secondary relative overflow-hidden">
      {/* Decorative map background */}
      <div className="absolute inset-0">
        {/* Water bodies hint */}
        <div className="absolute top-[10%] right-[5%] w-[25%] h-[30%] bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute top-[40%] left-[10%] w-[20%] h-[20%] bg-primary/5 rounded-full blur-2xl" />

        {/* Grid lines */}
        <svg className="absolute inset-0 w-full h-full opacity-20">
          <defs>
            <pattern
              id="grid"
              width="50"
              height="50"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 50 0 L 0 0 0 50"
                fill="none"
                stroke="currentColor"
                strokeWidth="0.5"
                className="text-border"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Map title */}
      <div className="absolute top-4 left-4 z-10">
        <div className="bg-card/80 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-border">
          <p className="text-xs font-medium text-foreground">Ontario, Canada</p>
          <p className="text-[10px] text-muted-foreground">
            {resorts.length} resorts
          </p>
        </div>
      </div>

      {/* Resort markers */}
      {resorts.map((resort) => {
        const x = lngToX(resort.coordinates.lng);
        const y = latToY(resort.coordinates.lat);
        const isHovered = hoveredResort === resort.id;

        return (
          <div
            key={resort.id}
            className="absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-200"
            style={{ left: `${x}%`, top: `${y}%` }}
            onMouseEnter={() => onMarkerHover(resort.id)}
            onMouseLeave={() => onMarkerHover(null)}
          >
            {/* Tooltip */}
            <div
              className={cn(
                "absolute bottom-full left-1/2 -translate-x-1/2 mb-2 transition-all duration-200",
                isHovered
                  ? "opacity-100 translate-y-0"
                  : "opacity-0 translate-y-1 pointer-events-none"
              )}
            >
              <div className="bg-card rounded-lg shadow-card-hover px-3 py-2 border border-border whitespace-nowrap">
                <p className="font-serif text-sm font-medium text-foreground">
                  {resort.name}
                </p>
                {/* <p className="text-xs text-muted-foreground">
                  ${resort.dayTicketPrice}/day · {resort.distance} km
                </p> */}
              </div>
              {/* Arrow */}
              <div className="absolute top-full left-1/2 -translate-x-1/2 -translate-y-px">
                <div className="w-2 h-2 bg-card border-r border-b border-border rotate-45" />
              </div>
            </div>

            {/* Pin */}
            <button
              className={cn(
                "flex items-center justify-center rounded-full transition-all duration-200 cursor-pointer",
                isHovered
                  ? "w-10 h-10 bg-primary shadow-lg ring-4 ring-primary/20"
                  : "w-8 h-8 bg-muted-foreground/80 shadow-card hover:bg-primary"
              )}
            >
              <MapPin
                className={cn(
                  "transition-all duration-200 text-card",
                  isHovered ? "w-5 h-5" : "w-4 h-4"
                )}
              />
            </button>
          </div>
        );
      })}

      {/* Legend */}
      <div className="absolute bottom-4 right-4 z-10">
        <div className="bg-card/80 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-border">
          <p className="text-[10px] text-muted-foreground">
            Hover on cards to highlight
          </p>
        </div>
      </div>
    </div>
  );
}
