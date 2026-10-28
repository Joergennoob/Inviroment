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
  activity: { text: string; journalist?: string; sources: Source[] } | null;
  contributions: { date: string; amount: string; recipient: string; politician_card: string; filing_id: string }[];
};

type Roster = {
  retrieved: string;
  both_sides_count: number;
  both_sides_note: string;
  both_sides_journalist: string;
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
            Dette er folk som jobber for selskapene og prøver å påvirke lovene. Listen er fra 2025 og 2026. At et selskap har gitt penger, betyr ikke at en politiker stemte på en bestemt måte.
          </p>
          <p className="note">{roster.both_sides_note}</p>
          <details className="help">
            <summary>For journalister</summary>
            <p>{roster.both_sides_journalist}</p>
            <p>
              Registreringen ligger i statens rådatafil, tabellen som kobler firma og klient. Sesjonsbeløpet er det selskapet selv har oppgitt at de har brukt på påvirkning, ikke én persons lønn.
            </p>
          </details>
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

      <h3>{compact ? "Hvem som bruker mest penger på å påvirke" : "Hvem som bruker mest penger"}</h3>
      {spenders.length === 0 ? (
        <p>Vi har ikke tall for akkurat dette problemet i listen. Det betyr ikke at ingen prøver å påvirke. Vi har bare ikke lest et skjema som handler om det.</p>
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
                  Firma som er registrert for å jobbe for dem:{" "}
                  {hired.map((firm, index) => (
                    <span key={firm.filer_id}>
                      {index > 0 ? ", " : ""}
                      <CardLink id={firm.card_id} name={firm.name} />
                    </span>
                  ))}
                  .
                </div>
              ) : (
                <div>Vi fant ikke et eget firma utenfor selskapet. Se de ansatte lenger nede på lobbylisten.</div>
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
                <strong>Folk som jobber der. </strong>
                {firm.lobbyists.map((person) => person.name).join(", ")}.
              </p>
              <p>
                <strong>Hvem de jobber for. </strong>
                {firm.clients.map((client, index) => (
                  <span key={client.filer_id}>
                    {index > 0 ? ", " : ""}
                    <CardLink id={client.card_id} name={client.name} />
                  </span>
                ))}
                .
              </p>
              <p>
                <strong>Hvilke lover. </strong>
                {firm.bills_note}
              </p>
              <p>
                <strong>Penger. </strong>
                {firm.fee_text ||
                  "Vi har ikke lest hvor mye akkurat dette firmaet fikk betalt. Beløpet over er det selskapet brukte totalt, ikke firmaets del."}
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

          <h2>Ansatte som påvirker for sitt eget selskap</h2>
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
                  {employer?.activity ? (
                    <>
                      <p>{employer.activity.text}</p>
                      {employer.activity.journalist ? (
                        <details className="help">
                          <summary>For journalister</summary>
                          <p>{employer.activity.journalist}</p>
                        </details>
                      ) : null}
                    </>
                  ) : (
                    <p>Vi har ikke lest en liste over lover for dette selskapet.</p>
                  )}
                  {employer && employer.contributions.length > 0 ? (
                    <p>
                      Selskapet har oppgitt disse gavene til politikeres valgkamp:{" "}
                      {employer.contributions.map((row) => `${row.date}, ${row.amount} dollar, til ${row.recipient}`).join("; ")}.
                      Vi har ikke laget kort for mottakerne ennå, så navnene er ikke lenker.
                    </p>
                  ) : null}
                </section>
              );
            })}

          {problem === "" || problem === "ca-problem-oil-gas-proximity" || problem === "ca-problem-refineries" ? (
            <>
              <h2>Betalinger der navnet ikke matcher registeret</h2>
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
