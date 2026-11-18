import { Image } from "expo-image";
import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { calculateDistanceKm } from "@fall-line/shared/distance";
import { getResortHeroImage } from "@fall-line/shared/resorts";
import type { Resort } from "@fall-line/shared/types/resort";
import { useApp } from "@mobile/providers/AppProvider";
import { assetUrl } from "@mobile/lib/links";
import { colors } from "@mobile/lib/theme";

export function ResortCard({ resort, selected, onPress }: { resort: Resort; selected: boolean; onPress: () => void }) {
  const { t, coordinates } = useApp();
  const url = assetUrl(getResortHeroImage(resort.resortId, resort.country, resort.region));
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const failedImage = url !== null && failedUrl === url;
  const distance = coordinates && resort.coordinates ? calculateDistanceKm(coordinates, resort.coordinates) : null;
  const activities = [
    [resort.hasAccommodations, "accommodations"], [resort.hasCrossCountry, "crossCountry"],
    [resort.hasLessons, "lessons"], [resort.hasIceSkate, "iceSkating"],
    [resort.hasSnowshoeing, "snowshoeing"], [resort.hasSpa, "spa"], [resort.hasTubing, "tubbing"],
  ] as const;
  const price = (value: number | undefined) => value && value > 0 ? `$${value}` : "--";
  return (
    <Pressable accessibilityRole="button" onPress={onPress} style={[styles.card, selected && styles.selected]}>
      <View style={styles.imageWrap}>
        <Image style={styles.image} source={url && !failedImage ? { uri: url } : require("../../../../public/icons/icon-512.png")} contentFit={url && !failedImage ? "cover" : "contain"} onError={() => setFailedUrl(url)} />
        <View style={styles.badges}>
          {resort.height ? <Text style={styles.badge}>{resort.height}</Text> : null}
          {distance !== null ? <Text style={styles.badge}>{distance.toFixed(1)} {t("distanceAway")}</Text> : null}
          <Text style={styles.badge}>{"\u2605"} {resort.rating}</Text>
        </View>
      </View>
      <View style={styles.body}>
        <Text style={styles.name}>{resort.name || resort.resortId}</Text>
        <View style={styles.row}>{activities.filter(([active]) => active).map(([, label]) => <Text key={label} style={styles.activity}>{t(label)}</Text>)}</View>
        <View style={styles.row}>
          {([["green", resort.runs.green, colors.green], ["blue", resort.runs.blue, colors.blue], ["black", resort.runs.black, colors.black], ["doubleBlack", resort.runs.doubleBlack, colors.black], ["freeStyle", resort.runs.freeStyle ?? 0, colors.orange]] as const).map(([label, count, color]) => count > 0 ? <Text key={label} style={[styles.run, { color }]}>{count} {t(label)}</Text> : null)}
        </View>
        <View style={styles.prices}>
          {([[t("liftPass"), price(resort.dayTicketPrice)], [t("skiRental"), price(resort.skiRentalPrice)], [t("snowboardRental"), price(resort.snowBoardRentalPrice)], ...(resort.tubbingPrice ? [[t("tubbing"), price(resort.tubbingPrice)]] : [])] as string[][]).map(([label, amount]) => (
            <View key={label} style={styles.price}><Text style={styles.priceLabel}>{label}</Text><Text style={styles.amount}>{amount}</Text></View>
          ))}
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.card, borderRadius: 13, overflow: "hidden", borderWidth: 1, borderColor: colors.border, marginBottom: 16 },
  selected: { borderColor: colors.primary, borderWidth: 2 },
  imageWrap: { height: 175, backgroundColor: colors.pale },
  image: { width: "100%", height: "100%" },
  badges: { position: "absolute", top: 10, right: 10, flexDirection: "row", gap: 5 },
  badge: { backgroundColor: "#fffffff0", overflow: "hidden", borderRadius: 15, paddingHorizontal: 9, paddingVertical: 5, color: colors.text, fontWeight: "700", fontSize: 11 },
  body: { padding: 16, gap: 12 },
  name: { fontFamily: "serif", fontSize: 21, fontWeight: "600", color: colors.text },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  activity: { color: colors.muted, fontSize: 11 },
  run: { fontSize: 12, fontWeight: "700" },
  prices: { borderTopWidth: 1, borderColor: colors.border, paddingTop: 12, flexDirection: "row", gap: 8 },
  price: { flex: 1, gap: 4 },
  priceLabel: { fontSize: 10, color: colors.muted, textTransform: "uppercase", fontWeight: "700" },
  amount: { color: colors.text, fontWeight: "700" },
});
