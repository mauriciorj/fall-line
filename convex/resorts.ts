import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";
import { resortSeedData } from "./resortSeed";

export const list = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    return await ctx.db.query("resort").collect();
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
        await ctx.db.replace(existing._id, resort);
        ids.push(existing._id);
      } else {
        ids.push(await ctx.db.insert("resort", resort));
      }
    }

    return ids;
  },
});
