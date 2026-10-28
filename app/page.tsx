"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useMemo, useState } from "react";
import { useEffect } from "react";
import CardBody from "@/components/ClaimList";
import PlaceNote from "@/components/PlaceNote";
import type { Placement } from "@/components/MapCanvas";
import { allCards, problems } from "@/lib/cards";
import { TYPE_LABEL } from "@/lib/types";
import { LAYER_TITLE, officialName, plainTitle } from "@/lib/words";

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
          <p>Ti steder der naturen eller forurensning gjør skade på folk. Klikk i kartet. Til høyre står det, med vanlige ord, hva som er galt, hvem som rammes, og hvem som tjener på det.</p>
          <details className="help">
            <summary>Slik leser du kartet</summary>
            <p>
              Fargene er områder. Prikkene er fabrikker, brønner eller skoler. Klikk et felt. Til høyre får du en forklaring først. Under det ligger tallene og lenkene. «I dokumentet» betyr at setningen står i et offentlig papir. «Vi vet ikke om miljøet er årsaken» betyr at sykdom og forurensning er på samme sted, men at vi ikke har bevist hvorfor. Ord som er vanskelige, står i <Link href="/ord/">Ord og forklaringer</Link>.
            </p>
          </details>
        </div>
        <nav className="nav">
          <Link href="/oversikt/">De ti problemene</Link>
          <Link href="/ord/">Ord og forklaringer</Link>
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
                {card.rank}. {plainTitle(card)}
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
            <legend>Hva vil du se?</legend>
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
                {LAYER_TITLE[layer.id] ?? layer.title}
              </label>
            ))}
          </fieldset>
          <div className="basemap-note">
            Bakgrunnskartet viser veier og byer. Det er gratis (OpenStreetMap). Navnet på kartet står også nede til høyre.
          </div>
        </div>
        <aside className="panel">
          {selected ? (
            <>
              <p className="note">{TYPE_LABEL[selected.type]}{selected.rank ? ` · nummer ${selected.rank} av 10` : ""}</p>
              <h2 style={{ marginTop: 0 }}>{plainTitle(selected)}</h2>
              {officialName(selected) ? (
                <details className="tech">
                  <summary>For journalister: tekniske detaljer</summary>
                  <p>Offisielt navn: {officialName(selected)}</p>
                </details>
              ) : null}
              {placement && placement.cardId === selected.id ? (
                <PlaceNote
                  featureName={placement.name}
                  sourceName={placement.sourceName}
                  recordId={placement.sourceRecordId}
                  sourceUrl={placement.sourceUrl}
                  retrieved={placement.sourceRetrieved}
                  note={placement.sourceNote}
                  layer={placement.layer}
                />
              ) : null}
              <CardBody card={selected} cardsById={byId} />
              <p>
                <Link href={`/kort/${selected.id}/`}>Les hele kortet på egen side</Link>
              </p>
            </>
          ) : (
            <p>Klikk et sted i kartet, eller velg et problem til venstre.</p>
          )}
        </aside>
      </div>
    </div>
  );
}
