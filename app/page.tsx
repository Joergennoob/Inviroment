"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useEffect } from "react";
import CardBody from "@/components/ClaimList";
import type { Placement } from "@/components/MapCanvas";
import { allCards, problems } from "@/lib/cards";
import { TYPE_LABEL } from "@/lib/types";

const MapView = dynamic(() => import("@/components/MapCanvas"), { ssr: false });

export default function HomePage() {
  const cards = allCards();
  const ranked = problems();
  const byId = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);
  const [selectedId, setSelectedId] = useState(ranked[0]?.id ?? "");
  const [placement, setPlacement] = useState<Placement | null>(null);
  const [layers, setLayers] = useState<{ id: string; title: string; problem: string; default: boolean }[]>([]);
  const [enabled, setEnabled] = useState<string[]>([]);
  const selected = byId.get(selectedId);

  useEffect(() => {
    void fetch("/data/layers/index.json")
      .then((response) => response.json())
      .then((index: { layers: { id: string; title: string; problem: string; default: boolean }[] }) => {
        setLayers(index.layers);
        setEnabled(index.layers.filter((layer) => layer.default).map((layer) => layer.id));
      })
      .catch(() => setLayers([]));
  }, []);

  const choose = (cardId: string) => {
    setSelectedId(cardId);
    setPlacement(null);
    const byProblem: Record<string, string[]> = {
      "ca-problem-south-coast-air": ["pm25"],
      "ca-problem-san-joaquin-air": ["pm25", "valley-fever"],
      "ca-problem-drinking-water": ["failing-water"],
      "ca-problem-oil-gas-proximity": ["oil-zone", "wells", "schools"],
      "ca-problem-pesticides": ["pesticide"],
      "ca-problem-salton-sea": ["salton-line", "salton-ring"],
      "ca-problem-refineries": ["circles", "facilities"],
      "ca-problem-aliso-canyon": ["circles", "facilities"],
      "ca-problem-pfas": ["pfas"],
      "ca-problem-groundwater-overdraft": ["basins"],
    };
    const turnOn = byProblem[cardId] ?? [];
    if (turnOn.length) setEnabled((current) => Array.from(new Set([...current, ...turnOn])));
  };

  return (
    <div className="shell">
      <header className="top">
        <div>
          <h1>Miljøkart California</h1>
          <p>Ti steder i California der miljøet gjør skade. Klikk i kartet. Til høyre står det hva som er galt, hvem som rammes, og hvem som står bak.</p>
          <details className="help">
            <summary>Slik leser du kartet</summary>
            <p>
              Fargene er områder, for eksempel luft som ikke klarer en grense, vannverk som bryter reglene, eller grunnvann som tappes for hardt. Prikkene er anlegg, brønner eller skoler. Klikk et felt. Panelet til høyre forklarer det med vanlige ord først. Under det ligger de nøyaktige tallene og lenkene. «Bekreftet» betyr at setningen står i et offentlig dokument. «Vi vet ikke om miljøet er årsaken» betyr at tallene henger sammen, men at vi ikke har bevist hvorfor.
            </p>
          </details>
        </div>
        <nav className="nav">
          <Link href="/oversikt/">Rangering</Link>
          <Link href="/kort/ca-problem-south-coast-air/">Kort</Link>
        </nav>
      </header>
      <div className="workspace">
        <aside className="list">
          {ranked.map((card) => (
            <a
              key={card.id}
              href={`#${card.id}`}
              onClick={(event) => {
                event.preventDefault();
                choose(card.id);
              }}
            >
              <strong>
                {card.rank}. {card.name}
              </strong>
              <span>{card.summary[0]?.text}</span>
            </a>
          ))}
        </aside>
        <div className="map-wrap">
          <MapView
            enabled={enabled}
            summaries={Object.fromEntries(cards.map((card) => [card.id, card.summary[0]?.text ?? ""]))}
            onSelect={(cardId, next) => {
              setSelectedId(cardId);
              setPlacement(next);
            }}
          />
          <fieldset className="layers">
            <legend>Lag</legend>
            {layers.map((layer) => (
              <label key={layer.id}>
                <input
                  type="checkbox"
                  checked={enabled.includes(layer.id)}
                  onChange={() =>
                    setEnabled((current) =>
                      current.includes(layer.id) ? current.filter((id) => id !== layer.id) : [...current, layer.id],
                    )
                  }
                />
                {layer.title}
              </label>
            ))}
          </fieldset>
          <div className="basemap-note">
            Bakgrunnskart: OpenFreeMap (OpenStreetMap). Fri bruk uten nøkkel. Attribusjon ligger også nede til høyre på kartet.
          </div>
        </div>
        <aside className="panel">
          {selected ? (
            <>
              <p className="note">{TYPE_LABEL[selected.type]}{selected.rank ? ` · rang ${selected.rank}` : ""}</p>
              <h2 style={{ marginTop: 0 }}>{selected.name}</h2>
              {placement && placement.cardId === selected.id ? (
                <div className="place">
                  <strong>Kilde for plassering. </strong>
                  {placement.name}. {placement.sourceNote} {placement.sourceName}, post {placement.sourceRecordId}.{" "}
                  <a href={placement.sourceUrl}>Kildelenke</a>. Hentet {placement.sourceRetrieved}.
                </div>
              ) : null}
              <CardBody card={selected} cardsById={byId} />
              <p>
                <Link href={`/kort/${selected.id}/`}>Åpne kortet som egen side</Link>
              </p>
            </>
          ) : (
            <p>Velg et punkt eller et problem.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
