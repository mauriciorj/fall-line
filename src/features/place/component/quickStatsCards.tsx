import Image from "next/image";
import { CableCar, Mountain } from "lucide-react";
import skiIcon from "@/icons/ski-svgrepo-com.svg";
import snowboardIcon from "@/icons/snowboard-1-svgrepo-com.svg";
import tubbingIcon from "@/icons/buoy-svgrepo-com.svg";
import { Resort } from "@/types/resort";
import TrackStats from "@/utils/trackStats";

const QuickStatsCards = (resort: Resort) => {
  const { totalTracks } = TrackStats({ resort });
  return (
    <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="flex flex-col justify-between bg-card rounded-lg p-5 border border-border">
        <div className="flex items-center gap-2 text-muted-foreground mb-2">
          <CableCar className="w-3.5 h-3.5" />
          <span className="text-xs uppercase tracking-wide">Lift Pass</span>
        </div>
        <p className="text-2xl font-medium text-foreground">
          ${resort.dayTicketPrice}
        </p>
      </div>
      <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
        <div className="flex items-center gap-2 text-muted-foreground mb-2">
          <Image alt="ski-icons" src={skiIcon} width={16} height={16} />
          <span className="text-xs uppercase tracking-wide">Ski Rental</span>
        </div>
        <p className="text-2xl font-medium text-foreground">
          ${resort.skiRentalPrice}
        </p>
      </div>
      <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
        <div className="flex items-center gap-2 text-muted-foreground mb-2">
          <Image alt="ski-icons" src={snowboardIcon} width={14} height={14} />
          <span className="text-xs uppercase tracking-wide">
            Snowboard Rental
          </span>
        </div>
        <p className="text-2xl font-medium text-foreground">
          ${resort.snowBoardRentalPrice}
        </p>
      </div>
      {Boolean(resort?.tubbingPrice && resort?.tubbingPrice > 0) && (
        <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
          <div className="flex items-center gap-2 text-muted-foreground mb-2">
            <Image alt="ski-icons" src={tubbingIcon} width={14} height={14} />
            <span className="text-xs uppercase tracking-wide">Tubbing</span>
          </div>
          <p className="text-2xl font-medium text-foreground">
            ${resort.tubbingPrice}
          </p>
        </div>
      )}
      <div className="flex flex-col justify-between  bg-card rounded-lg p-5 border border-border">
        <div className="flex items-center gap-2 text-muted-foreground mb-2">
          <Mountain className="w-4 h-4" />
          <span className="text-xs uppercase tracking-wide">Total Runs</span>
        </div>
        <p className="text-2xl font-medium text-foreground">{totalTracks}</p>
      </div>
    </section>
  );
};

export default QuickStatsCards;
