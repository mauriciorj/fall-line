# Security audit — prelaunch

**Audit date:** November 12, 2026  
**Target hosting:** Vercel  
**Scope:** Application, Convex, Clerk, frontend external calls, secret exposure, and application dependencies. The crawler is excluded.  
**Status:** Assessment only. No remediation was performed. This README preserves the findings from the original read-only audit; creating it did not rerun the audit.

## Verdict

**Not ready for launch. Three high-priority fixes were identified.**

“100% safe” cannot be certified. Source review and isolated tests establish specific protections and weaknesses, not the absence of every vulnerability or a previous breach.

No application code, configuration, accounts, deployments, or application data were changed during the audit. This report contains no secret values.

### Confirmed project requirements and settings

| Item | Confirmation |
| --- | --- |
| Release stage | Prelaunch |
| Planned hosting | Vercel |
| Unpublished resorts | Must be inaccessible, not merely omitted from listings |
| Google Maps key | Usage restrictions are not configured |
| Clerk admin requirements | Email verification is required; MFA is not required |

## High priority

### H1. Patch vulnerable runtime dependencies and narrow image permissions

Installed versions match published security advisories:

| Package | Installed | Minimum fix floor from checked advisories |
| --- | --- | --- |
| Next.js | 16.0.10 | 16.4.1 |
| Sharp | 0.34.5 | 0.35.5 |
| Clerk Next.js SDK | 6.37.3 | 6.39.3 |

These floors address the checked advisories, not future vulnerabilities or every possible dependency combination. Select maintained, compatible releases when remediation begins, update React/ReactDOM and `eslint-config-next` alongside Next.js as appropriate, and re-audit the resulting lockfile and transitive dependencies.

Evidence: [application dependencies](../../package.json).

**Main exposure:** Next.js/Sharp image-processing vulnerabilities, including published remote-code-execution advisories. The configuration also permits images from **any `*.convex.cloud` deployment**. The installed Next.js matcher accepted an unrelated deployment during isolated verification.

**Required fixes:**

- Patch the affected runtime dependencies before launch.
- Restrict image optimization to the application's production storage hostname and required paths.
- Remove unused remote image hosts.
- Verify that the Sharp version actually resolved by Next.js is patched, not only the direct package declaration.

Evidence: [remote image configuration](../../next.config.ts#L7-L19).

**Applicability limits:**

- Actual Vercel-managed image/runtime exposure was not tested.
- Clerk advisories concern route matching and combined authorization predicates. The current code does not use those affected patterns. **No Clerk account-impersonation vulnerability was demonstrated.**
- A package advisory match is not proof that every affected feature is reachable in this application.

Advisory sources:

- [Next.js/Sharp image-processing advisory](https://github.com/advisories/GHSA-2464-fhr4-w9xw)
- [Next.js AVIF image-processing advisory](https://github.com/advisories/GHSA-2xp9-vwfh-vxw4)
- [Clerk route-protection advisory](https://github.com/advisories/GHSA-vqx2-fgx2-5wq9)
- [Clerk authorization-predicate advisory](https://github.com/advisories/GHSA-w24r-5266-9c3c)

### H2. Make unpublished resorts inaccessible

The required behavior is that unpublished resorts must be inaccessible.

**Confirmed:** `resorts.getByResortId` returns records without checking `published`. An isolated test returned a `published: false` record to an anonymous caller. The public resort page checks existence rather than publication status.

Evidence:

- [Public resort lookup](../../convex/resorts.ts#L177-L185)
- [Public resort page lookup and existence check](../../src/app/[locale]/location/[country]/[region]/[resortId]/page.tsx#L120-L138)
- [Public hours lookup](../../convex/resortHours.ts#L35-L43)
- [Public weather lookup](../../convex/weatherAndStatus.ts#L94-L102)

**Required fixes:**

- Require `published === true` in every public resort-related getter, including hours and weather.
- Return `null` or 404 for unpublished records.
- Keep preview access behind separate admin-authorized queries.
- Invalidate cached pages and metadata when unpublishing.

Filtering listings or setting `noindex` does **not** enforce privacy.

### H3. Restrict the publicly exposed Google Maps key

Browser exposure is normal for a Maps JavaScript key. **Unrestricted usage is not.** The absence of restrictions was confirmed by the project owner.

**Risk:** unauthorized API consumption, quota exhaustion, and unwanted billing.

**Required fixes:**

- Restrict website referrers to intended production origins.
- Restrict APIs to the required Maps JavaScript and Geocoding services.
- Separate production and development/preview keys.
- Configure quotas and billing alerts, and review existing usage.
- Rotate the key if previous exposure or the usage review indicates misuse.

Do not proxy Maps JavaScript merely to hide its browser key.

Evidence: [Maps JavaScript key usage](../../src/features/common/components/regionDetector.tsx#L20-L23).

Reference: [Google Maps Platform security guidance](https://developers.google.com/maps/api-security-best-practices).

## Medium priority

### M1. Add server-side `/admin` protection

Clerk middleware initializes authentication but does not call `auth.protect()`. The admin layout supplies metadata only; access display is client-controlled.

**This is not an established database-write bypass:** Convex independently checks admin authorization.

**Required fixes:**

- Authenticate and authorize before server-rendering admin content.
- Retain all Convex authorization checks.
- Ensure the protected branch does not inherit public `force-static` behavior.
- Cover localized admin paths as well as the unprefixed route.

Evidence:

- [Clerk middleware invocation](../../src/proxy.ts#L47-L54)
- [Admin layout](../../src/app/[locale]/admin/layout.tsx)
- [Shared static rendering configuration](../../src/app/[locale]/layout.tsx#L18-L20)

### M2. Strengthen admin identity and account security

Admin authorization uses email matching without checking `emailVerified` or binding permissions to an immutable Clerk identity.

The configured verified-email requirement reduces immediate risk. Synthetic unverified-email claims passed the local gate, but **real Clerk issuance of such claims was not demonstrated**.

**Required fixes:**

- Bind admin permissions to Clerk `subject` or Convex `tokenIdentifier`.
- Verify email ownership when granting access.
- Require MFA for admins; the current requirement is email verification only.
- Configure production origin restrictions and Clerk `authorizedParties`.
- Record privilege changes and destructive operations in an audit trail.

Evidence: [admin identity extraction and authorization](../../convex/admin.ts#L17-L31).

References:

- [Convex identity fields and authentication in functions](https://docs.convex.dev/auth/functions-auth)
- [Clerk production deployment security guidance](https://clerk.com/docs/guides/development/deployment/production)

### M3. Minimize public Convex responses and bound expensive reads

The weather query returns the entire document, including optional `rawData`. Several public queries collect complete result sets. The published-article listing also returns full article bodies.

**Required fixes:**

- Define explicit public response shapes.
- Exclude unnecessary raw payloads from public responses.
- Paginate and index expensive reads.
- Establish abuse and cost controls, including usage monitoring.

Contents of upstream raw payloads were not investigated. No claim is made that those payloads currently contain secrets.

Evidence:

- [Public weather response](../../convex/weatherAndStatus.ts#L94-L102)
- [Weather schema and raw payload field](../../convex/schema.ts#L202-L217)
- [Public article listing](../../convex/blog.ts#L25-L35)
- [Resort location listing](../../convex/resorts.ts#L125-L135)

### M4. Validate uploaded images and article bodies server-side

Upload URL creation requires admin access. However, article creation lacks server-side file-type and size verification, and article bodies accept arbitrary array contents.

**Required fixes:**

- Verify stored file metadata and the actual image format.
- Enforce file-size and image-dimension limits.
- Validate typed article blocks and content lengths.
- Clean up orphaned uploads.

Browser `accept="image/*"` is not security validation.

**This is not an anonymous-upload vulnerability.**

Evidence:

- [Article input validation](../../convex/admin.ts#L5-L15)
- [Upload URL creation and article creation](../../convex/admin.ts#L155-L176)
- [Browser upload flow](../../src/app/[locale]/admin/page.tsx#L151-L159)

### M5. Separate advertising from admin and address privacy behavior

Google Ads loads through the shared layout without consent gating, including on admin pages. Geocoding forwards browser-provided coordinates directly to Google.

**Required fixes:**

- Exclude advertising from admin pages.
- Obtain required consent before nonessential tracking.
- Disclose coordinate sharing accurately.
- Consider coarsening coordinates when regional detection does not need precise location.
- Keep the privacy policy consistent with actual advertising and location-processing behavior.

Evidence:

- [Shared Google Ads scripts](../../src/app/[locale]/layout.tsx#L85-L98)
- [Coordinates supplied to Google Geocoding](../../src/features/common/components/regionDetector.tsx#L35-L38)
- [Privacy policy](../../src/app/[locale]/privacy/page.tsx)

### M6. Establish security headers

The reviewed Next.js configuration defines no application security headers. Effective Vercel headers remain unverified.

**Required fixes:**

- Inspect deployed responses.
- Configure missing Content Security Policy, anti-framing protections, `X-Content-Type-Options: nosniff`, referrer policy, and permissions policy.
- Verify HTTPS and HSTS behavior.
- Allow necessary Clerk and Maps resources in CSP without broad unrestricted allowances.

Evidence: [Next.js configuration](../../next.config.ts).

### M7. Update remaining dependencies and add regression checks

The audit also flags production-graph dependencies such as `js-cookie`, Zod, and PostCSS, plus development tooling including Hono, minimatch, and MCP SDK dependencies.

The dev-only critical `proxy-addr` finding traces through **shadcn's MCP/Express tooling**, not an identified public application endpoint.

**Required fixes:**

- Update affected parent packages and transitive dependencies.
- Review unused dependencies before removing them; usage outside this audit's scope was not assessed.
- Add automated dependency and secret scanning.
- Add regression tests covering anonymous, non-admin, disabled-admin, and unpublished-record access.

Evidence: [development dependencies](../../package.json#L73-L91) and [dependency lockfile](../../pnpm-lock.yaml).

## Low priority

### L1. Remove Clerk user-object console logging

The admin page logs the Clerk user object. This unnecessarily exposes personal information in browser logs; it is not a demonstrated remote leak.

**Required fix:** remove the user-object logging from production code.

Evidence: [admin logging](../../src/app/[locale]/admin/page.tsx#L68-L74).

### L2. Prevent administrative lockout and accidental destructive operations

The current mutation can disable the final enabled admin.

**Required fixes:**

- Add safeguards against disabling the last enabled admin.
- Add confirmation for destructive operations.

Evidence:

- [Admin enable/disable mutation](../../convex/admin.ts#L73-L80)
- [Admin dashboard actions](../../src/app/[locale]/admin/page.tsx#L242-L250)

### L3. Validate stored outbound URLs

Rich-text links and images accept arbitrary destinations.

**Required fixes:**

- Enforce appropriate URL schemes.
- Restrict image hosts where feasible.
- Retain `noopener noreferrer` on external new-tab links.

No executable-HTML or XSS exploit was demonstrated here.

Evidence: [rich-text image and link rendering](../../src/features/blog/components/richText.tsx#L30-L40).

## Dependency audit results

These are registry severity counts, **not counts of proven exploitable application bugs**. Report priorities remain high, medium, and low; “critical” below is the registry's advisory severity.

| Scope | Critical | High | Moderate | Low | Total matches |
| --- | --- | --- | --- | --- | --- |
| Full dependency graph | 7 | 77 | 79 | 14 | 177 |
| Production dependency graph | 6 | 32 | 21 | 5 | 64 |

The production graph includes some build-time libraries. Platform-specific and unused-feature advisories require applicability checks. Windows-hosting findings do not match the planned Vercel deployment.

Advisory matches can repeat across packages and version ranges; these totals are not counts of unique CVEs.

The original audit used:

```text
pnpm audit --json --registry=https://registry.npmjs.org
pnpm audit --prod --json --registry=https://registry.npmjs.org
```

Installed direct dependency versions were checked against local package metadata. Selected important advisories were cross-checked against published vendor/GitHub advisory information. No dependencies were installed or updated.

## Keys and frontend external calls

### Secret checks

- No private-key pattern matches were found in scoped current source or 724 historical text blobs across 120 locally available commits.
- Known private environment values were absent from the 362 existing browser assets inspected.
- Environment files are ignored and were not tracked.
- Local configuration uses Clerk test and Convex dev credentials. This is expected prelaunch, not production approval.
- Secret values were not printed or included in this report.

These checks do not establish that every possible credential format or unavailable historical artifact is free of secrets. Existing browser assets were inspected without producing a new build.

Evidence: [environment-file ignore rules](../../.gitignore#L68-L72).

### External-call decisions

| External integration | Recommendation |
| --- | --- |
| Convex browser SDK | **Keep direct calls.** The public deployment URL is not a secret. Fix authorization and data visibility in Convex, not by hiding the URL. |
| Clerk browser SDK | **Keep.** The publishable key is intentionally public. Patch the SDK and verify production configuration. |
| Google Maps/Geocoding | **Keep the browser integration**, with key restrictions and appropriate location disclosure. |
| Google Ads | **Change the loading policy:** consent where required; advertising is not needed in admin. The advertising ID is not a secret. |
| Convex uploads/images | The direct upload flow is acceptable after admin authorization. Add validation and narrow image hostname permissions. |

`CLERK_SECRET_KEY` must remain server-only. `CONVEX_DEPLOY_KEY` belongs in controlled deployment/CI environments, not browser bundles or unnecessary web-runtime configuration.

## Convex and Clerk assessment

### Verified protections

- All **12 privileged Convex handlers** rejected anonymous and non-admin identities in isolated tests.
- A disabled admin was rejected.
- Admin bootstrap is registered as an internal mutation.
- Blog queries check publication status.
- Auth configuration specifies the Clerk issuer and `applicationID: "convex"`.

Evidence:

- [Admin authorization helper](../../convex/admin.ts#L24-L31)
- [Internal admin bootstrap](../../convex/admin.ts#L211-L223)
- [Published article lookup](../../convex/blog.ts#L39-L53)
- [Convex authentication configuration](../../convex/auth.config.ts)

The isolated tests exercised application handlers with synthetic identities and database fixtures. They did not forge real Clerk tokens, call live Convex mutations, or verify production dashboard settings.

### Still required before launch

- Verify the production Clerk issuer and JWT audience.
- Confirm that deployed Convex functions match the reviewed source and do not retain unintended public entry points.
- Review Clerk, Convex, and hosting dashboard access and MFA.
- Review deployment-key permissions and environment separation.
- Establish backups, monitoring, and usage alerts.
- Run real authorization regression tests in a controlled environment after remediation.

### Breach status and assessment limits

**Breach status: undetermined.**

No Clerk, Convex, or Vercel incident logs were reviewed. No live exploit tests, deployments, installs, or remediation were performed. The crawler was excluded throughout the investigation.

Re-audit after remediation and before launch. This report is a point-in-time assessment, not a security certification.
