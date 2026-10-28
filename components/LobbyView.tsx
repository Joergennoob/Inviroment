"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Source = {
  url: string;
  title: string;
  publisher: string;
  retrieved: string;
  archive_url: string;
  archive_note: string;
};

type Client = {
  filer_id: string;
  name: string;
  card_id: string;
  problems: string[];
};

type Firm = {
  filer_id: string;
  name: string;
  card_id: string;
  problems: string[];
  lobbyists: { id: string; name: string }[];
  clients: Client[];
  fee_text: string;
  fee_sources: Source[];
  both_sides: boolean;
  bills_note: string;
};

type Employer = {
  filer_id: string;
  name: string;
  card_id: string;
  problems: string[];
  session_lobby_usd: number;
  session_text: string;
  sources: Source[];
  activity: { text: string; sources: Source[] } | null;
  contributions: { date: string; amount: string; recipient: string; politician_card: string; filing_id: string }[];
};

type Roster = {
  retrieved: string;
  both_sides_count: number;
  both_sides_note: string;
  registration_source: Source;
  problems: { id: string; title: string }[];
  employers: Employer[];
  inhouse: { filer_id: string; people: { id: string; name: string }[]; card_id: string }[];
  firms: Firm[];
  unmatched_payments: { payee: string; text: string; card_id: string; note: string }[];
};

function SourceLine({ source }: { source: Source }) {
  return (
    <li>
      <a href={source.url}>{source.title}</a> ({source.publisher}, hentet {source.retrieved})
      {source.archive_url ? (
        <>
          {" "}
          · <a href={source.archive_url}>Arkiv</a>
        </>
      ) : (
        <> · {source.archive_note}</>
      )}
    </li>
  );
}

function CardLink({ id, name }: { id: string; name: string }) {
  if (!id) return <span>{name}</span>;
  return <Link href={`/kort/${id}/`}>{name}</Link>;
}

export default function LobbyView({
  roster,
  initialProblem = "",
  compact = false,
}: {
  roster: Roster;
  initialProblem?: string;
  compact?: boolean;
}) {
  const [problem, setProblem] = useState(initialProblem);

  useEffect(() => {
    if (compact) return;
    const hash = window.location.hash.replace("#", "");
    if (hash) setProblem(hash);
  }, [compact]);

  const firms = useMemo(
    () => roster.firms.filter((firm) => !problem || firm.problems.includes(problem)),
    [roster.firms, problem],
  );
  const employers = useMemo(() => {
    return roster.employers
      .filter((employer) => !problem || employer.problems.includes(problem))
      .sort((a, b) => b.session_lobby_usd - a.session_lobby_usd);
  }, [roster.employers, problem]);

  const spenders = compact ? employers.slice(0, 5) : employers;

  return (
    <div>
      {compact ? (
        <h2>Lobby og penger</h2>
      ) : (
        <>
          <p className="note">
            Registreringer i sesjonen 2025–2026. Et bidrag eller et honorar er det skjemaet fører. Det sier ikke at pengene endret en stemme.
          </p>
          <p className="note">{roster.both_sides_note}</p>
        </>
      )}
      {compact ? null : (
        <div className="filters">
          <button type="button" className={problem === "" ? "on" : ""} onClick={() => setProblem("")}>
            Alle
          </button>
          {roster.problems.map((item) => (
            <button
              key={item.id}
              type="button"
              className={problem === item.id ? "on" : ""}
              onClick={() => setProblem(item.id)}
            >
              {item.title}
            </button>
          ))}
        </div>
      )}

      <h3>{compact ? "Største lobbybudsjett på dette problemet" : "Hvem som betaler mest"}</h3>
      {spenders.length === 0 ? (
        <p>Ingen oppdragsgiver i dette uttrekket er koblet til problemet. PFAS og drikkevann har ikke en egen lobbyfil i listen.</p>
      ) : null}
      <ul className="plain">
        {spenders.map((employer) => {
          const hired = roster.firms.filter((firm) => firm.clients.some((client) => client.filer_id === employer.filer_id));
          return (
            <li key={employer.filer_id}>
              <CardLink id={employer.card_id} name={employer.name} />
              {". "}
              {employer.session_text}
              {hired.length > 0 ? (
                <div>
                  Firma registrert for dem:{" "}
                  {hired.map((firm, index) => (
                    <span key={firm.filer_id}>
                      {index > 0 ? ", " : ""}
                      <CardLink id={firm.card_id} name={firm.name} />
                    </span>
                  ))}
                  .
                </div>
              ) : (
                <div>Ingen eksternt firma i dette uttrekket. Se interne lobbyister under.</div>
              )}
            </li>
          );
        })}
      </ul>
      {compact ? (
        <p>
          <Link href={`/lobbyister/#${initialProblem}`}>Hele lobbylisten</Link>
        </p>
      ) : null}

      {compact ? null : (
        <>
          <h2>Firma</h2>
          {firms.map((firm) => (
            <section key={firm.filer_id} className="lobby-block">
              <h3>
                <CardLink id={firm.card_id} name={firm.name} />
                {firm.both_sides ? <span className="badge indication"> Jobber for begge sider</span> : null}
              </h3>
              <p>
                <strong>Lobbyister. </strong>
                {firm.lobbyists.map((person) => person.name).join(", ")}.
              </p>
              <p>
                <strong>Klienter i sesjon 2025. </strong>
                {firm.clients.map((client, index) => (
                  <span key={client.filer_id}>
                    {index > 0 ? ", " : ""}
                    <CardLink id={client.card_id} name={client.name} />
                  </span>
                ))}
                .
              </p>
              <p>
                <strong>Saker. </strong>
                {firm.bills_note}
              </p>
              <p>
                <strong>Penger. </strong>
                {firm.fee_text ||
                  "Kvartalsbeløpet til dette firmanavnet er ikke hentet ut. Sesjonsbeløpet står på klienten over, og er ikke firmaets andel."}
              </p>
              {firm.fee_sources.length > 0 ? (
                <ul className="sources">
                  {firm.fee_sources.map((source) => (
                    <SourceLine key={source.url} source={source} />
                  ))}
                </ul>
              ) : null}
            </section>
          ))}

          <h2>Interne lobbyister</h2>
          {roster.inhouse
            .filter((group) => {
              const employer = roster.employers.find((item) => item.filer_id === group.filer_id);
              return !problem || employer?.problems.includes(problem);
            })
            .map((group) => {
              const employer = roster.employers.find((item) => item.filer_id === group.filer_id);
              return (
                <section key={group.filer_id} className="lobby-block">
                  <h3>
                    <CardLink id={group.card_id} name={employer?.name || group.filer_id} />
                  </h3>
                  <p>{group.people.map((person) => person.name).join(", ")}.</p>
                  {employer?.activity ? <p>{employer.activity.text}</p> : <p>Ingen lovliste er lest for denne oppdragsgiveren.</p>}
                  {employer && employer.contributions.length > 0 ? (
                    <p>
                      Bidrag ført på skjema 635:{" "}
                      {employer.contributions.map((row) => `${row.date} ${row.amount} dollar til ${row.recipient}`).join("; ")}.
                      Kort for mottakeren er ikke skrevet ennå, så navnet er ikke lenket.
                    </p>
                  ) : null}
                </section>
              );
            })}

          {problem === "" || problem === "ca-problem-oil-gas-proximity" || problem === "ca-problem-refineries" ? (
            <>
              <h2>Betalinger med et annet firmanavn</h2>
              <ul className="plain">
                {roster.unmatched_payments.map((row) => (
                  <li key={row.payee}>
                    <CardLink id={row.card_id} name={row.payee} />. {row.text} {row.note}
                  </li>
                ))}
              </ul>
            </>
          ) : null}
          <p className="note">
            Kilde for registreringene:{" "}
            <a href={roster.registration_source.url}>{roster.registration_source.title}</a>. Hentet {roster.retrieved}.
          </p>
        </>
      )}
    </div>
  );
}
