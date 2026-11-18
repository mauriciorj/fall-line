import type { NextConfig } from "next";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { parse } from "dotenv";
import { expand } from "dotenv-expand";

// Preserve root Convex CLI configuration while allowing app-local overrides.
const nodeEnv = process.env.NODE_ENV ?? "development";
const rootEnvFiles = [
  `.env.${nodeEnv}.local`,
  ...(nodeEnv === "test" ? [] : [".env.local"]),
  `.env.${nodeEnv}`,
  ".env",
];
for (const file of rootEnvFiles) {
  try {
    const parsed = parse(readFileSync(resolve(process.cwd(), "../..", file)));
    for (const key of Object.keys(parsed)) {
      if (Object.prototype.hasOwnProperty.call(process.env, key)) delete parsed[key];
    }
    expand({ parsed });
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code !== "ENOENT") throw error;
  }
}

const nextConfig: NextConfig = {
  transpilePackages: ["@fall-line/shared"],
  experimental: {
    turbopackUseSystemTlsCerts: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "www.skiresort.info",
      },
      // Convex file storage (blog hero images), any deployment.
      {
        protocol: "https",
        hostname: "*.convex.cloud",
        pathname: "/api/storage/**",
      },
    ],
  },
  env: {
    NEXT_PUBLIC_CONVEX_URL:
      process.env.NEXT_PUBLIC_CONVEX_URL ?? process.env.CONVEX_URL,
  },
};

export default nextConfig;
