export * from "@fall-line/shared/resorts";

import { toResort as toSharedResort } from "@fall-line/shared/resorts";
import type { Resort } from "@/types/resort";

export function toResort(
  value: unknown,
  overrides: Partial<Resort> = {},
): Resort | null {
  return toSharedResort(value, overrides as Parameters<typeof toSharedResort>[1]);
}
