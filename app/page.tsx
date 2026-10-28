"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useMemo, useState } from "react";
import CardBody from "@/components/ClaimList";
import { allCards, problems } from "@/lib/cards";
import { TYPE_LABEL } from "@/lib/types";

const MapCanvas = dynamic(() => import("@/components/MapCanvas"), { ssr: false });

export default function HomePage() {
  const cards = allCards();
  const ranked = problems();
  const byId = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);
  const [selectedId, setSelectedId] = useState(ranked[0]?.id ?? "");
  const selected = byId.get(selectedId);

  return (
    <div className="shell">
      <header className="top">
        <div>
          <h1>Miljøkart California</h1>
          <p>Ti miljøproblemer, med kilder, status og vei videre til selskap, lov og penger.</p>
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
                setSelectedId(card.id);
              }}
            >
              <strong>
                {card.rank}. {card.name}
              </strong>
              <span>{card.summary[0]?.text.slice(0, 110)}…</span>
            </a>
          ))}
        </aside>
        <div className="map-wrap">
          <MapCanvas onSelect={setSelectedId} />
          <div className="basemap-note">
            Bakgrunnskart: OpenFreeMap (OpenStreetMap). Fri bruk uten nøkkel. Attribusjon ligger også nede til høyre på kartet.
          </div>
        </div>
        <aside className="panel">
          {selected ? (
            <>
              <p className="note">{TYPE_LABEL[selected.type]}{selected.rank ? ` · rang ${selected.rank}` : ""}</p>
              <h2 style={{ marginTop: 0 }}>{selected.name}</h2>
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
