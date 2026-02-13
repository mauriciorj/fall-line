import { CircleDot, GraduationCap } from "lucide-react";
import { Resort } from "@/types/resort";

const PricingSection = ({ resort }: { resort: Resort }) => {
  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        Pricing
      </h2>
      <div className="bg-card rounded-lg border border-border divide-y divide-border">
        <div className="flex items-center justify-between p-5">
          <div>
            <p className="font-medium text-foreground">Lift Pass</p>
            {/* <p className="text-sm text-muted-foreground">
                  Lift access
                </p> */}
          </div>
          <p className="text-xl font-medium text-foreground">
            ${resort.dayTicketPrice}
          </p>
        </div>
        <div className="flex items-center justify-between p-5">
          <div>
            <p className="font-medium text-foreground">Ski Rental</p>
            {/* <p className="text-sm text-muted-foreground">Skis with boots</p> */}
          </div>
          <p className="text-xl font-medium text-foreground">
            ${resort.skiRentalPrice}
          </p>
        </div>
        <div className="flex items-center justify-between p-5">
          <div>
            <p className="font-medium text-foreground">Snowboard Rental</p>
            {/* <p className="text-sm text-muted-foreground">
                  Snowboard with boots
                </p> */}
          </div>
          <p className="text-xl font-medium text-foreground">
            ${resort.snowBoardRentalPrice}
          </p>
        </div>
        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="font-medium text-foreground">Lessons</p>
              {/* <p className="text-sm text-muted-foreground">
                    Group lesson (2 hours)
                  </p> */}
            </div>
          </div>
          <p className="text-xl font-medium text-foreground">
            ${resort.lessonsPrice}
          </p>
        </div>
        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-2">
            <CircleDot className="w-4 h-4 text-muted-foreground" />
            <div>
              <p className="font-medium text-foreground">Tubing</p>
              {/* <p className="text-sm text-muted-foreground">
                    Full day snow tubing pass
                  </p> */}
            </div>
          </div>
          <p className="text-xl font-medium text-foreground">
            ${resort?.tubbingPrice}
          </p>
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
