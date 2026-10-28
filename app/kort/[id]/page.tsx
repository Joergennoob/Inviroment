import Link from "next/link";
import { notFound } from "next/navigation";
import CardBody from "@/components/ClaimList";
import { allCards, cardById } from "@/lib/cards";
import { TYPE_LABEL } from "@/lib/types";

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
        <Link href="/oversikt/">Rangering</Link>
        {" · "}
        <Link href="/lobbyister/">Lobbyister</Link>
      </p>
      <p className="note">{TYPE_LABEL[card.type]}</p>
      <h1>{card.name}</h1>
      <CardBody card={card} cardsById={byId} />
    </div>
  );
}
