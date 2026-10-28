import Link from "next/link";
import { notFound } from "next/navigation";
import CardBody from "@/components/ClaimList";
import { allCards, cardById } from "@/lib/cards";
import { TYPE_LABEL } from "@/lib/types";
import { officialName, plainTitle } from "@/lib/words";

export function generateStaticParams() {
  return allCards().map((card) => ({ id: card.id }));
}

export default async function CardPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const card = cardById(id);
  if (!card) notFound();
  const byId = new Map(allCards().map((item) => [item.id, item]));
  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/oversikt/">De ti problemene</Link>
        {" · "}
        <Link href="/ord/">Ord og forklaringer</Link>
        {" · "}
        <Link href="/lobbyister/">Lobbyister</Link>
      </p>
      <p className="note">{TYPE_LABEL[card.type]}</p>
      <h1>{plainTitle(card)}</h1>
      {officialName(card) ? (
        <details className="tech">
          <summary>For journalister: tekniske detaljer</summary>
          <p>Offisielt navn: {officialName(card)}</p>
        </details>
      ) : null}
      <CardBody card={card} cardsById={byId} />
    </div>
  );
}
