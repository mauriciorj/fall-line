import { internalMutation, query } from "./_generated/server";
import { v } from "convex/values";

const locationValidator = v.object({
  continent: v.string(),
  country: v.string(),
  region: v.string(),
});

export const list = query({
  args: {},
  returns: v.array(locationValidator),
  handler: async (ctx) => {
    const locations = await ctx.db.query("locations").order("asc").collect();
    return locations.map(({ continent, country, region }) => ({
      continent,
      country,
      region,
    }));
  },
});

export const sync = internalMutation({
  args: { locations: v.array(locationValidator) },
  returns: v.number(),
  handler: async (ctx, args) => {
    const existing = await ctx.db.query("locations").collect();
    for (const location of existing) {
      await ctx.db.delete(location._id);
    }

    for (const location of args.locations) {
      await ctx.db.insert("locations", location);
    }

    return args.locations.length;
  },
});
