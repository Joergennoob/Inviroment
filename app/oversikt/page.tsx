import Link from "next/link";
import { problems } from "@/lib/cards";
import { plainTitle } from "@/lib/words";

export default function OverviewPage() {
  const ranked = problems();
  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/ord/">Ord og forklaringer</Link>
        {" · "}
        <Link href="/lobbyister/">Lobbyister</Link>
      </p>
      <h1>Ti problemer i California</h1>
      <p>
        De med flest mennesker står øverst. Vi bruker tallet fra den etaten som har ansvaret, når de har telt folk. Klikk et problem for å lese det med vanlige ord.
      </p>
      <details className="tech">
        <summary>For journalister: tekniske detaljer</summary>
        <p>Hele begrunnelsen for rekkefølgen står i data/ca/oversikt.md.</p>
      </details>
      <ol>
        {ranked.map((card) => (
          <li key={card.id}>
            <Link href={`/kort/${card.id}/`}>{plainTitle(card)}</Link>
            <p>{card.summary[0]?.text}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
