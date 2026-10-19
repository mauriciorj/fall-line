"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api";
import { getResortLocationPath } from "@/utils/convexResort";

const LegacyPlaceRedirect = () => {
  const { id } = useParams<{ id?: string | string[] }>();
  const router = useRouter();
  const resortId = Array.isArray(id) ? id.at(-1) : id;
  const resort = useQuery(
    api.resorts.getByResortId,
    resortId ? { resortId } : "skip",
  );

  useEffect(() => {
    if (!resortId || resort === undefined) return;

    router.replace(
      getResortLocationPath(
        resort?.resortId ?? resortId,
        resort?.country,
        resort?.region,
      ),
    );
  }, [resort, resortId, router]);

  return null;
};

export default LegacyPlaceRedirect;
