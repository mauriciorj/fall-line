import type { ReactNode } from "react";

// <html>/<body> live in app/[locale]/layout.tsx so `lang` can follow the URL.
// A root layout is still required for app/not-found.tsx, so it passes through.
export default function RootLayout({ children }: { children: ReactNode }) {
  return children;
}
