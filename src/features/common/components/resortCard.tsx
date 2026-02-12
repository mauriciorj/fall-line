import Image from "next/image";
import { Resort } from "@/types/resort";
import { RunBreakdown } from "./runBreakdown";
import { Star, Ticket, Package } from "lucide-react";
import { cn } from "@/utils/utils";
import { useRouter } from "next/navigation";

interface ResortCardProps {
  resort: Resort;
  isResortHoveredOrSelected: boolean;
  setHoveredResort: (id: string | null) => void;
}

export function ResortCard({
  resort,
  isResortHoveredOrSelected,
  setHoveredResort,
}: ResortCardProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push(`/place/${resort.id}`);
  };

  return (
    <article
      className={cn(
        "group bg-card rounded-lg overflow-hidden transition-all duration-300 cursor-pointer",
        "shadow-card hover:shadow-card-hover",
        isResortHoveredOrSelected &&
          "shadow-md shadow-primary ring-1 ring-primary"
      )}
      onMouseEnter={() => setHoveredResort(resort.id)}
      onMouseLeave={() => setHoveredResort(null)}
      onClick={handleClick}
    >
      {/* Hero Image */}
      <div className="relative aspect-[16/9] overflow-hidden">
        <Image
          src={resort.image}
          alt={resort.name}
          width={500}
          height={500}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-foreground/30 to-transparent" />
      </div>

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* Resort Name */}
        <h3 className="font-serif text-xl font-medium text-foreground leading-tight">
          {resort.name}
        </h3>

        {/* Run Breakdown */}
        <RunBreakdown
          green={resort.runs.green}
          blue={resort.runs.blue}
          black={resort.runs.black}
        />

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-3 pt-1">
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Ticket className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase tracking-wide">
                Lift Pass
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Package className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase tracking-wide">
                Ski Rental
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
          <div className="space-y-1 w-max">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Package className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase tracking-wide">
                Snowboard Rental
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.snowBoardRentalPrice}
            </p>
          </div>
          <div className="space-y-1 ml-12">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Star className="w-3.5 h-3.5" />
            </div>
            <p className="text-sm font-medium text-foreground">
              {resort.rating}
            </p>
          </div>
        </div>
      </div>
    </article>
  );
}
