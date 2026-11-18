import { useState, type ReactNode } from "react";
import { useConvexConnectionState } from "convex/react";
import { router } from "expo-router";
import { Image } from "expo-image";
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import type { Locale } from "@fall-line/shared/i18n/translations";
import { useApp } from "@mobile/providers/AppProvider";
import { colors } from "@mobile/lib/theme";

export function Screen({
  children,
  home = false,
  onFilters,
}: {
  children: ReactNode;
  home?: boolean;
  onFilters?: () => void;
}) {
  const { t, locale, setLocale } = useApp();
  const connection = useConvexConnectionState();
  const [menuOpen, setMenuOpen] = useState(false);
  const entries = [
    [t("resortList"), "/"],
    [t("blog"), "/blog"],
    [t("aboutPage"), "/about"],
    [t("contactUs"), "/contact"],
    [t("terms"), "/terms"],
    [t("privacy"), "/privacy"],
  ] as const;
  return (
    <SafeAreaView style={styles.screen} edges={["top", "bottom"]}>
      <View style={styles.header}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={home ? t("backHome") : t("backAllResorts")}
          onPress={() => home ? router.replace("/") : router.canGoBack() ? router.back() : router.replace("/")}
          style={styles.brand}
        >
          <Image source={require("../../../web/public/icons/icon-512.png")} style={styles.logo} />
          <Text style={styles.brandText}>FALL LINE</Text>
        </Pressable>
        <View style={styles.actions}>
          {onFilters && <Pressable style={styles.filterButton} onPress={onFilters}><Text style={styles.filterText}>{t("filters")}</Text></Pressable>}
          <Pressable accessibilityRole="button" accessibilityLabel={t("menu")} style={styles.menuButton} onPress={() => setMenuOpen(true)}>
            <Text style={styles.menuIcon}>{"\u2630"}</Text>
          </Pressable>
        </View>
      </View>
      {!connection.isWebSocketConnected && connection.connectionRetries > 0 && (
        <Text accessibilityRole="alert" style={styles.offline}>
          {t("offlineReconnecting")}
        </Text>
      )}
      {children}
      <Modal visible={menuOpen} transparent animationType="fade" onRequestClose={() => setMenuOpen(false)}>
        <View style={styles.overlay}>
          <Pressable style={styles.scrim} accessibilityLabel={t("closeMenu")} onPress={() => setMenuOpen(false)} />
          <SafeAreaView style={styles.drawer}>
            <View style={styles.drawerHeader}>
              <Text style={styles.drawerTitle}>{t("menu")}</Text>
              <Pressable accessibilityRole="button" onPress={() => setMenuOpen(false)}><Text style={styles.close}>{"\u00d7"}</Text></Pressable>
            </View>
            <ScrollView>
              <Text style={styles.label}>{t("language")}</Text>
              <View style={styles.languages}>
                {(["en", "fr", "es"] as Locale[]).map((value) => (
                  <Pressable key={value} accessibilityRole="button" accessibilityState={{ selected: locale === value }} style={[styles.language, locale === value && styles.languageSelected]} onPress={() => setLocale(value)}>
                    <Text style={locale === value ? styles.languageSelectedText : styles.languageText}>{value.toUpperCase()}</Text>
                  </Pressable>
                ))}
              </View>
              {entries.map(([label, path]) => (
                <Pressable key={path} style={styles.menuLink} onPress={() => { setMenuOpen(false); router.navigate(path); }}>
                  <Text style={styles.menuLinkText}>{label}</Text>
                  <Text style={styles.chevron}>{"\u203a"}</Text>
                </Pressable>
              ))}
            </ScrollView>
          </SafeAreaView>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return <View style={styles.section}><Text style={styles.sectionTitle}>{title}</Text><View style={styles.card}>{children}</View></View>;
}

export function Action({ label, onPress }: { label: string; onPress: () => void }) {
  return <Pressable accessibilityRole="button" style={styles.action} onPress={onPress}><Text style={styles.actionText}>{label}</Text></Pressable>;
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background },
  header: { height: 66, flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingHorizontal: 16, borderBottomWidth: 1, borderColor: colors.border, backgroundColor: colors.card },
  brand: { flexDirection: "row", alignItems: "center", gap: 7 },
  logo: { width: 33, height: 33, borderRadius: 7 },
  brandText: { color: colors.primary, fontWeight: "800", fontSize: 15, letterSpacing: 1 },
  actions: { flexDirection: "row", alignItems: "center", gap: 8 },
  filterButton: { borderRadius: 20, borderWidth: 1, borderColor: colors.primary, paddingHorizontal: 12, paddingVertical: 9 },
  filterText: { color: colors.primary, fontSize: 12, fontWeight: "700" },
  menuButton: { backgroundColor: colors.primary, borderRadius: 8, width: 38, height: 38, alignItems: "center", justifyContent: "center" },
  menuIcon: { fontSize: 19, color: "white" },
  offline: { backgroundColor: "#fff1d6", color: "#704800", padding: 8, textAlign: "center", fontSize: 12 },
  overlay: { flex: 1, flexDirection: "row", backgroundColor: "#0007" },
  scrim: { flex: 1 },
  drawer: { width: 290, backgroundColor: colors.card, paddingHorizontal: 20 },
  drawerHeader: { height: 64, flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  drawerTitle: { color: colors.text, fontSize: 24, fontWeight: "700" },
  close: { color: colors.muted, fontSize: 30, paddingHorizontal: 5 },
  label: { fontSize: 12, fontWeight: "700", color: colors.muted, marginTop: 12, marginBottom: 8 },
  languages: { flexDirection: "row", gap: 8, marginBottom: 20 },
  language: { borderWidth: 1, borderColor: colors.border, borderRadius: 8, paddingVertical: 9, paddingHorizontal: 14 },
  languageSelected: { backgroundColor: colors.primary, borderColor: colors.primary },
  languageText: { color: colors.text, fontWeight: "700" },
  languageSelectedText: { color: "white", fontWeight: "700" },
  menuLink: { paddingVertical: 16, borderBottomWidth: 1, borderColor: colors.border, flexDirection: "row", justifyContent: "space-between" },
  menuLinkText: { color: colors.text, fontSize: 15, fontWeight: "500" },
  chevron: { color: colors.muted, fontSize: 18 },
  section: { gap: 12, marginTop: 26 },
  sectionTitle: { color: colors.text, fontFamily: "serif", fontSize: 21, fontWeight: "600" },
  card: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, borderRadius: 12, padding: 16, gap: 10 },
  action: { backgroundColor: colors.primary, borderRadius: 9, paddingVertical: 13, alignItems: "center", paddingHorizontal: 16 },
  actionText: { color: "white", fontWeight: "700", textAlign: "center" },
});
