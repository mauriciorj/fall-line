import { useQuery } from "convex/react";
import { useState } from "react";
import { Image } from "expo-image";
import { router, useLocalSearchParams } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import MapView, { Marker, PROVIDER_GOOGLE } from "react-native-maps";
import { api } from "@convex/_generated/api";
import { calculateDistanceKm } from "@fall-line/shared/distance";
import { formatDate } from "@fall-line/shared/i18n/format";
import { pickLocalized } from "@fall-line/shared/i18n/localized";
import { getResortHeroImage, getResortTrailMaps, toResort, toTrackConditions } from "@fall-line/shared/resorts";
import { Action, Screen, Section } from "@mobile/components/Screen";
import { TrailMaps } from "@mobile/components/TrailMaps";
import { assetUrl, openExternalUrl } from "@mobile/lib/links";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

export default function ResortDetail() {
  const { resortId } = useLocalSearchParams<{ resortId: string }>();
  const [heroFailed, setHeroFailed] = useState(false);
  const [trailPage, setTrailPage] = useState(0);
  const { t, locale, coordinates } = useApp();
  const id = typeof resortId === "string" ? resortId : "";
  const dbResort = useQuery(api.resorts.getByResortId, id ? { resortId: id } : "skip");
  const hours = useQuery(api.resortHours.getByResort, dbResort ? { resortId: id } : "skip");
  const status = useQuery(api.weatherAndStatus.getByResort, dbResort ? { resortId: id } : "skip");
  const resort = toResort(dbResort, { trackConditions: toTrackConditions(status) });

  if (dbResort === undefined) return <Screen><Text style={styles.message}>{t("loadingResort")}</Text></Screen>;
  if (!resort) return <Screen><Text style={styles.message}>{t("resortNotFound")}</Text></Screen>;

  const hero = assetUrl(getResortHeroImage(id, resort.country, resort.region));
  const trailMaps = getResortTrailMaps(id, resort.country, resort.region).map(assetUrl).filter((url): url is string => Boolean(url));
  const description = pickLocalized(resort.description, locale);
  const highlights = pickLocalized(resort.highlights, locale);
  const faq = pickLocalized(resort.faq, locale);
  const distance = coordinates && resort.coordinates ? calculateDistanceKm(coordinates, resort.coordinates) : null;
  const activityLabels = [
    [resort.hasAccommodations, "accommodations"], [resort.hasCrossCountry, "crossCountry"],
    [resort.hasLessons, "lessons"], [resort.hasIceSkate, "iceSkating"],
    [resort.hasSnowshoeing, "snowshoeing"], [resort.hasSpa, "spa"], [resort.hasTubing, "tubbing"],
  ] as const;
  const runs = [
    ["green", resort.runs.green], ["blue", resort.runs.blue], ["black", resort.runs.black],
    ["doubleBlack", resort.runs.doubleBlack], ["freeStyle", resort.runs.freeStyle ?? 0],
  ] as const;
  const totalRuns = runs.reduce((total, [, count]) => total + count, 0);
  const prices = [
    ["liftPass", resort.dayTicketPrice], ["skiRental", resort.skiRentalPrice],
    ["snowboardRental", resort.snowBoardRentalPrice], ["lessons", resort.lessonsPrice], ["tubbing", resort.tubbingPrice],
  ] as const;
  const difficultyOrder: Record<string, number> = { green: 1, blue: 2, black: 3, "double-black": 4, "free-style": 5 };
  const rows = [...(resort.trackConditions ?? [])].sort((a, b) =>
    (difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty]) || a.name.localeCompare(b.name),
  );
  const trailPages = Math.ceil(rows.length / 30);
  const currentTrailPage = Math.min(trailPage, Math.max(0, trailPages - 1));
  const difficultyByRun = {
    green: "green", blue: "blue", black: "black", doubleBlack: "double-black", freeStyle: "free-style",
  } as const;
  const source = (timestamp?: number | null, sourceUrl?: string | null) =>
    timestamp ? <Pressable disabled={!sourceUrl} onPress={() => sourceUrl && void openExternalUrl(sourceUrl)}><Text style={styles.updated}>{formatDate(timestamp, locale)}{sourceUrl ? "  \u2197" : ""}</Text></Pressable> : null;

  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.hero}>
          <Image source={hero && !heroFailed ? { uri: hero } : require("../../../../public/icons/icon-512.png")} style={styles.heroImage} contentFit={hero && !heroFailed ? "cover" : "contain"} onError={() => setHeroFailed(true)} />
          <View style={styles.heroCaption}><Text style={styles.heroTitle}>{resort.name}</Text>{distance !== null && <Text style={styles.heroDistance}>{distance.toFixed(1)} {t("distanceAway")}</Text>}</View>
        </View>
        <View style={styles.body}>
          <View style={styles.breadcrumb}>
            <Pressable onPress={() => router.navigate("/")}><Text style={styles.link}>{t("home")}</Text></Pressable>
            {resort.country && <Pressable onPress={() => router.push({ pathname: "/location/[country]", params: { country: resort.country! } })}><Text style={styles.link}> / {resort.country}</Text></Pressable>}
            {resort.country && resort.region && <Pressable onPress={() => router.push({ pathname: "/location/[country]", params: { country: resort.country!, region: resort.region! } })}><Text style={styles.link}> / {resort.region}</Text></Pressable>}
          </View>
          {resort.ticketUrl && <Action label={`${t("buyTickets")} - ${t("from")} $${resort.dayTicketPrice}`} onPress={() => void openExternalUrl(resort.ticketUrl!)} />}
          <View style={styles.activities}>{activityLabels.filter(([active]) => active).map(([, label]) => <Text key={label} style={styles.activity}>{t(label)}</Text>)}</View>
          {description && <Section title={t("aboutTitle", { name: resort.name })}><Text style={styles.paragraph}>{description.value}</Text></Section>}
          {highlights && <Section title={t("highlightsTitle")}>{highlights.value.map((item) => <Text key={item} style={styles.paragraph}>{"\u2022"} {item}</Text>)}</Section>}
          <Section title={t("sectionInfo", { name: resort.name })}>
            <Text style={styles.label}>{t("hoursOperation")}</Text>
            {source(hours?.updatedAt, hours?.sourceUrl)}
            {hours === undefined ? <Text style={styles.muted}>{t("loadingResort")}</Text> : !hours?.hours?.length ? <Text style={styles.muted}>{t("hoursUnavailable")}</Text> : hours.hours.map((section) => (
              <View key={section.name} style={styles.group}>
                <Text style={styles.label}>{section.name}</Text>
                {section.hours?.map((row) => <Text key={`${row.day}-${row.time}`} style={styles.paragraph}>{row.day}: {row.time}</Text>)}
                {section.activities?.map((activity) => <View key={activity.name}><Text style={styles.muted}>{activity.name}</Text>{activity.hours.map((row) => <Text key={`${row.day}-${row.time}`} style={styles.paragraph}>{row.day}: {row.time}</Text>)}</View>)}
              </View>
            ))}
            {resort.email ? <Pressable onPress={() => void openExternalUrl(`mailto:${resort.email}`)}><Text style={styles.link}>{resort.email}</Text></Pressable> : null}
            {resort.phone ? <Pressable onPress={() => void openExternalUrl(`tel:${resort.phone}`)}><Text style={styles.link}>{resort.phone}</Text></Pressable> : null}
            <Text style={styles.paragraph}>{t("rating")}: {resort.rating}</Text>
            {resort.elevation ? <Text style={styles.paragraph}>{t("elevation")}: {resort.elevation}</Text> : null}
            {resort.height ? <Text style={styles.paragraph}>{t("height")}: {resort.height}</Text> : null}
            {resort.website ? <Pressable onPress={() => void openExternalUrl(resort.website)}><Text style={styles.link}>{resort.website}</Text></Pressable> : null}
          </Section>
          {resort.resort_accommodations && <Section title={t("sectionAccommodations", { name: resort.name })}><Pressable onPress={() => void openExternalUrl(resort.resort_accommodations!)}><Text style={styles.link}>{t("accommodations")} {"\u2197"}</Text></Pressable></Section>}
          <Section title={t("sectionTracks", { name: resort.name })}>
            <Text style={styles.label}>{t("trackConditions")}</Text>
            {source(status?.updatedAt, status?.sourceUrl)}
            {rows.length ? <>
              {rows.slice(currentTrailPage * 30, (currentTrailPage + 1) * 30).map((item, index) => <View key={`${item.name}-${index}`} style={styles.row}><Text style={styles.paragraph}>{item.name}</Text><Text style={styles.muted}>{item.condition}</Text></View>)}
              {trailPages > 1 && <View style={styles.row}>
                <Pressable disabled={currentTrailPage === 0} onPress={() => setTrailPage(currentTrailPage - 1)}><Text style={[styles.link, currentTrailPage === 0 && styles.disabled]}>{t("previous")}</Text></Pressable>
                <Text style={styles.muted}>{t("pageOf", { page: currentTrailPage + 1, total: trailPages })}</Text>
                <Pressable disabled={currentTrailPage === trailPages - 1} onPress={() => setTrailPage(currentTrailPage + 1)}><Text style={[styles.link, currentTrailPage === trailPages - 1 && styles.disabled]}>{t("next")}</Text></Pressable>
              </View>}
            </> : runs.filter(([, count]) => count > 0).map(([key, count]) => <Text key={key} style={styles.paragraph}>{t(key)}: {count}</Text>)}
            <TrailMaps urls={trailMaps} label={t("trailMap")} />
          </Section>
          <Section title={t("sectionTerrain", { name: resort.name })}>
            {runs.map(([key, count]) => {
              const tracks = rows.filter((item) => item.difficulty === difficultyByRun[key]);
              const open = tracks.filter((item) => item.condition.toLowerCase() === "open").length;
              return <Text key={key} style={styles.paragraph}>{t(key)}: {count} {t("runs")} ({totalRuns ? Math.round(count / totalRuns * 100) : 0}%){tracks.length ? `  ${open}/${tracks.length} ${t("open")}` : ""}</Text>;
            })}
            {resort.tracksGreenLength ? <Text style={styles.muted}>{t("green")}: {resort.tracksGreenLength}</Text> : null}
            {resort.tracksBlueLength ? <Text style={styles.muted}>{t("blue")}: {resort.tracksBlueLength}</Text> : null}
            {resort.tracksBlackLength ? <Text style={styles.muted}>{t("black")}: {resort.tracksBlackLength}</Text> : null}
          </Section>
          <Section title={t("sectionPricing", { name: resort.name })}>
            {source(resort.updatedAt)}
            {prices.filter(([, amount]) => Boolean(amount && amount > 0)).map(([key, amount]) => <View key={key} style={styles.row}><Text style={styles.paragraph}>{t(key)}</Text><Text style={styles.label}>${amount}</Text></View>)}
          </Section>
          <Section title={t("sectionLocation", { name: resort.name })}>
            <Text style={styles.paragraph}>{resort.address || "--"}</Text>
            {resort.googleMapsUrl ? <Pressable onPress={() => void openExternalUrl(resort.googleMapsUrl)}><Text style={styles.link}>{t("getDirections")} {"\u2197"}</Text></Pressable> : null}
            {resort.coordinates && <MapView provider={PROVIDER_GOOGLE} style={styles.locationMap} initialRegion={{ latitude: resort.coordinates.lat, longitude: resort.coordinates.lng, latitudeDelta: 0.05, longitudeDelta: 0.05 }}><Marker coordinate={{ latitude: resort.coordinates.lat, longitude: resort.coordinates.lng }} title={resort.name} /></MapView>}
          </Section>
          {faq && <Section title={t("faqTitle")}>{faq.value.map((item) => <View key={item.question} style={styles.group}><Text style={styles.label}>{item.question}</Text><Text style={styles.paragraph}>{item.answer}</Text></View>)}</Section>}
        </View>
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  content: { paddingBottom: 40 },
  hero: { height: 260, backgroundColor: colors.pale },
  heroImage: { width: "100%", height: "100%" },
  heroCaption: { position: "absolute", bottom: 0, left: 0, right: 0, backgroundColor: "#0009", padding: 20 },
  heroTitle: { fontFamily: "serif", fontSize: 30, fontWeight: "700", color: "white" },
  heroDistance: { color: "white", marginTop: 4 },
  body: { padding: 18, gap: 8 },
  breadcrumb: { flexDirection: "row", flexWrap: "wrap", paddingBottom: 8 },
  link: { color: colors.primary, fontWeight: "600" },
  activities: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 10 },
  activity: { backgroundColor: colors.pale, color: colors.primary, borderRadius: 15, overflow: "hidden", paddingVertical: 7, paddingHorizontal: 10, fontSize: 12 },
  paragraph: { color: colors.text, lineHeight: 21 },
  label: { fontWeight: "700", color: colors.text },
  muted: { color: colors.muted, fontSize: 13 },
  updated: { color: colors.muted, fontSize: 12 },
  group: { gap: 5, marginVertical: 4 },
  row: { flexDirection: "row", justifyContent: "space-between", gap: 12, paddingVertical: 6 },
  disabled: { opacity: 0.4 },
  locationMap: { height: 220, borderRadius: 8, marginTop: 8 },
  message: { textAlign: "center", color: colors.muted, padding: 40 },
});
