import { router } from "expo-router";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { legalUpdated, privacySections, termsSections } from "@fall-line/shared/content/legal";
import { Screen } from "@mobile/components/Screen";
import { openExternalUrl } from "@mobile/lib/links";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

export function Information({ page }: { page: "about" | "contact" | "privacy" | "terms" }) {
  const { t, locale } = useApp();
  const email = process.env.EXPO_PUBLIC_SUPPORT_EMAIL;
  const site = t("appName");
  const legal = page === "privacy" || page === "terms";
  const sections = page === "privacy" ? privacySections("mobile") : termsSections;
  const title = page === "about" ? t("aboutPage") : page === "contact" ? t("contactUs") : page === "privacy" ? "Privacy Policy" : "Terms of Service";
  return (
    <Screen>
      <ScrollView contentContainerStyle={styles.body}>
        {legal && locale !== "en" && <Text style={styles.muted}>{t("englishOnly")}</Text>}
        <Text style={styles.title}>{title}</Text>
        {legal && <Text style={styles.muted}>Last updated: {legalUpdated}</Text>}
        {page === "about" && <>
          <Text style={styles.paragraph}>{t("aboutIntro", { site })}</Text>
          {([["aboutTeamHeading", "aboutTeamBody"], ["aboutDataHeading", "aboutDataBody"], ["aboutAccuracyHeading", "aboutAccuracyBody"], ["aboutLanguagesHeading", "aboutLanguagesBody"]] as const).map(([heading, body]) => <View key={heading} style={styles.section}><Text style={styles.heading}>{t(heading)}</Text><Text style={styles.paragraph}>{t(body, { site, team: t("teamName") })}</Text></View>)}
          <Pressable onPress={() => router.push("/contact")}><Text style={styles.link}>{t("contactUs")}</Text></Pressable>
        </>}
        {page === "contact" && <>
          <Text style={styles.muted}>{t("contactDescription")}</Text>
          <View style={styles.section}><Text style={styles.heading}>{t("getInTouch")}</Text><Text style={styles.paragraph}>{t("contactBody")}</Text>{email && <Pressable onPress={() => void openExternalUrl(`mailto:${email}`)}><Text style={styles.link}>{email}</Text></Pressable>}</View>
          <Pressable onPress={() => router.push("/about")}><Text style={styles.link}>{t("aboutPage")}</Text></Pressable>
        </>}
        {legal && <>
          {sections.map((section) => <View key={section.heading} style={styles.section}><Text style={styles.heading}>{section.heading}</Text>{section.paragraphs?.map((text) => <Text key={text} style={styles.paragraph}>{text}</Text>)}{section.items?.map((text) => <Text key={text} style={styles.paragraph}>{"\u2022"} {text}</Text>)}</View>)}
          <View style={styles.section}><Text style={styles.heading}>{page === "privacy" ? "9. Contact" : "8. Contact"}</Text><Text style={styles.paragraph}>{page === "privacy" ? "Privacy questions:" : "Questions about these terms:"}</Text><Pressable onPress={() => email ? void openExternalUrl(`mailto:${email}`) : router.push("/contact")}><Text style={styles.link}>{email || t("contactUs")}</Text></Pressable></View>
        </>}
      </ScrollView>
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { padding: 22, paddingBottom: 50, gap: 16 },
  title: { fontFamily: "serif", fontSize: 34, fontWeight: "700", color: colors.text },
  heading: { fontFamily: "serif", fontSize: 22, fontWeight: "700", color: colors.text },
  section: { gap: 10, marginTop: 12 },
  paragraph: { color: colors.text, fontSize: 15, lineHeight: 24 },
  muted: { color: colors.muted, lineHeight: 21 },
  link: { color: colors.primary, fontWeight: "700" },
});
