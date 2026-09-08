import { CircleDot, GraduationCap } from "lucide-react";
import { Resort } from "@/types/resort";

const PricingSection = ({ resort }: { resort: Resort }) => {
  return (
    <section className="space-y-4">
      <h2 className="font-serif text-xl font-medium text-foreground">
        Pricing
      </h2>
      <div className="bg-card rounded-lg border border-border divide-y divide-border">
        {resort?.dayTicketPrice && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">Lift Pass</p>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.dayTicketPrice}
            </p>
          </div>
        )}
        {resort?.skiRentalPrice && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">Ski Rental</p>
              {/* <p className="text-sm text-muted-foreground">Skis with boots</p> */}
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.skiRentalPrice}
            </p>
          </div>
        )}
        {resort?.snowBoardRentalPrice && (
          <div className="flex items-center justify-between p-5">
            <div>
              <p className="font-medium text-foreground">Snowboard Rental</p>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.snowBoardRentalPrice}
            </p>
          </div>
        )}
        {resort?.lessonsPrice && (
          <div className="flex items-center justify-between p-5">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="font-medium text-foreground">Lessons</p>
              </div>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.lessonsPrice}
            </p>
          </div>
        )}
        {resort?.tubbingPrice && (
          <div className="flex items-center justify-between p-5">
            <div className="flex items-center gap-2">
              <CircleDot className="w-4 h-4 text-muted-foreground" />
              <div>
                <p className="font-medium text-foreground">Tubing</p>
              </div>
            </div>
            <p className="text-xl font-medium text-foreground">
              ${resort.tubbingPrice}
            </p>
          </div>
        )}
      </div>
    </section>
  );
};

export default PricingSection;
