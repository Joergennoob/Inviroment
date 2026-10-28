import Link from "next/link";
import LobbyView from "@/components/LobbyView";
import PlaceNote from "@/components/PlaceNote";
import roster from "@/data/lobby/roster.json";
import type { Card, Claim } from "@/lib/types";
import { STATUS_LABEL } from "@/lib/types";
import { plainTitle } from "@/lib/words";

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
      <p className="note">Sist lest {card.updated}</p>
      <h2>Kort forklart</h2>
      {card.summary.map((claim) => (
        <ClaimBlock key={claim.id} claim={claim} />
      ))}
      <h2>Tall og kilder</h2>
      <p className="note">Her står de nøyaktige tallene, slik de står i dokumentene. Ordene kan være vanskelige. De er med fordi vi ikke endrer kilden.</p>
      {card.claims.map((claim) => (
        <ClaimBlock key={claim.id} claim={claim} />
      ))}
      {(["population", "demographics", "health_outcomes"] as const).map((key) => {
        const block = card[key];
        if (!block) return null;
        const title = key === "population" ? "Hvor mange som bor her" : key === "demographics" ? "Hvem som bor her" : "Sykdom";
        const intro =
          key === "population"
            ? "Hvor mange mennesker kildene knytter til området."
            : key === "demographics"
              ? "Hvem som bor der, sammenlignet med resten av California. Tallene sier ikke at miljøet er grunnen."
              : "Sykdomstall for området. Vi vet ikke om miljøet er grunnen.";
        return (
          <section key={key}>
            <h2>{title}</h2>
            <p>{intro}</p>
            <details className="tech">
              <summary>For journalister: tekniske detaljer</summary>
              <p>
                {block.geography}. {block.vintage}. Sammenligning: {block.comparison}.
              </p>
            </details>
            {block.claims.map((claim) => (
              <ClaimBlock key={claim.id} claim={claim} />
            ))}
          </section>
        );
      })}
      {card.geometry ? (
        <PlaceNote
          featureName={card.name}
          sourceName={card.geometry.source_name}
          recordId={card.geometry.source_record_id}
          sourceUrl={card.geometry.source_url}
          retrieved={card.geometry.retrieved}
          note={card.geometry.note}
        />
      ) : null}
      {card.type === "problem" ? <LobbyView roster={roster} initialProblem={card.id} compact /> : null}
      {card.links.length > 0 ? (
        <>
          <h2>Les mer om</h2>
          <ul className="plain">
            {card.links.map((link) => {
              const target = cardsById.get(link.target_id);
              return (
                <li key={link.target_id + link.text}>
                  <Link href={`/kort/${link.target_id}/`}>{target ? plainTitle(target) : link.target_id}</Link>
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
          <h2>Vi lette, men fant det ikke</h2>
          <ul className="plain">
            {card.checked_empty.map((item) => (
              <li key={item.field}>
                <span className={`badge ${item.result}`}>
                  {item.result === "not_found" ? "Fant ikke" : "Ikke ferdig sjekket"}
                </span>
                {item.searched}
              </li>
            ))}
          </ul>
        </>
      ) : null}
      {card.open_questions.length > 0 ? (
        <>
          <h2>Det vi fortsatt ikke vet</h2>
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
