import { Alert, Linking } from "react-native";
import * as WebBrowser from "expo-web-browser";

export async function openExternalUrl(value: string) {
  try {
    const url = new URL(value);
    if (url.protocol === "https:") {
      await WebBrowser.openBrowserAsync(url.toString());
      return;
    }
    if (url.protocol === "mailto:" || url.protocol === "tel:") {
      if (await Linking.canOpenURL(value)) {
        await Linking.openURL(value);
        return;
      }
    }
    throw new Error("Unsupported link");
  } catch {
    Alert.alert("Unable to open link", "Check that an appropriate app is installed.");
  }
}

export function assetUrl(path: string): string | null {
  const origin = process.env.EXPO_PUBLIC_SITE_URL;
  if (!origin || !path.startsWith("/")) return null;
  try {
    const base = new URL(origin);
    if (base.protocol !== "https:") return null;
    return new URL(path, base).toString();
  } catch {
    return null;
  }
}
