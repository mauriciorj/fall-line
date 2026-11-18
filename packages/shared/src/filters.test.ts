import { describe, expect, it } from "vitest";
import { applyResortFilters, defaultFilters } from "./filters";
import { toResort, toTrackConditions } from "./resorts";
import { pickLocalized } from "./i18n/localized";

describe("shared resort logic", () => {
  it("filters activities and sorts by distance consistently", () => {
    const resorts = [
      toResort({ resortId: "far", name: "Far", hasLessons: true, coordinates: { lat: 46, lng: -79 } })!,
      toResort({ resortId: "near", name: "Near", hasLessons: true, coordinates: { lat: 44, lng: -79 } })!,
      toResort({ resortId: "none", name: "No lessons" })!,
    ];
    const result = applyResortFilters(resorts, {
      ...defaultFilters,
      sortBy: "distance",
      activities: { ...defaultFilters.activities, lessons: true },
    }, { lat: 44, lng: -79 });
    expect(result.map((item) => item.resortId)).toEqual(["near", "far"]);
    expect(resorts.map((item) => item.resortId)).toEqual(["far", "near", "none"]);
  });

  it("normalizes trail conditions and falls back to English", () => {
    expect(toTrackConditions({ trails: [{ name: "One", difficulty: "easy", status: "open" }, { name: "Unknown", difficulty: "other" }] }))
      .toEqual([{ name: "One", difficulty: "green", condition: "open" }]);
    expect(pickLocalized({ en: "Welcome" }, "fr")).toEqual({ value: "Welcome", lang: "en" });
  });
});
