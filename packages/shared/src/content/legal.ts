type LegalSection = { heading: string; paragraphs?: string[]; items?: string[] };

export const legalUpdated = "September 8, 2026";

export function privacySections(platform: "web" | "mobile"): LegalSection[] {
  const mobile = platform === "mobile";
  return [
    { heading: "1. Scope", paragraphs: [`This Privacy Policy explains how Fall Line handles information when you use the ${mobile ? "mobile app" : "website"}.`] },
    { heading: "2. Information handled", items: [
      "Resort and location data retrieved from the application database to display search results.",
      mobile ? "Your selected location stored on your device so the app can preserve that preference." : "Your selected location stored in your browser's local storage so the site can preserve that preference.",
      mobile ? "Approximate location information only when you grant device location permission. This is used to suggest a nearby region and show distances." : "Approximate location information only when you grant browser location permission. This is used to suggest a nearby region.",
      "Information you choose to send when contacting support or providing feedback.",
    ] },
    { heading: "3. How information is used", paragraphs: ["Information is used to operate the resort directory, filter and sort results, suggest a location, respond to messages, protect the service, and improve reliability."] },
    { heading: "4. Service providers", paragraphs: [`The ${mobile ? "app" : "website"} uses infrastructure and map services to provide its features. Those providers may process information under their own privacy policies. External resort, map, booking, and payment links are governed by the policies of the linked service.`] },
    { heading: "5. Your choices", items: [
      mobile ? "Decline device location permission and choose a location manually." : "Decline browser location permission and choose a location manually.",
      mobile ? "Clear the app's stored preferences through device settings." : "Clear the site's local storage through your browser settings.",
      "Contact support about a privacy request or question.",
    ] },
    { heading: "6. Retention and security", paragraphs: [`Local preferences remain ${mobile ? "on your device" : "in your browser"} until you remove them. Information sent to support is retained only as needed to respond and maintain records. Reasonable safeguards are used, but no online service can guarantee absolute security.`] },
    { heading: "7. Children", paragraphs: ["The service is not directed to children under 13, and we do not knowingly collect personal information from children under 13."] },
    { heading: "8. Policy changes", paragraphs: ["This policy may be updated as the service changes. The current version is always available on this page."] },
  ];
}

export const termsSections: LegalSection[] = [
  { heading: "1. Acceptance", paragraphs: ["By using Fall Line, you agree to these Terms of Service. If you do not agree, do not use the service."] },
  { heading: "2. Service purpose", paragraphs: [
    "Fall Line provides resort information, conditions, prices, hours, maps, and related links for general informational and trip-planning purposes.",
    "Resort information can change without notice. Confirm prices, schedules, closures, availability, and restrictions with the resort before travelling.",
  ] },
  { heading: "3. Acceptable use", paragraphs: ["Use the service lawfully. Do not interfere with the service, attempt unauthorized access, scrape or overload systems, or use displayed information to create safety risks."] },
  { heading: "4. Third-party services and links", paragraphs: ["The service may display information from resorts and link to third-party websites, maps, booking systems, and payment providers. Third-party services have their own terms and privacy policies. Fall Line does not control or guarantee them."] },
  { heading: "5. No warranty", paragraphs: ["The service is provided on an as-is and as-available basis. To the extent permitted by law, Fall Line disclaims warranties about accuracy, availability, suitability, or uninterrupted operation."] },
  { heading: "6. Limitation of liability", paragraphs: ["To the extent permitted by law, Fall Line is not responsible for losses, injuries, missed reservations, costs, or damages arising from reliance on displayed information or use of linked third-party services."] },
  { heading: "7. Changes", paragraphs: ["These terms may be updated from time to time. The updated version takes effect when it is published on this page."] },
];
