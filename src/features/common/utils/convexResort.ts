import { Resort } from "@/types/resort";

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
    hasSnowshoeing: document.hasSnowshoeing ?? false,
    hasSpa: document.hasSpa ?? false,
    hasTubing: document.hasTubing ?? false,
    image: document.image ?? "/assets/lakeridge-ski-resort.webp",
    lessonsPrice: document.lessonsPrice ?? 0,
    phone: document.phone ?? document.contact ?? "",
    rating: document.rating ?? 0,
    runs: { ...emptyRuns, ...runs },
    skiRentalPrice: document.skiRentalPrice ?? 0,
    snowBoardRentalPrice: document.snowBoardRentalPrice ?? 0,
    trailMap: document.trailMap ?? "/assets/lakeridge-ski-resort-trail-map.jpg",
    website: document.website ?? "",
    ...overrides,
  };
}
