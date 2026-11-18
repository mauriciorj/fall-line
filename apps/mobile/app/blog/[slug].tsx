import { useQuery } from "convex/react";
import { Image } from "expo-image";
import { useLocalSearchParams } from "expo-router";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { api } from "@convex/_generated/api";
import { ArticleBlocks, ArticleMeta, articleStyles, type Article } from "@mobile/components/Article";
import { Screen } from "@mobile/components/Screen";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

export default function BlogDetail() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const { t, locale } = useApp();
  const article = useQuery(api.blog.getPublishedBySlug, slug ? { slug } : "skip") as Article | null | undefined;
  return (
    <Screen>
      {!article ? <Text style={styles.message}>{article === undefined ? t("loadingResort") : t("articleNotFound")}</Text> : (
        <ScrollView contentContainerStyle={styles.body}>
          {locale !== "en" && <Text style={articleStyles.description}>{t("englishOnly")}</Text>}
          <Text style={articleStyles.tags}>{article.tags.join("  /  ")}</Text>
          <Text style={styles.title}>{article.title}</Text>
          <Text style={styles.description}>{article.description}</Text>
          <ArticleMeta article={article} />
          {article.heroImageUrl && <Image source={{ uri: article.heroImageUrl }} style={styles.hero} contentFit="cover" />}
          <View style={styles.content}><ArticleBlocks blocks={article.body} /></View>
        </ScrollView>
      )}
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { padding: 20, paddingBottom: 50, gap: 16 },
  title: { color: colors.text, fontFamily: "serif", fontSize: 34, fontWeight: "700" },
  description: { color: colors.muted, fontSize: 17, lineHeight: 24 },
  hero: { width: "100%", height: 220, borderRadius: 12, backgroundColor: colors.pale },
  content: { paddingTop: 10 },
  message: { textAlign: "center", color: colors.muted, padding: 40 },
});
