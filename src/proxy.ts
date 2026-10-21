import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'
import { isLocale } from '@/src/i18n/routing'
import { defaultLocale } from '@/src/i18n/translations'

// Non-page routes that must never receive a locale prefix.
const passthroughPrefixes = ['/api', '/trpc', '/opengraph-image']

// Locale routing: the default locale is served unprefixed and rewritten to
// /<defaultLocale>/... internally; /<defaultLocale>/... redirects to the
// unprefixed URL so each page has exactly one address. No Accept-Language or
// geo redirects on purpose — crawlers must be able to reach every version.
export default clerkMiddleware((_auth, request) => {
  const { pathname } = request.nextUrl
  if (passthroughPrefixes.some((prefix) => pathname.startsWith(prefix))) {
    return NextResponse.next()
  }

  const [, first, ...rest] = pathname.split('/')
  if (first === defaultLocale) {
    const url = request.nextUrl.clone()
    url.pathname = `/${rest.join('/')}`
    return NextResponse.redirect(url, 308)
  }
  if (isLocale(first)) {
    return NextResponse.next()
  }

  const url = request.nextUrl.clone()
  url.pathname = `/${defaultLocale}${pathname}`
  return NextResponse.rewrite(url)
})

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest|txt|xml)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
