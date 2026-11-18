import { Image } from "expo-image";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { formatDate } from "@fall-line/shared/i18n/format";
import { useApp } from "@mobile/providers/AppProvider";
import { openExternalUrl } from "@mobile/lib/links";
import { colors } from "@mobile/lib/theme";

export type Article = {
  slug: string;
  title: string;
  description: string;
  author?: string | null;
  body: unknown[];
  tags: string[];
  publishedAt: number;
  updatedAt: number;
  heroImageUrl?: string | null;
};

export function ArticleMeta({ article }: { article: Article }) {
  const { locale, t } = useApp();
  const published = formatDate(article.publishedAt, locale);
  const updated = article.updatedAt ? formatDate(article.updatedAt, locale) : published;
  return <Text style={styles.meta}>{t("byAuthor", { author: article.author || t("teamName") })} {"\u00b7"} {t("publishedOn", { date: published })}{updated !== published ? ` \u00b7 ${t("updatedOn", { date: updated })}` : ""}</Text>;
}

export function ArticleBlocks({ blocks }: { blocks: unknown[] }) {
  return <View style={styles.blocks}>{blocks.map((raw, index) => {
    if (!raw || typeof raw !== "object") return null;
    const block = raw as { type?: string; text?: string; level?: number; items?: string[]; url?: string; alt?: string };
    if (block.type === "heading") return <Text key={index} style={styles.heading}>{block.text}</Text>;
    if (block.type === "list") return <View key={index} style={styles.blocks}>{(block.items ?? []).map((item, i) => <Text key={i} style={styles.paragraph}>{"\u2022"} {item}</Text>)}</View>;
    if (block.type === "quote") return <Text key={index} style={styles.quote}>{block.text}</Text>;
    if (block.type === "image" && block.url?.startsWith("https://")) return <View key={index}><Image source={{ uri: block.url }} style={styles.image} contentFit="contain" accessibilityLabel={block.alt} />{block.text && <Text style={styles.meta}>{block.text}</Text>}</View>;
    if (block.type === "link" && block.url) return <Pressable key={index} onPress={() => void openExternalUrl(block.url!)}><Text style={styles.link}>{block.text ?? block.url}</Text></Pressable>;
    return <Text key={index} style={styles.paragraph}>{block.text}</Text>;
  })}</View>;
}

export const articleStyles = StyleSheet.create({
  card: { backgroundColor: colors.card, borderRadius: 12, overflow: "hidden", borderWidth: 1, borderColor: colors.border, marginBottom: 16 },
  image: { height: 185, width: "100%", backgroundColor: colors.pale },
  body: { padding: 17, gap: 10 },
  tags: { color: colors.primary, fontSize: 12, fontWeight: "700" },
  title: { fontFamily: "serif", color: colors.text, fontSize: 23, fontWeight: "700" },
  description: { color: colors.muted, lineHeight: 20 },
});

const styles = StyleSheet.create({
  meta: { color: colors.muted, fontSize: 12, lineHeight: 18 },
  blocks: { gap: 14 },
  heading: { fontFamily: "serif", fontWeight: "700", fontSize: 22, color: colors.text, marginTop: 6 },
  paragraph: { color: colors.text, fontSize: 16, lineHeight: 25 },
  quote: { color: colors.text, fontStyle: "italic", borderLeftWidth: 3, borderColor: colors.primary, paddingLeft: 12, lineHeight: 23 },
  image: { width: "100%", height: 220 },
  link: { color: colors.primary, fontWeight: "700" },
});
