/* eslint-disable */
/**
 * Generated `api` utility.
 *
 * THIS CODE IS AUTOMATICALLY GENERATED.
 *
 * To regenerate, run `npx convex dev`.
 * @module
 */

import type * as locations from "../locations.js";
import type * as resortHours from "../resortHours.js";
import type * as resortRates from "../resortRates.js";
import type * as resortRentals from "../resortRentals.js";
import type * as resorts from "../resorts.js";
import type * as weatherAndStatus from "../weatherAndStatus.js";

import type {
  ApiFromModules,
  FilterApi,
  FunctionReference,
} from "convex/server";

declare const fullApi: ApiFromModules<{
  locations: typeof locations;
  resortHours: typeof resortHours;
  resortRates: typeof resortRates;
  resortRentals: typeof resortRentals;
  resorts: typeof resorts;
  weatherAndStatus: typeof weatherAndStatus;
}>;

/**
 * A utility for referencing Convex functions in your app's public API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = api.myModule.myFunction;
 * ```
 */
export declare const api: FilterApi<
  typeof fullApi,
  FunctionReference<any, "public">
>;

/**
 * A utility for referencing Convex functions in your app's internal API.
 *
 * Usage:
 * ```js
 * const myFunctionReference = internal.myModule.myFunction;
 * ```
 */
export declare const internal: FilterApi<
  typeof fullApi,
  FunctionReference<any, "internal">
>;

export declare const components: {};
