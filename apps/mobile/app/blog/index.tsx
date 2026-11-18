import { useQuery } from "convex/react";
import { Image } from "expo-image";
import { router } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { api } from "@convex/_generated/api";
import { ArticleMeta, articleStyles, type Article } from "@mobile/components/Article";
import { Screen } from "@mobile/components/Screen";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

export default function Blog() {
  const { t, locale } = useApp();
  const articles = useQuery(api.blog.listPublished) as Article[] | undefined;
  return (
    <Screen>
      <FlatList
        data={articles ?? []}
        keyExtractor={(item) => item.slug}
        contentContainerStyle={styles.body}
        ListHeaderComponent={<View style={styles.intro}><Text style={styles.kicker}>{t("blog")}</Text><Text style={styles.title}>{t("blogTitle")}</Text><Text style={styles.description}>{t("blogDescription")}</Text>{locale !== "en" && <Text style={styles.description}>{t("englishOnly")}</Text>}</View>}
        ListEmptyComponent={<Text style={styles.description}>{articles === undefined ? t("loadingResort") : t("noArticles")}</Text>}
        renderItem={({ item }) => (
          <Pressable style={articleStyles.card} onPress={() => router.push({ pathname: "/blog/[slug]", params: { slug: item.slug } })}>
            {item.heroImageUrl && <Image source={{ uri: item.heroImageUrl }} style={articleStyles.image} contentFit="cover" />}
            <View style={articleStyles.body}><Text style={articleStyles.tags}>{item.tags.join("  /  ")}</Text><Text style={articleStyles.title}>{item.title}</Text><Text style={articleStyles.description} numberOfLines={3}>{item.description}</Text><ArticleMeta article={item} /></View>
          </Pressable>
        )}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  body: { padding: 18, paddingBottom: 40 },
  intro: { gap: 12, paddingVertical: 24 },
  kicker: { color: colors.primary, fontWeight: "800", textTransform: "uppercase", letterSpacing: 2 },
  title: { fontFamily: "serif", fontSize: 32, fontWeight: "700", color: colors.text },
  description: { color: colors.muted, lineHeight: 21 },
});
