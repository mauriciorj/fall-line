import type { ExpoConfig } from "expo/config";

const config: ExpoConfig = {
  name: "Fall Line",
  slug: "fall-line",
  scheme: "fallline",
  version: "0.1.0",
  icon: "../../public/icons/icon-512.png",
  orientation: "default",
  userInterfaceStyle: "light",
  ios: {
    bundleIdentifier: process.env.IOS_BUNDLE_IDENTIFIER || "com.fallline.mobile",
    supportsTablet: false,
  },
  android: {
    package: process.env.ANDROID_PACKAGE || "com.fallline.mobile",
  },
  plugins: [
    "expo-router",
    [
      "expo-location",
      {
        locationWhenInUsePermission:
          "Allow Fall Line to suggest nearby ski regions and show distances.",
      },
    ],
    [
      "react-native-maps",
      {
        iosGoogleMapsApiKey: process.env.GOOGLE_MAPS_IOS_API_KEY,
        androidGoogleMapsApiKey: process.env.GOOGLE_MAPS_ANDROID_API_KEY,
      },
    ],
  ],
};

export default config;
