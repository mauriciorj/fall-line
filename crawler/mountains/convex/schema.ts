import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

const apiKeyValues = v.object({
  content: v.string(),
  iv: v.string(),
  tag: v.string(),
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

export default defineSchema({
  weatherAndStatus: defineTable({
    resortId: v.string(),
    updatedAt: v.number(),

    conditions: v.optional(conditionsSchema),

    lifts: v.array(liftSchema),
    trails: v.array(trailSchema),
    terrainParks: v.optional(v.array(trailSchema)),
    crossCountry: v.optional(v.array(crossCountrySchema)),
    tubing: v.optional(v.array(tubingSchema)),

    liftsSummary: v.optional(summarySchema),
    trailsSummary: v.optional(summarySchema),
    tubingSummary: v.optional(summarySchema),
  })
    .index("by_resort", ["resortId"])
    .index("by_updated", ["updatedAt"]),
});
