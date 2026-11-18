import Image from "next/image";
import Link from "next/link";
import { formatCad } from "@/src/i18n/format";
import { localizePath } from "@/src/i18n/routing";
import { Locale, getTranslator } from "@/src/i18n/translations";
import type { Resort } from "@/types/resort";
import {
  getResortHeroImage,
  getResortLocationPath,
} from "@/utils/convexResort";

const amenityKeys: [keyof Resort, string][] = [
  ["hasTubing", "tubbing"],
  ["hasLessons", "lessons"],
  ["hasAccommodations", "accommodations"],
  ["hasCrossCountry", "crossCountry"],
  ["hasIceSkate", "iceSkating"],
  ["hasSnowshoeing", "snowshoeing"],
  ["hasSpa", "spa"],
];

const runsTotal = ({ runs }: Resort) =>
  runs.green + runs.blue + runs.black + runs.doubleBlack + (runs.freeStyle ?? 0);

// Plain HTML table: the most machine-readable format for comparison queries.
export default function RegionTable({
  resorts,
  locale,
}: {
  resorts: Resort[];
  locale: Locale;
}) {
  const t = getTranslator(locale);
  const price = (amount: number) => (amount > 0 ? formatCad(amount, locale) : "—");
  const rows = [...resorts].sort(
    (a, b) =>
      (a.dayTicketPrice || Number.POSITIVE_INFINITY) -
        (b.dayTicketPrice || Number.POSITIVE_INFINITY) ||
      a.name.localeCompare(b.name),
  );

  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-card">
      <table className="w-full min-w-[720px] text-sm">
        <thead className="bg-muted/40 text-left text-xs uppercase tracking-wide text-muted-foreground">
          <tr>
            <th scope="col" className="px-4 py-3">{t("resort")}</th>
            <th scope="col" className="px-4 py-3">{t("liftPass")}</th>
            <th scope="col" className="px-4 py-3">{t("skiRental")}</th>
            <th scope="col" className="px-4 py-3">{t("snowboardRental")}</th>
            <th scope="col" className="px-4 py-3">{t("runsHeader")}</th>
            <th scope="col" className="px-4 py-3">{t("amenities")}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {rows.map((resort) => {
            const amenities = amenityKeys
              .filter(([field]) => resort[field])
              .map(([, key]) => t(key));
            const total = runsTotal(resort);

            return (
              <tr key={resort.resortId}>
                <th scope="row" className="px-4 py-3 font-medium">
                  <Link
                    href={localizePath(
                      getResortLocationPath(
                        resort.resortId,
                        resort.country,
                        resort.region,
                      ),
                      locale,
                    )}
                    className="flex items-center gap-3 text-foreground hover:text-primary hover:underline"
                  >
                    <Image
                      src={getResortHeroImage(
                        resort.resortId,
                        resort.country,
                        resort.region,
                      )}
                      alt=""
                      width={64}
                      height={36}
                      className="h-9 w-16 shrink-0 rounded object-cover"
                    />
                    {resort.name}
                  </Link>
                </th>
                <td className="px-4 py-3">{price(resort.dayTicketPrice)}</td>
                <td className="px-4 py-3">{price(resort.skiRentalPrice)}</td>
                <td className="px-4 py-3">{price(resort.snowBoardRentalPrice)}</td>
                <td className="px-4 py-3">
                  {total > 0 ? (
                    <>
                      <span className="font-medium">{total}</span>
                      <span className="ml-2 text-xs text-muted-foreground">
                        {resort.runs.green} / {resort.runs.blue} / {resort.runs.black}
                      </span>
                    </>
                  ) : (
                    "—"
                  )}
                </td>
                <td className="px-4 py-3 text-muted-foreground">
                  {amenities.length ? amenities.join(" · ") : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
