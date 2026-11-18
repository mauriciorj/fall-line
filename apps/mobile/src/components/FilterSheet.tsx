import { useState } from "react";
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { defaultFilters } from "@fall-line/shared/filters";
import type { FilterState } from "@fall-line/shared/types/filters";
import { locationKey, locationLabel } from "@fall-line/shared/types/location";
import { useApp } from "@mobile/providers/AppProvider";
import { Action } from "./Screen";
import { colors } from "@mobile/lib/theme";

export function FilterSheet({ visible, close }: { visible: boolean; close: () => void }) {
  const { t, locations, selectedLocation, setLocation, coordinates, detectLocation, filters, setFilters } = useApp();
  const [draft, setDraft] = useState(filters);
  const [choosingLocation, setChoosingLocation] = useState(false);
  const activities: [keyof FilterState["activities"], string][] = [
    ["accommodations", "accommodations"], ["crosscountry", "crossCountry"],
    ["lessons", "lessons"], ["iceSkating", "iceSkating"],
    ["snowshoeing", "snowshoeing"], ["spa", "spa"], ["tubbing", "tubbing"],
  ];
  return (
    <Modal visible={visible} animationType="slide" onRequestClose={close}>
      <SafeAreaView style={styles.screen}>
        <View style={styles.header}><Text style={styles.title}>{t("filterResorts")}</Text><Pressable onPress={close}><Text style={styles.close}>{"\u00d7"}</Text></Pressable></View>
        <ScrollView contentContainerStyle={styles.body}>
          <Text style={styles.label}>{t("location")}</Text>
          <Pressable style={styles.location} onPress={() => setChoosingLocation(!choosingLocation)}>
            <Text style={styles.locationText}>{selectedLocation ? locationLabel(selectedLocation) : t("selectLocation")}</Text>
            <Text>{"\u2304"}</Text>
          </Pressable>
          {choosingLocation && locations.map((item) => (
            <Pressable key={locationKey(item)} style={styles.locationOption} onPress={() => { setLocation(item); setChoosingLocation(false); }}>
              <Text style={styles.text}>{locationLabel(item)}</Text>
            </Pressable>
          ))}
          <Pressable onPress={() => void detectLocation()}><Text style={styles.link}>{t("useLocation")}</Text></Pressable>
          <Text style={styles.label}>{t("sortBy")}</Text>
          <View style={styles.wrap}>
            {(["price", "rating", "distance"] as const).map((key) => (
              <Pressable key={key} disabled={key === "distance" && !coordinates} accessibilityState={{ selected: draft.sortBy === key, disabled: key === "distance" && !coordinates }} style={[styles.chip, draft.sortBy === key && styles.selected, key === "distance" && !coordinates && styles.disabled]} onPress={() => setDraft({ ...draft, sortBy: key })}>
                <Text style={draft.sortBy === key ? styles.selectedText : styles.text}>{t(key === "price" ? "liftPrice" : key)}</Text>
              </Pressable>
            ))}
          </View>
          <Text style={styles.label}>{t("activities")}</Text>
          <View style={styles.wrap}>
            {activities.map(([key, label]) => (
              <Pressable key={key} accessibilityRole="checkbox" accessibilityState={{ checked: draft.activities[key] }} style={[styles.chip, draft.activities[key] && styles.selected]} onPress={() => setDraft({ ...draft, activities: { ...draft.activities, [key]: !draft.activities[key] } })}>
                <Text style={draft.activities[key] ? styles.selectedText : styles.text}>{t(label)}</Text>
              </Pressable>
            ))}
          </View>
          <Pressable onPress={() => { setDraft(defaultFilters); setFilters(defaultFilters); }}><Text style={styles.link}>{t("clearAll")}</Text></Pressable>
          <Action label={t("apply")} onPress={() => { setFilters(draft); close(); }} />
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 20, borderBottomWidth: 1, borderColor: colors.border },
  title: { fontFamily: "serif", fontWeight: "700", fontSize: 24, color: colors.text },
  close: { fontSize: 30, color: colors.muted },
  body: { padding: 20, gap: 14, paddingBottom: 40 },
  label: { color: colors.muted, fontWeight: "700", marginTop: 10, fontSize: 12 },
  location: { borderWidth: 1, borderColor: colors.border, backgroundColor: "white", borderRadius: 9, padding: 14, flexDirection: "row", justifyContent: "space-between" },
  locationText: { color: colors.text, flexShrink: 1 },
  locationOption: { padding: 12, backgroundColor: "white", borderBottomWidth: 1, borderColor: colors.border },
  text: { color: colors.text },
  link: { color: colors.primary, fontWeight: "700", paddingVertical: 4 },
  wrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { paddingVertical: 10, paddingHorizontal: 13, borderRadius: 9, borderWidth: 1, borderColor: colors.border, backgroundColor: "white" },
  selected: { backgroundColor: colors.primary, borderColor: colors.primary },
  selectedText: { color: "white", fontWeight: "700" },
  disabled: { opacity: 0.4 },
});
