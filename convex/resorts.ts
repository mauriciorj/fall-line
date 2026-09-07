import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";
import { resortSeedData, trackConditionsSeed } from "./resortSeed";

export const list = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    return await ctx.db.query("resorts").collect();
  },
});

export const saveMany = internalMutation({
  args: {
    resorts: v.array(v.any()),
  },
  returns: v.array(v.id("resorts")),
  handler: async (ctx, args) => {
    const ids = [];

    for (const resort of args.resorts) {
      const existing = await ctx.db
        .query("resorts")
        .withIndex("by_source_id", (q) => q.eq("sourceId", resort.sourceId))
        .unique();
      const document = {
        ...resort,
        source: resort.source ?? "skiresort.info",
        sourceId: resort.sourceId,
      };

      if (existing) {
        await ctx.db.replace(existing._id, document);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resorts", document));
      }
    }

    return ids;
  },
});

export const getBySourceId = query({
  args: { sourceId: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resorts")
      .withIndex("by_source_id", (q) => q.eq("sourceId", args.sourceId))
      .unique();
  },
});

export const seed = internalMutation({
  args: {},
  returns: v.array(v.id("resorts")),
  handler: async (ctx) => {
    const ids = [];

    for (const resort of resortSeedData) {
      const seedRecord = {
        ...resort,
        source: "curated",
        trackConditions: trackConditionsSeed[resort.sourceId] ?? [],
      };
      const existingBySourceId = await ctx.db
        .query("resorts")
        .withIndex("by_source_id", (q) => q.eq("sourceId", resort.sourceId))
        .unique();
      const existing =
        existingBySourceId ??
        (await ctx.db
          .query("resorts")
          .filter((q) => q.eq(q.field("name"), resort.name))
          .first());

      if (existing) {
        await ctx.db.replace(existing._id, seedRecord);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resorts", seedRecord));
      }
    }

    return ids;
  },
});

