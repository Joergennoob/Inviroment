"use client";

import { useEffect, useRef } from "react";
import type { GeoJSONSource, Map } from "maplibre-gl";

type Props = { onSelect: (cardId: string) => void };

export default function MapCanvas({ onSelect }: Props) {
  const node = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);
  const selectRef = useRef(onSelect);
  selectRef.current = onSelect;

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
      const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12 });
      popupHolder.popup = popup;

      map.on("load", async () => {
        const response = await fetch("/data/map.geojson");
        const collection = await response.json();
        const points = {
          type: "FeatureCollection" as const,
          features: collection.features.filter(
            (feature: { geometry: { type: string } }) => feature.geometry.type === "Point",
          ),
        };
        const areas = {
          type: "FeatureCollection" as const,
          features: collection.features.filter(
            (feature: { geometry: { type: string } }) => feature.geometry.type !== "Point",
          ),
        };
        map.addSource("areas", { type: "geojson", data: areas });
        map.addLayer({
          id: "areas-fill",
          type: "fill",
          source: "areas",
          paint: { "fill-color": "#c45c26", "fill-opacity": 0.38 },
        });
        map.addLayer({
          id: "areas-line",
          type: "line",
          source: "areas",
          paint: { "line-color": "#7a3412", "line-width": 1.4 },
        });
        map.addSource("points", {
          type: "geojson",
          data: points,
          cluster: true,
          clusterRadius: 42,
          clusterMaxZoom: 11,
        });
        map.addLayer({
          id: "clusters",
          type: "circle",
          source: "points",
          filter: ["has", "point_count"],
          paint: {
            "circle-color": "#1f4d3a",
            "circle-radius": ["step", ["get", "point_count"], 15, 3, 20, 6, 26],
            "circle-stroke-width": 2,
            "circle-stroke-color": "#f6f3ea",
          },
        });
        map.addLayer({
          id: "cluster-count",
          type: "symbol",
          source: "points",
          filter: ["has", "point_count"],
          layout: { "text-field": ["get", "point_count"], "text-size": 12 },
          paint: { "text-color": "#ffffff" },
        });
        map.addLayer({
          id: "points",
          type: "circle",
          source: "points",
          filter: ["!", ["has", "point_count"]],
          paint: {
            "circle-color": "#1d4e89",
            "circle-radius": 7,
            "circle-stroke-width": 2,
            "circle-stroke-color": "#ffffff",
          },
        });

        map.on("mouseenter", "points", (event) => {
          map.getCanvas().style.cursor = "pointer";
          const feature = event.features?.[0];
          const name = feature?.properties?.name;
          if (!name) return;
          popup.setLngLat(event.lngLat).setText(String(name)).addTo(map);
        });
        map.on("mouseleave", "points", () => {
          map.getCanvas().style.cursor = "";
          popup.remove();
        });
        map.on("mouseenter", "areas-fill", () => {
          map.getCanvas().style.cursor = "pointer";
        });
        map.on("mouseleave", "areas-fill", () => {
          map.getCanvas().style.cursor = "";
        });
        map.on("click", "clusters", async (event) => {
          const feature = event.features?.[0];
          if (!feature || feature.geometry.type !== "Point") return;
          const source = map.getSource("points") as GeoJSONSource;
          const clusterId = Number(feature.properties?.cluster_id);
          const zoom = await source.getClusterExpansionZoom(clusterId);
          map.easeTo({ center: feature.geometry.coordinates as [number, number], zoom });
        });
        const choose = (event: { features?: { properties?: { card_id?: string } }[] }) => {
          const id = event.features?.[0]?.properties?.card_id;
          if (id) selectRef.current(String(id));
        };
        map.on("click", "points", choose);
        map.on("click", "areas-fill", choose);
      });
    }

    void start();
    return () => {
      cancelled = true;
      popupHolder.popup?.remove();
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, []);

  return <div ref={node} className="map" />;
}
