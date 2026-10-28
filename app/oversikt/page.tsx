import Link from "next/link";
import { problems } from "@/lib/cards";

export default function OverviewPage() {
  const ranked = problems();
  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/lobbyister/">Lobbyister</Link>
      </p>
      <h1>Ti miljøproblemer i California</h1>
      <p>
        Rangeringen er redaksjonell. Den følger befolkning under en brutt standard først, og bruker
        etatens eget omfangstall når folketallet mangler. Hele begrunnelsen står i data/ca/oversikt.md.
      </p>
      <ol>
        {ranked.map((card) => (
          <li key={card.id}>
            <Link href={`/kort/${card.id}/`}>{card.name}</Link>
            <p>{card.summary[0]?.text}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
