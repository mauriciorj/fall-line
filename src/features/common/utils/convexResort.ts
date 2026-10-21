import { Resort } from "@/types/resort";

function toAssetSegment(value: string | undefined) {
  return (
    value
      ?.normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "unknown"
  );
}

export function getResortAssetPath(
  resortId: string,
  country: string | undefined,
  region: string | undefined,
  filename: string,
) {
  return `/assets/resorts/${toAssetSegment(country)}/${toAssetSegment(region)}/${toAssetSegment(resortId)}/${filename}`;
}

export function getResortHeroImage(
  resortId: string,
  country?: string,
  region?: string,
) {
  return getResortAssetPath(resortId, country, region, "hero.webp");
}

export function getResortTrailMap(
  resortId: string,
  country?: string,
  region?: string,
  index = 1,
) {
  return getResortAssetPath(
    resortId,
    country,
    region,
    `trail-${index}.webp`,
  );
}

export function getResortLocationParams(
  resortId: string,
  country?: string,
  region?: string,
) {
  return {
    country: toAssetSegment(country),
    region: toAssetSegment(region),
    resortId: toAssetSegment(resortId),
  };
}

export function getResortLocationPath(
  resortId: string,
  country?: string,
  region?: string,
) {
  const params = getResortLocationParams(resortId, country, region);
  return `/location/${params.country}/${params.region}/${params.resortId}`;
}

type DbResort = Partial<Resort> & {
  resortId?: string;
  continent?: string;
  country?: string;
  region?: string;
  contact?: string;
  tracksSummary?: Resort["runs"];
};

type TrackCondition = NonNullable<Resort["trackConditions"]>[number];

const difficultyMap: Record<string, TrackCondition["difficulty"]> = {
  easy: "green",
  medium: "blue",
  hard: "black",
  "double black": "double-black",
  freestyle: "free-style",
  "free style": "free-style",
};

const emptyRuns = {
  black: 0,
  blue: 0,
  doubleBlack: 0,
  freeStyle: 0,
  green: 0,
};

export function toTrackConditions(value: unknown): TrackCondition[] {
  if (!value || typeof value !== "object") return [];

  const trails = (value as { trails?: unknown }).trails;
  if (!Array.isArray(trails)) return [];

  return trails.flatMap((trail) => {
    if (!trail || typeof trail !== "object") return [];

    const record = trail as Record<string, unknown>;
    const name = record.name;
    const difficulty =
      typeof record.difficulty === "string"
        ? difficultyMap[record.difficulty.toLowerCase()]
        : undefined;

    if (typeof name !== "string" || !difficulty) return [];

    return [
      {
        name,
        condition: typeof record.status === "string" ? record.status : "",
        difficulty,
      },
    ];
  });
}

export function toResort(
  value: unknown,
  overrides: Partial<Resort> = {},
): Resort | null {
  if (!value || typeof value !== "object") return null;

  const document = value as DbResort;
  if (!document.resortId) return null;

  const runs = document.tracksSummary ?? document.runs ?? emptyRuns;

  return {
    ...document,
    resortId: document.resortId,
    name: document.name ?? "",
    address: document.address ?? "",
    coordinates: document.coordinates,
    dayTicketPrice: document.dayTicketPrice ?? 0,
    email: document.email ?? "",
    googleMapsUrl: document.googleMapsUrl ?? "",
    hasAccommodations: document.hasAccommodations ?? false,
    hasCrossCountry: document.hasCrossCountry ?? false,
    hasLessons: document.hasLessons ?? false,
    hasIceSkate: document.hasIceSkate ?? false,
    hasSnowshoeing: document.hasSnowshoeing ?? false,
    hasSpa: document.hasSpa ?? false,
    hasTubing: document.hasTubing ?? false,
    image:
      document.image ??
      getResortHeroImage(
        document.resortId,
        document.country,
        document.region,
      ),
    lessonsPrice: document.lessonsPrice ?? 0,
    phone: document.phone ?? document.contact ?? "",
    rating: document.rating ?? 0,
    runs: { ...emptyRuns, ...runs },
    skiRentalPrice: document.skiRentalPrice ?? 0,
    snowBoardRentalPrice: document.snowBoardRentalPrice ?? 0,
    trailMap:
      document.trailMap ??
      getResortTrailMap(
        document.resortId,
        document.country,
        document.region,
      ),
    website: document.website ?? "",
    ...overrides,
  };
}
