import type { StaticImageData } from "next/image";
import type { Resort as SharedResort } from "@fall-line/shared/types/resort";

export * from "@fall-line/shared/types/resort";
export type Resort = SharedResort<StaticImageData | string>;
