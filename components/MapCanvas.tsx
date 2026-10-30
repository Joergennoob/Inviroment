"use client";

import { useEffect, useRef } from "react";
import type { Map as MlMap } from "maplibre-gl";
import { layerColor } from "@/lib/stage";
import { explainPlacement } from "@/lib/words";

export type Placement = {
  cardId: string;
  name: string;
  layer: string;
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

export type MapFocus = { lng: number; lat: number; zoom: number; token: string };

type Props = {
  enabled: string[];
  summaries: Record<string, string>;
  focus?: MapFocus | null;
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

export default function MapCanvas({ enabled, summaries, focus, onSelect }: Props) {
  const node = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MlMap | null>(null);
  const selectRef = useRef(onSelect);
  const enabledRef = useRef(enabled);
  const summariesRef = useRef(summaries);
  const focusRef = useRef(focus);
  summariesRef.current = summaries;
  focusRef.current = focus;
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
        style: "/map/desk.json",
        center: [-119.4, 36.5],
        zoom: 5.3,
      });
      mapRef.current = map;
      map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
      const popup = new maplibregl.Popup({ closeButton: true, closeOnClick: true, maxWidth: "260px", className: "desk-pop" });
      popupHolder.popup = popup;

      const show = (properties: Record<string, unknown> | null | undefined) => {
        if (!properties?.card_id) return;
        const placement: Placement = {
          cardId: String(properties.card_id),
          name: String(properties.name ?? ""),
          layer: String(properties.layer ?? ""),
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
          if (spec.kind === "cluster" || spec.kind === "circle") {
            map.addSource(sourceId, { type: "geojson", data });
            const color = layerColor(spec.id);
            map.addLayer({
              id: `${spec.id}-heat`,
              type: "heatmap",
              source: sourceId,
              paint: {
                "heatmap-weight": 1,
                "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 0, 0.35, 8, 1],
                "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 0, 5, 8, 14],
                "heatmap-opacity": ["interpolate", ["linear"], ["zoom"], 4, 0.8, 8, 0.4, 10.5, 0],
                "heatmap-color": [
                  "interpolate",
                  ["linear"],
                  ["heatmap-density"],
                  0,
                  "rgba(253,230,138,0)",
                  0.2,
                  "rgba(253,230,138,0.55)",
                  0.55,
                  "rgba(249,115,22,0.75)",
                  1,
                  "rgba(127,29,29,0.92)",
                ],
              },
            });
            map.addLayer({
              id: `${spec.id}-glow`,
              type: "circle",
              source: sourceId,
              paint: {
                "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 1.5, 13, 9],
                "circle-color": color,
                "circle-blur": 1,
                "circle-opacity": ["interpolate", ["linear"], ["zoom"], 7.2, 0, 9, 0.4],
              },
            });
            map.addLayer({
              id: spec.id,
              type: "circle",
              source: sourceId,
              paint: {
                "circle-radius": ["interpolate", ["linear"], ["zoom"], 7, 1, 13, 3.2],
                "circle-color": color,
                "circle-opacity": ["interpolate", ["linear"], ["zoom"], 7.2, 0, 9, 0.95],
                "circle-stroke-width": 0,
              },
            });
            map.on("click", spec.id, (event) => show(event.features?.[0]?.properties));
          } else if (spec.kind === "line") {
            map.addSource(sourceId, { type: "geojson", data });
            map.addLayer({ id: spec.id, type: "line", source: sourceId, paint: { "line-color": layerColor(spec.id), "line-width": 1.5 } });
            map.on("click", spec.id, (event) => show(event.features?.[0]?.properties));
          } else {
            map.addSource(sourceId, { type: "geojson", data });
            const sequential = [
              "case",
              ["==", ["to-string", ["get", "value"]], ""],
              "#E5E5E2",
              [
                "interpolate",
                ["linear"],
                ["to-number", ["get", "value"]],
                0,
                "#FDE68A",
                spec.id === "valley-fever" ? 40 : 2000000,
                "#F97316",
                spec.id === "valley-fever" ? 160 : 12000000,
                "#7F1D1D",
              ],
            ];
            const fill = spec.kind === "choropleth" ? sequential : spec.id === "districts" ? "#6B7075" : layerColor(spec.id);
            map.addLayer({
              id: spec.id,
              type: "fill",
              source: sourceId,
              paint: {
                "fill-color": fill as string,
                "fill-opacity": spec.id === "districts" ? 0.08 : spec.kind === "choropleth" ? 0.78 : 0.34,
              },
            });
            map.addLayer({
              id: `${spec.id}-line`,
              type: "line",
              source: sourceId,
              paint: { "line-color": spec.id === "districts" ? "#6B7075" : layerColor(spec.id), "line-width": spec.id === "districts" ? 0.6 : 1 },
            });
            map.on("click", spec.id, (event) => {
              const properties = event.features?.[0]?.properties;
              if (!properties) return;
              const cardLine = (summariesRef.current[String(properties.card_id ?? "")] ?? "").split(/(?<=\.)\s/)[0] ?? "";
              const explained = explainPlacement({
                featureName: String(properties.name ?? ""),
                sourceName: String(properties.source_name ?? ""),
                recordId: String(properties.source_record_id ?? ""),
                note: String(properties.source_note ?? ""),
                layer: spec.id,
              });
              const value = properties.value === "" || properties.value == null ? "" : `${properties.value} ${properties.value_label ?? ""}`.trim();
              popup
                .setLngLat(event.lngLat)
                .setHTML(
                  `<strong>${escapeHtml(explained.headline)}</strong>${cardLine ? `<div>${escapeHtml(cardLine)}</div>` : ""}<div>${escapeHtml(explained.plain)}</div>${value ? `<div class="mono">${escapeHtml(value)}</div>` : ""}`,
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
            for (const suffix of ["", "-line", "-heat", "-glow", "-clusters", "-count", "-points"]) {
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
        map.resize();
        const pendingFocus = focusRef.current;
        if (pendingFocus) {
          map.easeTo({ center: [pendingFocus.lng, pendingFocus.lat], zoom: pendingFocus.zoom, duration: 900 });
        }
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
    map?.resize();
    map?.__apply?.();
  }, [enabled]);

  useEffect(() => {
    const onResize = () => mapRef.current?.resize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  useEffect(() => {
    if (!focus) return;
    const map = mapRef.current;
    map?.resize();
    map?.easeTo({ center: [focus.lng, focus.lat], zoom: focus.zoom, duration: 1000 });
  }, [focus]);

  return <div ref={node} className="map" />;
}
