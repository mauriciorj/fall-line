import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    turbopackUseSystemTlsCerts: true,
  },
  env: {
    NEXT_PUBLIC_CONVEX_URL:
      process.env.NEXT_PUBLIC_CONVEX_URL ?? process.env.CONVEX_URL,
  },
};

export default nextConfig;
