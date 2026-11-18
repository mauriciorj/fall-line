import AsyncStorage from "@react-native-async-storage/async-storage";
import { useQuery } from "convex/react";
import * as Location from "expo-location";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { Alert } from "react-native";
import { api } from "@convex/_generated/api";
import { applyResortFilters, defaultFilters } from "@fall-line/shared/filters";
import { getTranslator, locales, type Locale } from "@fall-line/shared/i18n/translations";
import { toResort } from "@fall-line/shared/resorts";
import { findDefaultLocation, locationKey, type LocationOption } from "@fall-line/shared/types/location";
import type { FilterState } from "@fall-line/shared/types/filters";
import type { Coordinates, Resort } from "@fall-line/shared/types/resort";

const LOCALE_KEY = "fallline.locale";
const LOCATION_KEY = "selected-location";
const SPLIT_KEY = "fallline.map-split";
const LOCATION_PROMPT_KEY = "fallline.location-prompted";

function normalize(value: string) {
  return value.normalize("NFKD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function matchDetectedLocation(
  locations: LocationOption[],
  address: Location.LocationGeocodedAddress,
) {
  const aliases: Record<string, string> = {
    ca: "canada", us: "united states", usa: "united states", "united states of america": "united states",
    qc: "quebec", on: "ontario", ab: "alberta", bc: "british columbia",
    mb: "manitoba", nb: "new brunswick", nl: "newfoundland and labrador",
    ns: "nova scotia", pe: "prince edward island", sk: "saskatchewan",
  };
  const normalized = (value?: string | null) => {
    const result = normalize(value ?? "");
    return aliases[result] ?? result;
  };
  const countries = [normalized(address.isoCountryCode), normalized(address.country)].filter(Boolean);
  const region = normalized(address.region);
  const countryLocations = locations.filter((item) => countries.includes(normalized(item.country)));
  return countryLocations.find((item) => normalized(item.region) === region)
    ?? countryLocations.find((item) => normalize(item.region) === "unknown")
    ?? countryLocations[0];
}

type AppState = {
  locale: Locale;
  t: ReturnType<typeof getTranslator>;
  setLocale: (locale: Locale) => void;
  locations: LocationOption[];
  selectedLocation: LocationOption | null;
  setLocation: (location: LocationOption) => void;
  coordinates: Coordinates | null;
  detectLocation: () => Promise<void>;
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  resorts: Resort[];
  isLoading: boolean;
  updatedAt: number | null;
  selectedResort: string | null;
  setSelectedResort: (id: string | null) => void;
  split: number;
  setSplit: (value: number) => void;
};

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [locale, updateLocale] = useState<Locale>("en");
  const t = useMemo(() => getTranslator(locale), [locale]);
  const [savedLocation, setSavedLocation] = useState<string | null>(null);
  const [storageReady, setStorageReady] = useState(false);
  const [explicitLocation, updateLocation] = useState<LocationOption | null>(null);
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [filters, setFilters] = useState<FilterState>(defaultFilters);
  const [selectedResort, setSelectedResort] = useState<string | null>(null);
  const [split, updateSplit] = useState(0.5);
  const dbLocations = useQuery(api.locations.list);
  const locations = useMemo(() => dbLocations ?? [], [dbLocations]);
  const selectedLocation = explicitLocation ?? (storageReady && dbLocations
    ? locations.find((item) => locationKey(item) === savedLocation) ?? findDefaultLocation(locations) ?? null
    : null);

  useEffect(() => {
    AsyncStorage.multiGet([LOCALE_KEY, LOCATION_KEY, SPLIT_KEY])
      .then((values) => {
        const saved = Object.fromEntries(values);
        if (locales.includes(saved[LOCALE_KEY] as Locale)) updateLocale(saved[LOCALE_KEY] as Locale);
        setSavedLocation(saved[LOCATION_KEY]);
        const ratio = Number(saved[SPLIT_KEY]);
        if (saved[SPLIT_KEY] && ratio >= 0.15 && ratio <= 0.85) updateSplit(ratio);
      })
      .catch(() => {})
      .finally(() => setStorageReady(true));
  }, []);

  const setLocation = useCallback((location: LocationOption) => {
    updateLocation(location);
    setSavedLocation(locationKey(location));
    setSelectedResort(null);
    void AsyncStorage.setItem(LOCATION_KEY, locationKey(location));
  }, []);

  const setLocale = useCallback((value: Locale) => {
    updateLocale(value);
    void AsyncStorage.setItem(LOCALE_KEY, value);
  }, []);

  const setSplit = useCallback((value: number) => {
    updateSplit(value);
    void AsyncStorage.setItem(SPLIT_KEY, String(value));
  }, []);

  const detectLocation = useCallback(async () => {
    try {
      const permission = await Location.requestForegroundPermissionsAsync();
      if (!permission.granted) {
        Alert.alert(t("locationUnavailable"), t("chooseRegionManually"));
        return;
      }
      const position = await Promise.race([
        Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Low }),
        new Promise<never>((_, reject) => setTimeout(() => reject(new Error("Location timed out")), 10000)),
      ]);
      const point = { lat: position.coords.latitude, lng: position.coords.longitude };
      setCoordinates(point);
      const [address] = await Location.reverseGeocodeAsync({
        latitude: point.lat,
        longitude: point.lng,
      });
      const matched = address && matchDetectedLocation(locations, address);
      if (matched) setLocation(matched);
      else Alert.alert(t("regionNotFound"), t("chooseRegionManually"));
    } catch {
      Alert.alert(t("locationUnavailable"), t("chooseRegionManually"));
    }
  }, [locations, setLocation, t]);

  useEffect(() => {
    if (!storageReady || !dbLocations || savedLocation || !locations.length) return;
    let cancelled = false;
    void AsyncStorage.getItem(LOCATION_PROMPT_KEY).then(async (prompted) => {
      if (cancelled || prompted) return;
      await AsyncStorage.setItem(LOCATION_PROMPT_KEY, "1");
      if (cancelled) return;
      const permission = await Location.getForegroundPermissionsAsync();
      if (cancelled) return;
      if (permission.granted) {
        void detectLocation();
      } else if (permission.canAskAgain) {
        Alert.alert(t("useLocation"), t("locationPrompt"), [
          { text: t("notNow"), style: "cancel" },
          { text: t("useLocation"), onPress: () => void detectLocation() },
        ]);
      }
    }).catch(() => {});
    return () => { cancelled = true; };
  }, [dbLocations, detectLocation, locations, savedLocation, storageReady, t]);

  const dbResorts = useQuery(api.resorts.list, selectedLocation ?? "skip");
  const allResorts = useMemo(
    () => (dbResorts ?? []).map((item) => toResort(item)).filter((item): item is Resort => item !== null),
    [dbResorts],
  );
  const resorts = useMemo(() => applyResortFilters(allResorts, filters, coordinates), [allResorts, filters, coordinates]);
  const updatedAt = useMemo(
    () => allResorts.reduce<number | null>((latest, resort) => resort.updatedAt ? Math.max(latest ?? 0, resort.updatedAt) : latest, null),
    [allResorts],
  );

  const value: AppState = {
    locale, t, setLocale, locations, selectedLocation, setLocation,
    coordinates, detectLocation, filters, setFilters, resorts,
    isLoading: !storageReady || dbLocations === undefined || (selectedLocation !== null && dbResorts === undefined),
    updatedAt, selectedResort, setSelectedResort, split, setSplit,
  };
  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error("AppProvider is required");
  return context;
}
