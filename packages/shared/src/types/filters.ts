export interface FilterState {
  sortBy: "price" | "rating" | "distance";
  distanceRange: [number, number];
  activities: {
    accommodations: boolean;
    crosscountry: boolean;
    lessons: boolean;
    iceSkating: boolean;
    snowshoeing: boolean;
    spa: boolean;
    tubbing: boolean;
  };
}
