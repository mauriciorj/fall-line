import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";
import { ensureResort } from "./resorts";

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

export const save = internalMutation({
  args: {
    resortId: v.string(),
    sourceUrl: v.optional(v.string()),
    updatedAt: v.optional(v.number()),
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
  },
  returns: v.id("weatherAndStatus"),
  handler: async (ctx, args) => {
    const { updatedAt: updatedAtArg, ...docFields } = args;
    const updatedAt = updatedAtArg ?? Date.now();
    await ensureResort(ctx, {
      resortId: args.resortId,
      website: args.sourceUrl,
    });
    const doc = { ...docFields, updatedAt };

    const existing = await ctx.db
      .query("weatherAndStatus")
      .withIndex("by_resort", (q) => q.eq("resortId", args.resortId))
      .unique();

    if (existing) {
      await ctx.db.replace(existing._id, doc);
      return existing._id;
    }

    return await ctx.db.insert("weatherAndStatus", doc);
  },
});

export const getByResort = query({
  args: { resortId: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("weatherAndStatus")
      .withIndex("by_resort", (q) => q.eq("resortId", args.resortId))
      .unique();
  },
});
