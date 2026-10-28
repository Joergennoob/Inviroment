import Link from "next/link";
import { GLOSSARY } from "@/lib/words";

export default function GlossaryPage() {
  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/oversikt/">De ti problemene</Link>
      </p>
      <h1>Ord og forklaringer</h1>
      <p>
        Kartet bruker noen ord fra etatene i California. Her står de med vanlige ord. De nøyaktige navnene og tallene ligger fortsatt på kortene, under «For journalister».
      </p>
      <dl className="glossary">
        {GLOSSARY.map((entry) => (
          <div key={entry.word}>
            <dt>{entry.word}</dt>
            <dd>{entry.means}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
