import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

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
  sourceUrl: v.string(),
  updatedAt: v.number(),
  hours: v.array(hoursSectionSchema),
};

export const resortRatesFields = {
  resortId: v.string(),
  sourceUrl: v.string(),
  updatedAt: v.number(),
  rates: v.any(),
};

export const resortRentalsFields = {
  resortId: v.string(),
  sourceUrl: v.string(),
  updatedAt: v.number(),
  rentals: v.any(),
};

export const resortsFields = {
  resortId: v.string(),
  published: v.optional(v.boolean()),
  name: v.optional(v.string()),
  continent: v.optional(v.string()),
  country: v.optional(v.string()),
  region: v.optional(v.string()),
  website: v.optional(v.string()),
  address: v.optional(v.string()),
  coordinates: v.optional(
    v.object({
      lat: v.number(),
      lng: v.number(),
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
  lessonsPrice: v.optional(v.number()),
  phone: v.optional(v.string()),
  rating: v.optional(v.number()),
  skiRentalPrice: v.optional(v.number()),
  snowBoardRentalPrice: v.optional(v.number()),
  tracksSummary: v.optional(
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
  tubbingPrice: v.optional(v.number()),
};

export default defineSchema({
  resorts: defineTable(resortsFields)
    .index("by_resort_id", ["resortId"])
    .index("by_location", ["continent", "country", "region"]),

  locations: defineTable({
    continent: v.string(),
    country: v.string(),
    region: v.string(),
  }).index("by_location", ["continent", "country", "region"]),

  weatherAndStatus: defineTable({
    resortId: v.string(),
    sourceUrl: v.optional(v.string()),
    updatedAt: v.number(),
    conditions: v.optional(conditionsSchema),

    lifts: v.array(liftSchema),
    trails: v.array(trailSchema),
    terrainParks: v.optional(v.array(trailSchema)),
    crossCountry: v.optional(v.array(crossCountrySchema)),
    tubing: v.optional(v.array(tubingSchema)),
    liftsSummary: v.optional(summarySchema),
    trailsSummary: v.optional(summarySchema),

    rawData: v.optional(v.any()),
  })
    .index("by_resort", ["resortId"])
    .index("by_updated", ["updatedAt"]),

  resortHours: defineTable(resortHoursFields)
    .index("by_resort", ["resortId"])
    .index("by_updated", ["updatedAt"]),

  resortRates: defineTable(resortRatesFields)
    .index("by_resort", ["resortId"])
    .index("by_updated", ["updatedAt"]),

  resortRentals: defineTable(resortRentalsFields)
    .index("by_resort", ["resortId"])
    .index("by_updated", ["updatedAt"]),

  articles: defineTable({
    slug: v.string(),
    title: v.string(),
    description: v.string(),
    body: v.array(v.any()),
    tags: v.array(v.string()),
    published: v.boolean(),
    publishedAt: v.number(),
    heroImageId: v.id("_storage"),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_slug", ["slug"])
    .index("by_published", ["published", "publishedAt"]),

  adminEmails: defineTable({
    email: v.string(),
    enabled: v.boolean(),
    createdAt: v.number(),
  }).index("by_email", ["email"]),
});
