import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse, type NextFetchEvent, type NextRequest } from 'next/server'
import { isLocale, stripLocale } from '@/src/i18n/routing'
import { defaultLocale } from '@/src/i18n/translations'

// Non-page routes that must never receive a locale prefix.
const passthroughPrefixes = ['/api', '/trpc', '/opengraph-image']

// Locale routing: the default locale is served unprefixed and rewritten to
// /<defaultLocale>/... internally; /<defaultLocale>/... redirects to the
// unprefixed URL so each page has exactly one address. No Accept-Language or
// geo redirects on purpose — crawlers must be able to reach every version.
function localeRouting(request: NextRequest) {
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
}

// Clerk only has server-side work on the admin area and API routes. On public
// pages it would just parse cookies and decorate cacheable responses; auth for
// those is handled client-side by ClerkProvider and on the Convex side.
function needsClerk(pathname: string) {
  const path = stripLocale(pathname)
  return (
    path === '/admin' ||
    path.startsWith('/admin/') ||
    path.startsWith('/api') ||
    path.startsWith('/trpc')
  )
}

const withClerk = clerkMiddleware((_auth, request) => localeRouting(request))

export default function proxy(request: NextRequest, event: NextFetchEvent) {
  return needsClerk(request.nextUrl.pathname)
    ? withClerk(request, event)
    : localeRouting(request)
}

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest|txt|xml)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
}
