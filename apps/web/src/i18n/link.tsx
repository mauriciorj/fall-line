"use client";

import Link from "next/link";
import type { ComponentProps } from "react";
import { useLanguage } from "@/src/i18n";
import { localizePath } from "@/src/i18n/routing";

type LocalizedLinkProps = Omit<ComponentProps<typeof Link>, "href"> & {
  href: string;
};

// Drop-in for next/link that prefixes internal paths with the active locale.
export default function LocalizedLink({ href, ...props }: LocalizedLinkProps) {
  const { locale } = useLanguage();
  return <Link href={localizePath(href, locale)} {...props} />;
}
