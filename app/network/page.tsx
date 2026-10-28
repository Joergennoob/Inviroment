"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import edgesFile from "@/data/network/edges.json";
import nodesFile from "@/data/network/nodes.json";

const LABELS: Record<string, string> = {
  employed_by: "Ansatt hos",
  represents: "Registrert for",
  firm_roster: "Via firmaet",
  contributed_to: "Bidrag",
  voted_on: "Stemme",
  stated: "Uttalelse",
  relates_to: "Loven og problemet",
  lobbied_on: "Sak på skjema",
};

export default function NetworkPage() {
  const [kind, setKind] = useState("represents");
  const names = useMemo(() => new Map(nodesFile.nodes.map((node) => [node.id, node.name])), []);
  const edges = edgesFile.edges.filter((edge) => edge.type === kind).slice(0, 80);
  const kinds = Array.from(new Set(edgesFile.edges.map((edge) => edge.type)));

  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/lobbyister/">Lobbyister</Link>
      </p>
      <h1>Nettverk</h1>
      <p className="note">
        {edgesFile.edges.length} kanter. Den lesbare listen over firma og personer ligger på Lobbyister. Her er råkantene, med status.
      </p>
      <div className="filters">
        {kinds.map((item) => (
          <button key={item} type="button" className={kind === item ? "on" : ""} onClick={() => setKind(item)}>
            {LABELS[item] || item}
          </button>
        ))}
      </div>
      <ul className="plain">
        {edges.map((edge) => (
          <li key={edge.id}>
            <span className={`badge ${edge.status}`}>{edge.status}</span>
            {names.get(edge.from) || edge.from} → {names.get(edge.to) || edge.to}. {edge.detail}
          </li>
        ))}
      </ul>
    </div>
  );
}
