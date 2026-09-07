import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const conditionsSchema = v.object({
  temperature: v.optional(v.string()),
  baseDepth: v.optional(v.string()),
  newSnow: v.optional(v.string()),
  surfaceConditions: v.optional(v.string()),
  snowmaking: v.optional(v.string()),
  lastUpdated: v.optional(v.string()),
  hours: v.optional(v.string()),
});

const summarySchema = v.object({
  open: v.number(),
  total: v.number(),
});

const liftSchema = v.object({
  name: v.string(),
  status: v.string(),
  hours: v.optional(v.string()),
  dayStatus: v.optional(v.string()),
  nightStatus: v.optional(v.string()),
  identifier: v.optional(v.string()),
});

const trailSchema = v.object({
  name: v.string(),
  status: v.string(),
  difficulty: v.optional(v.string()),
  dayStatus: v.optional(v.string()),
  nightStatus: v.optional(v.string()),
  area: v.optional(v.string()),
  number: v.optional(v.string()),
});

const tubingSchema = v.object({
  name: v.optional(v.string()),
  status: v.string(),
  hours: v.optional(v.string()),
});

const crossCountrySchema = v.object({
  trail: v.string(),
  distance: v.optional(v.string()),
  status: v.string(),
  trackSet: v.optional(v.string()),
  groomedToday: v.optional(v.string()),
});

export const hoursRowSchema = v.object({
  day: v.string(),
  time: v.string(),
});

export const activityHoursSchema = v.object({
  name: v.string(),
  hours: v.array(hoursRowSchema),
});

export const hoursSectionSchema = v.object({
  name: v.string(),
  activities: v.optional(v.array(activityHoursSchema)),
  hours: v.optional(v.array(hoursRowSchema)),
});

export const resortHoursFields = {
  resortId: v.string(),
  resortName: v.string(),
  sourceUrl: v.string(),
  fetchedAt: v.number(),
  sections: v.array(hoursSectionSchema),
};

export const resortRatesFields = {
  resortId: v.string(),
  resortName: v.string(),
  sourceUrl: v.string(),
  fetchedAt: v.number(),
  rates: v.any(),
};

export const resortRentalsFields = {
  resortId: v.string(),
  resortName: v.string(),
  sourceUrl: v.string(),
  fetchedAt: v.number(),
  rentals: v.any(),
};

export const resortsFields = {
  source: v.optional(v.string()),
  sourceId: v.optional(v.string()),
  name: v.string(),
  continent: v.optional(v.string()),
  country: v.optional(v.string()),
  region: v.optional(v.string()),
  rate: v.optional(v.number()),
  contact: v.optional(v.string()),
  website: v.optional(v.string()),
  directoryData: v.optional(v.object({
    locationTrail: v.array(v.string()),
    url: v.optional(v.string()),
    rating: v.optional(v.number()),
    altitudeDifference: v.optional(v.string()),
    altitudeBase: v.optional(v.string()),
    altitudeTop: v.optional(v.string()),
    slopesTotal: v.optional(v.string()),
    slopesEasy: v.optional(v.string()),
    slopesIntermediate: v.optional(v.string()),
    slopesDifficult: v.optional(v.string()),
    skiPassPrice: v.optional(v.string()),
    imageUrl: v.optional(v.string()),
    fetchedAt: v.number(),
    rawData: v.optional(v.any()),
  })),
  address: v.optional(v.string()),
  coordinates: v.optional(
    v.object({
      lat: v.number(),
      lng: v.number(),
    }),
  ),
  crawlerUrls: v.optional(
    v.object({
      dayTicketPriceUrl: v.optional(v.string()),
      equipmentRentalsUrl: v.optional(v.string()),
      hoursOfOperationUrl: v.optional(v.string()),
      lessonsUrl: v.optional(v.string()),
      trackConditionsUrl: v.optional(v.string()),
      tubbing: v.optional(v.string()),
    }),
  ),
  dayTicketPrice: v.optional(v.number()),
  email: v.optional(v.string()),
  googleMapsUrl: v.optional(v.string()),
  hasAccommodations: v.optional(v.boolean()),
  hasCrossCountry: v.optional(v.boolean()),
  hasLessons: v.optional(v.boolean()),
  hasSnowshoeing: v.optional(v.boolean()),
  hasSpa: v.optional(v.boolean()),
  hasTubing: v.optional(v.boolean()),
  hasZipline: v.optional(v.boolean()),
  hoursOfOperation: v.optional(
    v.object({
      sunday: v.optional(v.string()),
      monday: v.optional(v.string()),
      tuesday: v.optional(v.string()),
      wednesday: v.optional(v.string()),
      thursday: v.optional(v.string()),
      friday: v.optional(v.string()),
      saturday: v.optional(v.string()),
    }),
  ),
  image: v.optional(v.string()),
  lessonsPrice: v.optional(v.number()),
  phone: v.optional(v.string()),
  rating: v.optional(v.number()),
  skiRentalPrice: v.optional(v.number()),
  snowBoardRentalPrice: v.optional(v.number()),
  runs: v.optional(
    v.object({
      black: v.optional(v.number()),
      blue: v.optional(v.number()),
      doubleBlack: v.optional(v.number()),
      freeStyle: v.optional(v.number()),
      green: v.optional(v.number()),
    }),
  ),
  ticketUrl: v.optional(v.string()),
  tollFree: v.optional(v.string()),
  trackConditions: v.optional(
    v.array(
      v.object({
        name: v.string(),
        condition: v.string(),
        difficulty: v.string(),
      }),
    ),
  ),
  trailMap: v.optional(v.string()),
  tubbingPrice: v.optional(v.number()),
};

export default defineSchema({
  resorts: defineTable(resortsFields).index("by_source_id", ["sourceId"]),

  weatherAndStatus: defineTable({
    resortId: v.string(),
    resortName: v.string(),
    sourceUrl: v.optional(v.string()),
    fetchedAt: v.number(),

    conditions: v.optional(conditionsSchema),

    lifts: v.array(liftSchema),
    trails: v.array(trailSchema),
    terrainParks: v.optional(v.array(trailSchema)),
    crossCountry: v.optional(v.array(crossCountrySchema)),
    tubing: v.optional(v.array(tubingSchema)),

    liftsSummary: v.optional(summarySchema),
    trailsSummary: v.optional(summarySchema),
    tubingSummary: v.optional(summarySchema),
    rawData: v.optional(v.any()),
  })
    .index("by_resort", ["resortId"])
    .index("by_fetched", ["fetchedAt"]),

  resortHours: defineTable(resortHoursFields)
    .index("by_resort", ["resortId"])
    .index("by_fetched", ["fetchedAt"]),

  resortRates: defineTable(resortRatesFields)
    .index("by_resort", ["resortName"])
    .index("by_fetched", ["fetchedAt"]),

  resortRentals: defineTable(resortRentalsFields)
    .index("by_resort", ["resortName"])
    .index("by_fetched", ["fetchedAt"]),
});
