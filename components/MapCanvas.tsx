"use client";

import { useEffect, useRef } from "react";
import type { GeoJSONSource, Map as MlMap } from "maplibre-gl";

export type Placement = {
  cardId: string;
  name: string;
  sourceName: string;
  sourceRecordId: string;
  sourceUrl: string;
  sourceRetrieved: string;
  sourceNote: string;
};

type LayerSpec = {
  id: string;
  file: string;
  filter: string;
  title: string;
  kind: "fill" | "line" | "circle" | "cluster" | "choropleth";
  color: string;
  default: boolean;
};

type Props = {
  enabled: string[];
  summaries: Record<string, string>;
  onSelect: (cardId: string, placement: Placement) => void;
};

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function matches(layerName: string, filter: string): boolean {
  return layerName === filter || layerName.startsWith(`${filter}-`);
}

function asCollection(payload: { features?: { properties?: Record<string, unknown> }[] }, filter: string): GeoJSON.FeatureCollection {
  const features = (payload.features ?? []).filter((feature) => matches(String(feature.properties?.layer ?? ""), filter));
  return { type: "FeatureCollection", features: features as GeoJSON.Feature[] };
}

function wellsCollection(payload: {
  source_name: string;
  source_url: string;
  source_retrieved: string;
  source_note: string;
  points: [number, number, string, string, string][];
}): GeoJSON.FeatureCollection {
  return {
    type: "FeatureCollection",
    features: payload.points.map(([lon, lat, id, cardId, status]) => ({
      type: "Feature",
      geometry: { type: "Point", coordinates: [lon, lat] },
      properties: {
        card_id: cardId,
        name: `${status} ${id}`,
        layer: "wells",
        source_name: payload.source_name,
        source_record_id: id,
        source_url: payload.source_url,
        source_retrieved: payload.source_retrieved,
        source_note: `${payload.source_note} Status: ${status}.`,
      },
    })),
  };
}

export default function MapCanvas({ enabled, summaries, onSelect }: Props) {
  const node = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MlMap | null>(null);
  const selectRef = useRef(onSelect);
  const enabledRef = useRef(enabled);
  const summariesRef = useRef(summaries);
  summariesRef.current = summaries;
  const loaded = useRef(new Set<string>());
  selectRef.current = onSelect;
  enabledRef.current = enabled;

  useEffect(() => {
    let cancelled = false;
    const popupHolder: { popup?: { remove: () => void } } = {};

    async function start() {
      const maplibregl = await import("maplibre-gl");
      await import("maplibre-gl/dist/maplibre-gl.css");
      if (cancelled || !node.current || mapRef.current) return;
      const map = new maplibregl.Map({
        container: node.current,
        style: "https://tiles.openfreemap.org/styles/liberty",
        center: [-119.4, 36.5],
        zoom: 5.3,
      });
      mapRef.current = map;
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
      const popup = new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "280px" });
      popupHolder.popup = popup;

      const show = (properties: Record<string, unknown> | null | undefined) => {
        if (!properties?.card_id) return;
        const placement: Placement = {
          cardId: String(properties.card_id),
          name: String(properties.name ?? ""),
          sourceName: String(properties.source_name ?? ""),
          sourceRecordId: String(properties.source_record_id ?? ""),
          sourceUrl: String(properties.source_url ?? ""),
          sourceRetrieved: String(properties.source_retrieved ?? ""),
          sourceNote: String(properties.source_note ?? ""),
        };
        selectRef.current(placement.cardId, placement);
      };

      map.on("load", async () => {
        const index = await (await fetch("/data/layers/index.json")).json();
        const specs = index.layers as LayerSpec[];
        const pending = new Set<string>();
        const ensure = async (spec: LayerSpec) => {
          if (loaded.current.has(spec.id) || pending.has(spec.id) || !map.getStyle()) return;
          pending.add(spec.id);
          const response = await fetch(`/data/layers/${spec.file}`);
          const payload = await response.json();
          const data = spec.kind === "cluster" ? wellsCollection(payload) : asCollection(payload, spec.filter);
          const sourceId = `src-${spec.id}`;
          if (spec.kind === "cluster") {
            map.addSource(sourceId, { type: "geojson", data, cluster: true, clusterRadius: 48, clusterMaxZoom: 12 });
            map.addLayer({
              id: `${spec.id}-clusters`,
              type: "circle",
              source: sourceId,
              filter: ["has", "point_count"],
              paint: {
                "circle-color": spec.color,
                "circle-radius": ["step", ["get", "point_count"], 12, 50, 16, 200, 22],
                "circle-stroke-width": 1,
                "circle-stroke-color": "#ffffff",
              },
            });
            map.addLayer({
              id: `${spec.id}-count`,
              type: "symbol",
              source: sourceId,
              filter: ["has", "point_count"],
              layout: { "text-field": ["get", "point_count_abbreviated"], "text-size": 11 },
              paint: { "text-color": "#ffffff" },
            });
            map.addLayer({
              id: `${spec.id}-points`,
              type: "circle",
              source: sourceId,
              filter: ["!", ["has", "point_count"]],
              paint: { "circle-color": spec.color, "circle-radius": 4, "circle-stroke-width": 1, "circle-stroke-color": "#ffffff" },
            });
            map.on("click", `${spec.id}-clusters`, async (event) => {
              const feature = event.features?.[0];
              if (!feature || feature.geometry.type !== "Point") return;
              const source = map.getSource(sourceId) as GeoJSONSource;
              const zoom = await source.getClusterExpansionZoom(Number(feature.properties?.cluster_id));
              map.easeTo({ center: feature.geometry.coordinates as [number, number], zoom });
            });
            map.on("click", `${spec.id}-points`, (event) => show(event.features?.[0]?.properties));
          } else if (spec.kind === "line") {
            map.addSource(sourceId, { type: "geojson", data });
            map.addLayer({ id: spec.id, type: "line", source: sourceId, paint: { "line-color": spec.color, "line-width": 2 } });
            map.on("click", spec.id, (event) => show(event.features?.[0]?.properties));
          } else if (spec.kind === "circle") {
            map.addSource(sourceId, { type: "geojson", data, cluster: true, clusterRadius: 36, clusterMaxZoom: 11 });
            map.addLayer({
              id: `${spec.id}-clusters`,
              type: "circle",
              source: sourceId,
              filter: ["has", "point_count"],
              paint: { "circle-color": spec.color, "circle-radius": 13, "circle-stroke-width": 1, "circle-stroke-color": "#fff" },
            });
            map.addLayer({
              id: spec.id,
              type: "circle",
              source: sourceId,
              filter: ["!", ["has", "point_count"]],
              paint: { "circle-color": spec.color, "circle-radius": 5, "circle-stroke-width": 1, "circle-stroke-color": "#fff" },
            });
            map.on("click", spec.id, (event) => show(event.features?.[0]?.properties));
            map.on("click", `${spec.id}-clusters`, async (event) => {
              const feature = event.features?.[0];
              if (!feature || feature.geometry.type !== "Point") return;
              const source = map.getSource(sourceId) as GeoJSONSource;
              const zoom = await source.getClusterExpansionZoom(Number(feature.properties?.cluster_id));
              map.easeTo({ center: feature.geometry.coordinates as [number, number], zoom });
            });
          } else {
            map.addSource(sourceId, { type: "geojson", data });
            const color =
              spec.kind === "choropleth"
                ? [
                    "case",
                    ["==", ["to-string", ["get", "value"]], ""],
                    "#e4ddd0",
                    ["interpolate", ["linear"], ["to-number", ["get", "value"]], 0, "#f4e7c8", spec.id === "valley-fever" ? 20 : 1000000, "#e0b15a", spec.id === "valley-fever" ? 80 : 8000000, "#c45c26", spec.id === "valley-fever" ? 260 : 26000000, "#6b2410"],
                  ]
                : spec.color;
            map.addLayer({
              id: spec.id,
              type: "fill",
              source: sourceId,
              paint: { "fill-color": color as string, "fill-opacity": spec.kind === "choropleth" ? 0.72 : 0.28 },
            });
            map.addLayer({
              id: `${spec.id}-line`,
              type: "line",
              source: sourceId,
              paint: { "line-color": spec.color, "line-width": 1 },
            });
            map.on("click", spec.id, (event) => {
              const properties = event.features?.[0]?.properties;
              if (!properties) return;
              const value = properties.value === "" || properties.value == null ? "" : ` Verdi: ${properties.value} ${properties.value_label ?? ""}.`;
              const plain = summariesRef.current[String(properties.card_id ?? "")] ?? "";
              popup
                .setLngLat(event.lngLat)
                .setHTML(
                  `<strong>${escapeHtml(String(properties.name ?? ""))}</strong><div>${escapeHtml(plain)}</div><div>${escapeHtml(value)}</div><div><strong>Kilde for plassering.</strong> ${escapeHtml(String(properties.source_note ?? ""))} ${escapeHtml(String(properties.source_name ?? ""))}, post ${escapeHtml(String(properties.source_record_id ?? ""))}. <a href="${escapeHtml(String(properties.source_url ?? ""))}" target="_blank" rel="noreferrer">Kildelenke</a>. Hentet ${escapeHtml(String(properties.source_retrieved ?? ""))}.</div>`,
                )
                .addTo(map);
              show(properties);
            });
          }
          loaded.current.add(spec.id);
          pending.delete(spec.id);
          applyVisibility(map, specs);
        };

        const applyVisibility = (target: MlMap, all: LayerSpec[]) => {
          const on = new Set(enabledRef.current);
          for (const spec of all) {
            const visible = on.has(spec.id) ? "visible" : "none";
            for (const suffix of ["", "-line", "-clusters", "-count", "-points"]) {
              const id = suffix ? `${spec.id}${suffix}` : spec.id;
              if (target.getLayer(id)) target.setLayoutProperty(id, "visibility", visible);
            }
          }
        };

        const sync = async () => {
          for (const spec of specs) {
            if (enabledRef.current.includes(spec.id)) await ensure(spec);
          }
          applyVisibility(map, specs);
        };
        (map as MlMap & { __apply?: () => void }).__apply = () => {
          void sync();
        };
        await sync();
      });
    }

    void start();
    return () => {
      cancelled = true;
      popupHolder.popup?.remove();
      mapRef.current?.remove();
      mapRef.current = null;
      loaded.current.clear();
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current as (MlMap & { __apply?: () => void }) | null;
    map?.__apply?.();
  }, [enabled]);

  return <div ref={node} className="map" />;
}
