import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { router } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import MapView, { Marker, PROVIDER_GOOGLE } from "react-native-maps";
import { Gesture, GestureDetector } from "react-native-gesture-handler";
import Animated, { runOnJS, useAnimatedStyle, useSharedValue } from "react-native-reanimated";
import type { Resort } from "@fall-line/shared/types/resort";
import { FilterSheet } from "@mobile/components/FilterSheet";
import { ResortCard } from "@mobile/components/ResortCard";
import { Screen } from "@mobile/components/Screen";
import { colors } from "@mobile/lib/theme";
import { useApp } from "@mobile/providers/AppProvider";

const HANDLE_HEIGHT = 44;
const INITIAL_CENTER = { latitude: 44.5, longitude: -80, latitudeDelta: 3, longitudeDelta: 3 };

export default function Home() {
  const { t, selectedLocation, resorts, isLoading, coordinates, selectedResort, setSelectedResort, split, setSplit } = useApp();
  const [filterOpen, setFilterOpen] = useState(false);
  const [height, setHeight] = useState(0);
  const [mapReady, setMapReady] = useState(false);
  const list = useRef<FlatList<Resort>>(null);
  const map = useRef<MapView>(null);
  const ratio = useSharedValue(split);
  const startingRatio = useSharedValue(split);
  const availableHeight = Math.max(0, height - HANDLE_HEIGHT);
  const mapped = useMemo(() => resorts.filter((item) => item.coordinates), [resorts]);
  const markerKey = mapped.map((item) => item.resortId).join("|");

  useEffect(() => { ratio.value = split; }, [ratio, split]);
  useEffect(() => {
    if (!mapReady || mapped.length === 0) return;
    const points = mapped.map((item) => ({ latitude: item.coordinates!.lat, longitude: item.coordinates!.lng }));
    if (points.length === 1) {
      map.current?.animateToRegion({ ...points[0], latitudeDelta: 0.08, longitudeDelta: 0.08 }, 300);
    } else {
      map.current?.fitToCoordinates(points, { edgePadding: { top: 45, right: 45, bottom: 45, left: 45 }, animated: true });
    }
    // Keep the current camera while the divider is dragged.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapReady, markerKey]);

  const select = useCallback((id: string) => {
    setSelectedResort(id);
    const index = resorts.findIndex((item) => item.resortId === id);
    if (index >= 0) list.current?.scrollToIndex({ index, animated: true, viewPosition: 0 });
  }, [resorts, setSelectedResort]);

  const lower = availableHeight ? Math.min(0.5, Math.max(0.15, 100 / availableHeight)) : 0.15;
  const upper = 1 - lower;
  useEffect(() => {
    if (!availableHeight) return;
    const clamped = Math.min(upper, Math.max(lower, split));
    if (clamped !== split) setSplit(clamped);
  }, [availableHeight, lower, upper, split, setSplit]);
  const gesture = Gesture.Pan()
    .onBegin(() => { startingRatio.value = ratio.value; })
    .onUpdate((event) => {
      if (availableHeight > 0) ratio.value = Math.min(upper, Math.max(lower, startingRatio.value + event.translationY / availableHeight));
    })
    .onEnd(() => { runOnJS(setSplit)(ratio.value); });
  const mapStyle = useAnimatedStyle(() => ({ height: availableHeight * ratio.value }));
  const resize = (next: number) => setSplit(Math.min(upper, Math.max(lower, next)));

  return (
    <Screen home onFilters={() => setFilterOpen(true)}>
      <View style={styles.main} onLayout={(event) => setHeight(event.nativeEvent.layout.height)}>
        <Animated.View style={[styles.map, mapStyle]}>
          <MapView ref={map} provider={PROVIDER_GOOGLE} initialRegion={INITIAL_CENTER} style={StyleSheet.absoluteFill} onMapReady={() => setMapReady(true)}>
            {coordinates && <Marker coordinate={{ latitude: coordinates.lat, longitude: coordinates.lng }} title={t("yourLocation")} pinColor="#2563eb" />}
            {mapped.map((resort) => (
              <Marker key={resort.resortId} coordinate={{ latitude: resort.coordinates!.lat, longitude: resort.coordinates!.lng }} title={resort.name} pinColor={selectedResort === resort.resortId ? colors.primary : "#8fb7f2"} onPress={() => select(resort.resortId)} />
            ))}
          </MapView>
        </Animated.View>
        <GestureDetector gesture={gesture}>
          <Animated.View
            accessibilityRole="adjustable"
            accessibilityLabel={t("resizeMap")}
            accessibilityValue={{ min: Math.round(lower * 100), max: Math.round(upper * 100), now: Math.round(split * 100) }}
            accessibilityActions={[{ name: "increment" }, { name: "decrement" }, { name: "activate", label: t("resetSplit") }]}
            onAccessibilityAction={(event) => {
              if (event.nativeEvent.actionName === "increment") resize(split + 0.1);
              if (event.nativeEvent.actionName === "decrement") resize(split - 0.1);
              if (event.nativeEvent.actionName === "activate") resize(0.5);
            }}
            style={styles.handle}
          >
            <View style={styles.handleBar} />
          </Animated.View>
        </GestureDetector>
        <FlatList
          ref={list}
          style={styles.list}
          data={resorts}
          keyExtractor={(item) => item.resortId}
          contentContainerStyle={styles.listContent}
          onScrollToIndexFailed={({ index, averageItemLength }) => {
            list.current?.scrollToOffset({ offset: averageItemLength * index, animated: false });
            setTimeout(() => list.current?.scrollToIndex({ index, animated: true }), 250);
          }}
          ListHeaderComponent={
            <View style={styles.intro}>
              <Text style={styles.heading}>{t("homeTitle", { region: selectedLocation?.region ?? "Ontario" })}</Text>
              <Text style={styles.subtitle}>{t("homeIntro", { region: selectedLocation?.region ?? "Ontario" })}</Text>
              {selectedLocation && <Pressable onPress={() => router.push({ pathname: "/location/[country]", params: { country: selectedLocation.country, region: selectedLocation.region } })}><Text style={styles.link}>{t("allResortsIn", { region: selectedLocation.region })} {"\u2192"}</Text></Pressable>}
            </View>
          }
          ListEmptyComponent={<Text style={styles.empty}>{isLoading ? t("loadingResorts") : t("noResorts")}</Text>}
          renderItem={({ item }) => <ResortCard resort={item} selected={selectedResort === item.resortId} onPress={() => router.push({ pathname: "/resort/[resortId]", params: { resortId: item.resortId } })} />}
        />
      </View>
      {filterOpen && <FilterSheet visible close={() => setFilterOpen(false)} />}
    </Screen>
  );
}

const styles = StyleSheet.create({
  main: { flex: 1 },
  map: { width: "100%", backgroundColor: colors.pale },
  handle: { height: HANDLE_HEIGHT, alignItems: "center", justifyContent: "center", backgroundColor: colors.card, borderTopWidth: 1, borderBottomWidth: 1, borderColor: colors.border },
  handleBar: { width: 54, height: 5, borderRadius: 4, backgroundColor: "#a4afba" },
  list: { flex: 1 },
  listContent: { paddingHorizontal: 18, paddingBottom: 30 },
  intro: { paddingVertical: 18, gap: 7 },
  heading: { fontFamily: "serif", fontSize: 21, fontWeight: "600", color: colors.text },
  subtitle: { color: colors.muted, lineHeight: 20 },
  link: { color: colors.primary, fontWeight: "700", paddingVertical: 4 },
  empty: { textAlign: "center", color: colors.muted, paddingVertical: 40 },
});
