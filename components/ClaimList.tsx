import Link from "next/link";
import type { Card, Claim } from "@/lib/types";
import { STATUS_LABEL } from "@/lib/types";

function ClaimBlock({ claim }: { claim: Claim }) {
  return (
    <div className="claim">
      <p>
        <span className={`badge ${claim.status}`}>{STATUS_LABEL[claim.status]}</span>
        {claim.text}
      </p>
      {claim.note ? <p className="note">{claim.note}</p> : null}
      <ul className="sources">
        {claim.sources.map((source) => (
          <li key={source.url + source.title}>
            <a href={source.url}>{source.title}</a>
            {" "}
            ({source.publisher}, hentet {source.retrieved})
            {source.archive_url ? (
              <>
                {" "}
                · <a href={source.archive_url}>Arkiv</a>
              </>
            ) : (
              <> · {source.archive_note}</>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function CardBody({ card, cardsById }: { card: Card; cardsById: Map<string, Card> }) {
  return (
    <article>
      <p className="note">Oppdatert {card.updated}</p>
      <h2>I korte trekk</h2>
      {card.summary.map((claim) => (
        <ClaimBlock key={claim.id} claim={claim} />
      ))}
      <h2>Detaljer med kilder</h2>
      {card.claims.map((claim) => (
        <ClaimBlock key={claim.id} claim={claim} />
      ))}
      {(["population", "demographics", "health_outcomes"] as const).map((key) => {
        const block = card[key];
        if (!block) return null;
        const title = key === "population" ? "Befolkning" : key === "demographics" ? "Demografi" : "Helseutfall";
        return (
          <section key={key}>
            <h2>{title}</h2>
            <p className="note">
              {block.geography}. {block.vintage}. Sammenligning: {block.comparison}.
            </p>
            {block.claims.map((claim) => (
              <ClaimBlock key={claim.id} claim={claim} />
            ))}
          </section>
        );
      })}
      {card.geometry ? (
        <div className="place">
          <strong>Kilde for plassering. </strong>
          {card.geometry.note} {card.geometry.source_name}, post {card.geometry.source_record_id}.{" "}
          <a href={card.geometry.source_url}>Kildelenke</a>. Hentet {card.geometry.retrieved}.
        </div>
      ) : null}
      {card.links.length > 0 ? (
        <>
          <h2>Videre</h2>
          <ul className="plain">
            {card.links.map((link) => {
              const target = cardsById.get(link.target_id);
              return (
                <li key={link.target_id + link.text}>
                  <Link href={`/kort/${link.target_id}/`}>{target?.name ?? link.target_id}</Link>
                  {". "}
                  {link.text}
                </li>
              );
            })}
          </ul>
        </>
      ) : null}
      {card.checked_empty.length > 0 ? (
        <>
          <h2>Sjekket uten funn</h2>
          <ul className="plain">
            {card.checked_empty.map((item) => (
              <li key={item.field}>
                <span className={`badge ${item.result}`}>
                  {item.result === "not_found" ? "Ikke funnet" : "Ikke verifisert"}
                </span>
                {item.searched}
              </li>
            ))}
          </ul>
        </>
      ) : null}
      {card.open_questions.length > 0 ? (
        <>
          <h2>Åpne spørsmål</h2>
          <ul className="plain">
            {card.open_questions.map((question) => (
              <li key={question}>{question}</li>
            ))}
          </ul>
        </>
      ) : null}
    </article>
  );
}
