import { useState } from "react";
import { Image } from "expo-image";
import { Modal, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, { useAnimatedStyle, useSharedValue } from "react-native-reanimated";
import { colors } from "@mobile/lib/theme";

function ZoomableImage({ url }: { url: string }) {
  const scale = useSharedValue(1);
  const start = useSharedValue(1);
  const x = useSharedValue(0);
  const y = useSharedValue(0);
  const oldX = useSharedValue(0);
  const oldY = useSharedValue(0);
  const pinch = Gesture.Pinch().onStart(() => { start.value = scale.value; }).onUpdate((event) => {
    scale.value = Math.max(1, Math.min(5, start.value * event.scale));
  }).onEnd(() => { if (scale.value === 1) { x.value = 0; y.value = 0; } });
  const pan = Gesture.Pan().onStart(() => { oldX.value = x.value; oldY.value = y.value; }).onUpdate((event) => {
    if (scale.value > 1) { x.value = oldX.value + event.translationX; y.value = oldY.value + event.translationY; }
  });
  const style = useAnimatedStyle(() => ({ transform: [{ translateX: x.value }, { translateY: y.value }, { scale: scale.value }] }));
  return <GestureDetector gesture={Gesture.Simultaneous(pinch, pan)}><Animated.View style={[styles.zoomImage, style]}><Image source={{ uri: url }} style={styles.image} contentFit="contain" /></Animated.View></GestureDetector>;
}

export function TrailMaps({ urls, label }: { urls: string[]; label: string }) {
  const [visible, setVisible] = useState(false);
  const [index, setIndex] = useState(0);
  if (!urls.length) return null;
  return (
    <View>
      <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={() => setVisible(true)}>
        <Image source={{ uri: urls[0] }} style={styles.preview} contentFit="contain" />
        <Text style={styles.link}>{label}</Text>
      </Pressable>
      <Modal visible={visible} onRequestClose={() => setVisible(false)} animationType="slide">
        <SafeAreaView style={styles.viewer}>
          <View style={styles.bar}><Text style={styles.title}>{label}</Text><Pressable onPress={() => setVisible(false)}><Text style={styles.close}>{"\u00d7"}</Text></Pressable></View>
          <View style={styles.viewport}><ZoomableImage key={urls[index]} url={urls[index]} /></View>
          {urls.length > 1 && <ScrollView horizontal contentContainerStyle={styles.pages}>{urls.map((url, i) => <Pressable key={url} style={[styles.page, index === i && styles.active]} onPress={() => setIndex(i)}><Text style={index === i ? styles.activeText : styles.pageText}>{i + 1}</Text></Pressable>)}</ScrollView>}
        </SafeAreaView>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  preview: { width: "100%", height: 200, borderRadius: 8, backgroundColor: colors.background },
  link: { color: colors.primary, fontWeight: "700", paddingTop: 8 },
  viewer: { flex: 1, backgroundColor: colors.background },
  bar: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 16 },
  title: { fontWeight: "700", color: colors.text, fontSize: 18, flex: 1 },
  close: { fontSize: 30, color: colors.muted },
  viewport: { flex: 1, overflow: "hidden", justifyContent: "center" },
  zoomImage: { width: "100%", height: "100%" },
  image: { width: "100%", height: "100%" },
  pages: { padding: 12, gap: 8 },
  page: { padding: 12, borderRadius: 8, backgroundColor: colors.card },
  active: { backgroundColor: colors.primary },
  pageText: { color: colors.text },
  activeText: { color: "white" },
});
