import { useMemo } from "react";
import { useQueries } from "convex/react";
import { router, useLocalSearchParams } from "expo-router";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "@convex/_generated/api";
import { regionStats } from "@fall-line/shared/locations";
import { toResort } from "@fall-line/shared/resorts";
import { locationKey } from "@fall-line/shared/types/location";
import type { Resort } from "@fall-line/shared/types/resort";
import { ResortCard } from "@mobile/components/ResortCard";
import { Screen } from "@mobile/components/Screen";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

export default function LocationDirectory() {
  const { country, region } = useLocalSearchParams<{ country: string; region?: string }>();
  const { locations, t } = useApp();
  const matching = useMemo(
    () => locations.filter((item) => item.country === country && (!region || item.region === region)),
    [locations, country, region],
  );
  const queries = useMemo(
    () => Object.fromEntries(matching.map((location) => [
      locationKey(location),
      { query: api.resorts.list, args: { continent: location.continent, country: location.country, region: location.region } },
    ])),
    [matching],
  );
  const results = useQueries(queries);
  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.body}>
        <Text style={styles.title}>{region ? t("regionHeading", { region, country }) : country}</Text>
        {matching.map((location) => {
          const response = results[locationKey(location)];
          const resorts = Array.isArray(response)
            ? response.map((item) => toResort(item)).filter((item): item is Resort => item !== null)
            : [];
          const stats = regionStats(resorts);
          return (
            <View key={locationKey(location)} style={styles.region}>
              {!region && <Text style={styles.heading}>{location.region}</Text>}
              {response === undefined ? <Text style={styles.muted}>{t("loadingResorts")}</Text> :
                response instanceof Error ? <Text style={styles.muted}>{t("unableLoadRegion")}</Text> :
                  resorts.length === 0 ? <Text style={styles.muted}>{t("noResorts")}</Text> : <>
                    <Text style={styles.muted}>{stats.count} resorts | {stats.totalRuns} {t("runs")}</Text>
                    {resorts.map((resort) => <ResortCard key={resort.resortId} resort={resort} selected={false} onPress={() => router.push({ pathname: "/resort/[resortId]", params: { resortId: resort.resortId } })} />)}
                  </>}
            </View>
          );
        })}
        {matching.length === 0 && <Text style={styles.muted}>{t("noResorts")}</Text>}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { padding: 18, paddingBottom: 40, gap: 18 },
  title: { fontFamily: "serif", fontWeight: "700", fontSize: 29, color: colors.text },
  heading: { fontFamily: "serif", fontWeight: "700", fontSize: 22, color: colors.text },
  region: { gap: 12 },
  muted: { color: colors.muted },
});
