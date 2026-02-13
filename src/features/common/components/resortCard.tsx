import Image from "next/image";
import { useRouter } from "next/navigation";
import { Resort } from "@/types/resort";
import { RunBreakdown } from "./runBreakdown";
import { Star, CableCar } from "lucide-react";
import { AmenitiesList } from "@/components/amenitiesList";
import { cn } from "@/utils/utils";

import skiIcon from "@/icons/ski-svgrepo-com.svg";
import snowboardIcon from "@/icons/snowboard-1-svgrepo-com.svg";
import tubbingIcon from "@/icons/buoy-svgrepo-com.svg";

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
        <div className="w-full flex flex-row justify-between">
          <h3 className="font-serif text-xl font-medium text-foreground leading-tight">
            {resort.name}
          </h3>
          <div className="flex flex-row justify-center items-center">
            <Star className="w-3.5 h-3.5" />
            <p className="text-sm font-medium text-foreground ml-1">
              {resort.rating}
            </p>
          </div>
        </div>

        <AmenitiesList resort={resort} />

        {/* Run Breakdown */}
        <RunBreakdown
          green={resort.runs.green}
          blue={resort.runs.blue}
          black={resort.runs.black}
        />

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-3 pt-1">
          <div className="flex flex-col justify-between space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <CableCar className="w-3.5 h-3.5" />
              <span className="text-[10px] uppercase tracking-wide">
                Lift Pass
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
          <div className="flex flex-col justify-between space-y-1">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Image alt="ski-icons" src={skiIcon} width={16} height={16} />
              <span className="text-[10px] uppercase tracking-wide">
                Ski Rental
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
          <div className="flex flex-col justify-between space-y-1 w-max">
            <div className="flex items-center gap-1 text-muted-foreground">
              <Image
                alt="ski-icons"
                src={snowboardIcon}
                width={14}
                height={14}
              />
              <span className="text-[10px] uppercase tracking-wide">
                Snowboard Rental
              </span>
            </div>
            <p className="text-sm font-medium text-foreground">
              ${resort.snowBoardRentalPrice}
            </p>
          </div>
          {Boolean(resort?.tubbingPrice && resort?.tubbingPrice > 0) && (
            <div className="flex flex-col justify-between space-y-1 ml-12">
              <div className="flex items-center gap-1 text-muted-foreground">
                <Image
                  alt="ski-icons"
                  src={tubbingIcon}
                  width={14}
                  height={14}
                />
                <span className="text-[10px] uppercase tracking-wide">
                  Tubbing
                </span>
              </div>
              <p className="text-sm font-medium text-foreground">
                ${resort.tubbingPrice}
              </p>
            </div>
          )}
        </div>
      </div>
    </article>
  );
}
