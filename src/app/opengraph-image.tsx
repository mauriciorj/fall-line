import { ImageResponse } from "next/og";
import { SITE_NAME, SITE_TAGLINE } from "@/utils/seo";

export const alt = SITE_NAME;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          height: "100%",
          width: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          padding: 80,
          background: "linear-gradient(135deg, #1f2f4d 0%, #4a6fa5 100%)",
          color: "#ffffff",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ fontSize: 80, fontWeight: 700, letterSpacing: -2 }}>
          {SITE_NAME}
        </div>
        <div style={{ marginTop: 20, fontSize: 36, color: "#dbe4f3" }}>
          {SITE_TAGLINE}
        </div>
      </div>
    ),
    size,
  );
}
