import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";
import { resortSeedData, trackConditionsSeed } from "./resortSeed";

export const list = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    return await ctx.db.query("resort").collect();
  },
});

export const saveMany = internalMutation({
  args: {
    resorts: v.array(v.any()),
  },
  returns: v.array(v.id("resort")),
  handler: async (ctx, args) => {
    const ids = [];

    for (const resort of args.resorts) {
      const existing = await ctx.db
        .query("resort")
        .withIndex("by_resort_id", (q) => q.eq("id", resort.id))
        .unique();
      const document = {
        ...resort,
        source: resort.source ?? "skiresort.info",
        sourceId: resort.sourceId ?? resort.id,
      };

      if (existing) {
        await ctx.db.replace(existing._id, document);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resort", document));
      }
    }

    return ids;
  },
});

export const getById = query({
  args: { id: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("resort")
      .withIndex("by_resort_id", (q) => q.eq("id", args.id))
      .unique();
  },
});

export const seed = internalMutation({
  args: {},
  returns: v.array(v.id("resort")),
  handler: async (ctx) => {
    const ids = [];

    for (const resort of resortSeedData) {
      const seedRecord = {
        ...resort,
        trackConditions: trackConditionsSeed[resort.id] ?? [],
      };
      const existingById = await ctx.db
        .query("resort")
        .withIndex("by_resort_id", (q) => q.eq("id", resort.id))
        .unique();
      const existing =
        existingById ??
        (await ctx.db
          .query("resort")
          .filter((q) => q.eq(q.field("name"), resort.name))
          .first());

      if (existing) {
        await ctx.db.replace(existing._id, seedRecord);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resort", seedRecord));
      }
    }

    return ids;
  },
});
