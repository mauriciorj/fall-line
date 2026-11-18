import { convexTest } from "convex-test";
import { describe, expect, it } from "vitest";
import { api } from "./_generated/api";
import schema from "./schema";

const modules = import.meta.glob("./**/*.ts");

describe("public mountain detail queries", () => {
  it("only exposes published resorts and their related records", async () => {
    const t = convexTest(schema, modules);
    await t.run(async (ctx) => {
      for (const [resortId, published] of [["public", true], ["draft", false], ["unset", undefined]] as const) {
        await ctx.db.insert("resorts", { resortId, published });
        await ctx.db.insert("resortHours", { resortId, sourceUrl: "https://example.com", updatedAt: 1, hours: [] });
        await ctx.db.insert("weatherAndStatus", {
          resortId, updatedAt: 1, lifts: [], trails: [{ name: "Trail", status: "open" }],
          rawData: { secret: "must not leave the server" },
        });
      }
      await ctx.db.insert("resortHours", { resortId: "orphan", sourceUrl: "https://example.com", updatedAt: 1, hours: [] });
      await ctx.db.insert("weatherAndStatus", { resortId: "orphan", updatedAt: 1, lifts: [], trails: [] });
    });

    for (const resortId of ["draft", "unset", "orphan", "missing"]) {
      expect(await t.query(api.resorts.getByResortId, { resortId })).toBeNull();
      expect(await t.query(api.resortHours.getByResort, { resortId })).toBeNull();
      expect(await t.query(api.weatherAndStatus.getByResort, { resortId })).toBeNull();
    }
    expect(await t.query(api.resorts.getByResortId, { resortId: "public" })).toMatchObject({ published: true });
    expect(await t.query(api.resortHours.getByResort, { resortId: "public" })).toMatchObject({ hours: [] });
    const status = await t.query(api.weatherAndStatus.getByResort, { resortId: "public" });
    expect(status).toMatchObject({ trails: [{ name: "Trail", status: "open" }] });
    expect(status).not.toHaveProperty("rawData");

    await t.run(async (ctx) => {
      const resort = await ctx.db.query("resorts").withIndex("by_resort_id", (q) => q.eq("resortId", "public")).unique();
      await ctx.db.patch(resort!._id, { published: false });
    });
    expect(await t.query(api.resorts.getByResortId, { resortId: "public" })).toBeNull();
    expect(await t.query(api.resortHours.getByResort, { resortId: "public" })).toBeNull();
    expect(await t.query(api.weatherAndStatus.getByResort, { resortId: "public" })).toBeNull();
  });
});
