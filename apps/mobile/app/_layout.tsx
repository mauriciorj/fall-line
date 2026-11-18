import { GestureHandlerRootView } from "react-native-gesture-handler";
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Stack } from "expo-router";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { Text, View } from "react-native";
import { Component, type ReactNode } from "react";
import { AppProvider } from "@mobile/providers/AppProvider";
import { colors } from "@mobile/lib/theme";

const url = process.env.EXPO_PUBLIC_CONVEX_URL;
const convex = url ? new ConvexReactClient(url) : null;

class QueryErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (this.state.failed) {
      return (
        <View style={{ flex: 1, justifyContent: "center", padding: 24, backgroundColor: colors.background }}>
          <Text>Unable to load the app. Check your connection and try again.</Text>
          <Text accessibilityRole="button" onPress={() => this.setState({ failed: false })} style={{ color: colors.primary, marginTop: 16, fontWeight: "700" }}>Try again</Text>
        </View>
      );
    }
    return this.props.children;
  }
}

export default function RootLayout() {
  if (!convex) {
    return (
      <View style={{ flex: 1, justifyContent: "center", padding: 24, backgroundColor: colors.background }}>
        <Text>Set EXPO_PUBLIC_CONVEX_URL to the existing Convex deployment, then restart Expo.</Text>
      </View>
    );
  }
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <ConvexProvider client={convex}>
          <QueryErrorBoundary>
            <AppProvider>
              <Stack screenOptions={{ headerShown: false, contentStyle: { backgroundColor: colors.background } }} />
            </AppProvider>
          </QueryErrorBoundary>
        </ConvexProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}
