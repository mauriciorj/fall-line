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

export const resortFields = {
  name: v.string(),
  location: v.object({
    address: v.string(),
    city: v.string(),
    provinceOrState: v.string(),
    country: v.string(),
    postalCode: v.string(),
  }),
  rate: v.number(),
  contact: v.string(),
  website: v.string(),
};

export default defineSchema({
  resort: defineTable(resortFields),

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
