"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import type { MapFocus } from "@/components/MapCanvas";
import MiniGraph from "@/components/MiniGraph";
import SourceChip from "@/components/SourceChip";
import { allCards } from "@/lib/cards";
import {
  dollars,
  HEADLINE,
  headlineParts,
  layerColor,
  mapPoint,
  PLACE,
  PROBLEM_CAMERA,
  PROBLEM_LAYERS,
  problemColor,
  STATUS_WORD,
  initials,
  voteWord,
  youtubeId,
  type PanelTab,
} from "@/lib/stage";
import type { Card, Claim, Source } from "@/lib/types";
import { TYPE_LABEL } from "@/lib/types";
import { LAYER_TITLE, officialName, plainTitle } from "@/lib/words";
import catalog from "@/data/media/catalog.json";
import edgesFile from "@/data/network/edges.json";
import nodesFile from "@/data/network/nodes.json";
import roster from "@/data/lobby/roster.json";

const MapView = dynamic(() => import("@/components/MapCanvas"), { ssr: false });

type NetSource = Source;
type NetNode = {
  id: string;
  name: string;
  type: string;
  card_id?: string;
  problems?: string[];
  detail?: string;
  firm_name?: string;
  sources?: NetSource[];
};
type NetEdge = {
  id: string;
  type: string;
  from: string;
  to: string;
  status: string;
  detail: string;
  amount_usd?: string;
  date?: string;
  vote?: string;
};

const TABS: { id: PanelTab; label: string }[] = [
  { id: "hva", label: "Hva skjer" },
  { id: "rammes", label: "Hvem rammes" },
  { id: "penger", label: "Hvem tjener penger" },
  { id: "politikere", label: "Politikere" },
  { id: "filmer", label: "Filmer" },
];

const KIND: Record<string, string> = {
  problem: "Sted",
  politician: "Person",
  lawmaker: "Person",
  organization: "Selskap",
  lobbying_firm: "Firma",
  lobbyist: "Lobbyist",
  bill: "Lov",
};

const nodes = nodesFile.nodes as NetNode[];
const edges = edgesFile.edges as NetEdge[];
const films = catalog.items as {
  id: string;
  title: string;
  maker: string;
  url: string;
  problems: string[];
  what_it_claims: string;
  affiliation: string;
}[];

function nodeById(id: string): NetNode | undefined {
  return nodes.find((node) => node.id === id);
}

function nodeForCard(cardId: string): NetNode | undefined {
  return nodes.find((node) => node.id === cardId || node.card_id === cardId);
}

function edgeCaption(edge: NetEdge): string {
  if (edge.type === "contributed_to") return dollars(edge.amount_usd);
  if (edge.type === "voted_on") return voteWord(edge.vote);
  return "";
}

function asClaim(id: string, text: string, status: Claim["status"], sources: Source[]): Claim {
  return { id, text, status, note: "", sources };
}

export default function InvestigateApp() {
  const cards = useMemo(() => allCards(), []);
  const byId = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);
  const problems = useMemo(
    () => cards.filter((card) => card.type === "problem").sort((a, b) => (a.rank ?? 99) - (b.rank ?? 99)),
    [cards],
  );
  const [problemId, setProblemId] = useState("");
  const [panel, setPanel] = useState<PanelTab>("hva");
  const [stack, setStack] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [layers, setLayers] = useState<{ id: string; title: string; kind: string }[]>([]);
  const [enabled, setEnabled] = useState<string[]>([]);
  const [focus, setFocus] = useState<MapFocus | null>(null);
  const [sheet, setSheet] = useState<"list" | "detail">("list");
  const [layersOpen, setLayersOpen] = useState(true);
  const [layersMobile, setLayersMobile] = useState(false);
  const [booted, setBooted] = useState(false);

  const flyTo = (id: string) => {
    const camera = PROBLEM_CAMERA[id];
    if (camera) setFocus({ ...camera, token: `${id}-${Date.now()}` });
    setEnabled(PROBLEM_LAYERS[id] ?? []);
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const problem = params.get("problem");
    const tab = params.get("panel");
    const kort = params.get("kort");
    const chosen = problem && byId.get(problem)?.type === "problem" ? problem : "";
    if (chosen) {
      setProblemId(chosen);
      setSheet("detail");
      const camera = PROBLEM_CAMERA[chosen];
      if (camera) setFocus({ ...camera, token: `start-${chosen}` });
    }
    if (tab && TABS.some((item) => item.id === tab)) setPanel(tab as PanelTab);
    if (kort && (byId.get(kort) || nodeById(kort))) setStack([kort]);
    void fetch("/data/layers/index.json")
      .then((response) => response.json())
      .then((index: { layers: { id: string; title: string; kind: string; default: boolean }[] }) => {
        setLayers(index.layers);
        const base = chosen && PROBLEM_LAYERS[chosen] ? PROBLEM_LAYERS[chosen] : [];
        const withDistricts = tab === "politikere" ? [...new Set([...base, "districts"])] : base;
        setEnabled(withDistricts);
      })
      .catch(() => setLayers([]));
    setBooted(true);
  }, [byId, problems]);

  useEffect(() => {
    if (!booted) return;
    const params = new URLSearchParams();
    if (sheet === "detail" && problemId) params.set("problem", problemId);
    if (sheet === "detail" && panel) params.set("panel", panel);
    if (stack[0]) params.set("kort", stack[0]);
    const next = params.toString() ? `/?${params.toString()}` : "/";
    window.history.replaceState(null, "", next);
  }, [booted, problemId, panel, stack, sheet]);

  const openProblem = (id: string) => {
    setProblemId(id);
    setStack([]);
    setPanel("hva");
    setSheet("detail");
    flyTo(id);
  };

  const openTarget = (id: string) => {
    const direct = byId.get(id);
    if (direct?.type === "problem") {
      openProblem(id);
      return;
    }
    if (direct) {
      setStack((current) => [id, ...current.filter((item) => item !== id)]);
      setSheet("detail");
      return;
    }
    const node = nodeById(id);
    if (node?.card_id && byId.get(node.card_id)) {
      openTarget(node.card_id);
      return;
    }
    if (node) {
      setStack((current) => [node.id, ...current.filter((item) => item !== node.id)]);
      setSheet("detail");
    }
  };

  const chooseTab = (tab: PanelTab) => {
    setPanel(tab);
    if (tab === "politikere") {
      setEnabled((current) => (current.includes("districts") ? current : [...current, "districts"]));
    }
  };

  const problem = byId.get(problemId);
  const top = stack[0];
  const activeCard = top ? byId.get(top) : undefined;
  const activeNode = top && !activeCard ? nodeById(top) : undefined;
  const summaries = useMemo(() => Object.fromEntries(cards.map((card) => [card.id, card.summary[0]?.text ?? ""])), [cards]);

  const hits = useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (needle.length < 2) return [];
    const fromCards = cards
      .filter((card) => {
        const blob = `${plainTitle(card)} ${card.name} ${card.summary.map((claim) => claim.text).join(" ")}`.toLowerCase();
        return blob.includes(needle);
      })
      .slice(0, 6)
      .map((card) => ({ id: card.id, title: plainTitle(card), kind: card.type === "problem" ? "Sted" : TYPE_LABEL[card.type] }));
    const seen = new Set(fromCards.map((hit) => hit.id));
    const fromNodes = nodes
      .filter((node) => !seen.has(node.id) && !(node.card_id && seen.has(node.card_id)) && node.name.toLowerCase().includes(needle))
      .slice(0, 4)
      .map((node) => ({ id: node.card_id && byId.get(node.card_id) ? node.card_id : node.id, title: node.name, kind: KIND[node.type] ?? "Treff" }));
    const fromFilms = films
      .filter((film) => film.title.toLowerCase().includes(needle))
      .slice(0, 2)
      .map((film) => ({ id: `film:${film.problems[0] ?? ""}`, title: film.title, kind: "Film" }));
    return [...fromCards, ...fromNodes, ...fromFilms].slice(0, 8);
  }, [byId, cards, query]);

  const crumbName = (id: string) => {
    const card = byId.get(id);
    if (card) return plainTitle(card);
    return nodeById(id)?.name ?? id;
  };

  const tally = `${problems.length} saker · ${cards.length} kort · ${cards.filter((card) => card.type === "lawmaker").length} politikere · ${roster.firms.length} lobbyfirma`;
  const showList = sheet === "list" && !activeCard && !activeNode;

  return (
    <div className={`inv ${layersOpen ? "" : "layers-shut"} ${layersMobile ? "layers-mobile" : ""} ${sheet === "detail" ? "sheet-detail" : "sheet-list"}`}>
      <header className="inv-top">
        <Link href="/" className="brand">
          <i />
          Miljøkart
        </Link>
        <div className="search">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Søk etter person, selskap, lov eller sted"
            aria-label="Søk"
          />
          {hits.length > 0 ? (
            <ul>
              {hits.map((hit) => (
                <li key={hit.id + hit.title}>
                  <button
                    type="button"
                    onClick={() => {
                      setQuery("");
                      if (hit.id.startsWith("film:")) {
                        const problemHit = hit.id.slice(5);
                        if (problemHit) {
                          openProblem(problemHit);
                          setPanel("filmer");
                        }
                        return;
                      }
                      openTarget(hit.id);
                    }}
                  >
                    <small>{hit.kind}</small>
                    {hit.title}
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
        <p className="counts mono">{tally}</p>
        <nav>
          <Link href="/lobbyister/" className="lobby-link">
            Lobbyister
          </Link>
          <Link href="/ord/" className="helpbtn" aria-label="Ord og forklaringer">
            ?
          </Link>
        </nav>
      </header>
      <aside className="desk-layers" aria-label="Kartlag">
        <div className="layer-head">
          <p className="kicker">Kartlag</p>
          <button type="button" className="iconbtn" aria-label={layersOpen ? "Skjul kartlag" : "Vis kartlag"} onClick={() => setLayersOpen((open) => !open)}>
            {layersOpen ? "‹" : "›"}
          </button>
        </div>
        {layers.map((layer) => {
          const point = layer.kind === "circle" || layer.kind === "cluster";
          return (
            <label key={layer.id} className="layer-row">
              <span className="switch">
                <input
                  type="checkbox"
                  checked={enabled.includes(layer.id)}
                  onChange={() =>
                    setEnabled((current) => (current.includes(layer.id) ? current.filter((id) => id !== layer.id) : [...current, layer.id]))
                  }
                />
                <i />
              </span>
              <span>{LAYER_TITLE[layer.id] ?? layer.title}</span>
              <span
                className={`minscale ${point || layer.kind === "choropleth" ? "heat" : layer.kind === "circle" ? "dot" : ""}`}
                style={point || layer.kind === "choropleth" || layer.id === "districts" ? undefined : { background: layerColor(layer.id) }}
              />
            </label>
          );
        })}
        <Link href="/lobbyister/" className="layer-foot">
          Lobbyister
        </Link>
      </aside>
      <div className="inv-map">
        <MapView enabled={enabled} summaries={summaries} focus={focus} onSelect={(cardId) => openTarget(cardId)} />
        <button type="button" className="lagbtn" onClick={() => setLayersMobile((open) => !open)}>
          Lag
        </button>
        <div className="legend" aria-hidden>
          <p className="kicker">Alvor</p>
          <div className="scale" />
          <div className="ticks mono">
            <span>10</span>
            <span>1</span>
          </div>
        </div>
      </div>
      <aside className="desk-rail" aria-label={showList ? "De ti problemene" : "Detaljer"}>
        <div className="sheet-handle" />
        {showList ? (
          <div className="rail-scroll">
            <div className="rail-head">
              <p className="kicker">Saker</p>
              <span className="mono note">{problems.length}</span>
            </div>
            {problems.map((card) => {
              const parts = headlineParts(HEADLINE[card.id] ?? "");
              return (
                <button key={card.id} type="button" className={`scard ${card.id === problemId ? "on" : ""}`} onClick={() => openProblem(card.id)}>
                  <Thumb id={card.id} />
                  <span>
                    <span className="meta mono">{String(card.rank ?? "").padStart(2, "0")} · {PLACE[card.id] ?? ""}</span>
                    <strong>{plainTitle(card)}</strong>
                    <span className="meta">{mapPoint(card.id)}</span>
                  </span>
                  <span className="figcol">
                    <span className="figure mono">{parts.figure}</span>
                    <span className="meta">{parts.unit}</span>
                    <i className={`dot ${card.summary[0]?.status ?? "not_verified"}`} title={STATUS_WORD[card.summary[0]?.status ?? "not_verified"]} />
                  </span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="rail-scroll">
            <div className="crumbs">
              <button type="button" onClick={() => { setStack([]); setSheet("list"); }}>
                Saker
              </button>
              {problem ? (
                <button type="button" onClick={() => setStack([])}>
                  {plainTitle(problem)}
                </button>
              ) : null}
              {stack
                .slice()
                .reverse()
                .map((id, index, all) =>
                  index === all.length - 1 ? (
                    <span key={id}>{crumbName(id)}</span>
                  ) : (
                    <button key={id} type="button" onClick={() => setStack((current) => current.slice(current.indexOf(id)))}>
                      {crumbName(id)}
                    </button>
                  ),
                )}
            </div>
            {activeCard ? (
              <EntityView card={activeCard} cards={byId} onOpen={openTarget} onBack={() => setStack((current) => current.slice(1))} />
            ) : activeNode ? (
              <NodeView node={activeNode} cards={byId} onOpen={openTarget} onBack={() => setStack((current) => current.slice(1))} />
            ) : problem ? (
              <ProblemView card={problem} cards={cards} tab={panel} onTab={chooseTab} onOpen={openTarget} />
            ) : (
              <p className="empty">Velg en sak i listen.</p>
            )}
          </div>
        )}
      </aside>
    </div>
  );
}

function Thumb({ id }: { id: string }) {
  const camera = PROBLEM_CAMERA[id];
  const x = camera ? ((camera.lng + 124.4) / 10.4) * 56 : 28;
  const y = camera ? ((42 - camera.lat) / 9.6) * 40 : 20;
  const color = problemColor(id);
  return (
    <svg className="thumb" viewBox="0 0 56 40" aria-hidden>
      <rect width="56" height="40" fill="#F4F4F2" />
      <circle cx={x} cy={y} r="9" fill={color} opacity="0.28" />
      <circle cx={x} cy={y} r="2.2" fill={color} />
    </svg>
  );
}

function ProblemView({
  card,
  cards,
  tab,
  onTab,
  onOpen,
}: {
  card: Card;
  cards: Card[];
  tab: PanelTab;
  onTab: (tab: PanelTab) => void;
  onOpen: (id: string) => void;
}) {
  const people = cards.filter((item) => item.type === "lawmaker" && item.links.some((link) => link.target_id === card.id));
  const companies = roster.employers.filter((employer) => employer.problems.includes(card.id));
  const firms = roster.firms.filter((firm) => firm.problems.includes(card.id));
  const relatedFilms = films.filter((film) => film.problems.includes(card.id));
  const parts = headlineParts(HEADLINE[card.id] ?? "");
  return (
    <div>
      <p className="kicker">Nummer {card.rank} av 10 · oppdatert {card.updated}</p>
      <h2>{plainTitle(card)}</h2>
      <p className="headline-num mono">{parts.figure}</p>
      <p className="note">{parts.unit}{mapPoint(card.id) ? ` · ${mapPoint(card.id)}` : ""}</p>
      <div className="tabs" role="tablist">
        {TABS.map((item) => (
          <button key={item.id} type="button" role="tab" aria-selected={tab === item.id} className={tab === item.id ? "on" : ""} onClick={() => onTab(item.id)}>
            {item.label}
          </button>
        ))}
      </div>
      {tab === "hva" ? (
        <div>
          {card.summary.map((claim) => (
            <p key={claim.id} className="lead">
              <i className={`dot ${claim.status}`} title={STATUS_WORD[claim.status]} />
              {claim.text} <SourceChip claim={claim} />
            </p>
          ))}
          <details className="tech">
            <summary>For journalister</summary>
            {officialName(card) ? <p>Offisielt navn: {officialName(card)}</p> : null}
            <p>Kort-id: {card.id}</p>
            {card.claims.slice(0, 4).map((claim) => (
              <p key={claim.id}>{claim.text}</p>
            ))}
          </details>
        </div>
      ) : null}
      {tab === "rammes" ? <WhoLives card={card} /> : null}
      {tab === "penger" ? (
        <div>
          {companies.length === 0 && firms.length === 0 ? <p className="empty">Vi har ikke et lobbybeløp koblet rett til dette problemet.</p> : null}
          {companies.length > 0 ? (
            <table className="desk-table">
              <thead>
                <tr>
                  <th>Selskap</th>
                  <th className="num">Dollar</th>
                </tr>
              </thead>
              <tbody>
                {companies.map((employer) => (
                  <tr key={employer.filer_id} onClick={() => onOpen(employer.card_id || employer.filer_id)}>
                    <td>
                      <strong>{employer.name}</strong>
                      <small className="empty">{employer.session_text}</small>
                    </td>
                    <td className="num mono">{new Intl.NumberFormat("nb-NO", { maximumFractionDigits: 0 }).format(employer.session_lobby_usd)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
          {firms.map((firm) => (
            <article key={firm.filer_id} className="firmblock">
              <button type="button" className="rowbtn" onClick={() => onOpen(firm.card_id || `firm-${firm.filer_id}`)}>
                <strong>{firm.name}</strong>
                <span>{firm.fee_text || "Firma som er registrert for å påvirke politikere."}</span>
              </button>
              <div className="chiprow">
                {firm.lobbyists.slice(0, 4).map((person) => (
                  <button key={person.id} type="button" className="textbtn" onClick={() => onOpen(`lobbyist-${person.id}`)}>
                    {person.name}
                  </button>
                ))}
              </div>
            </article>
          ))}
          <p>
            <Link href={`/lobbyister/#${card.id}`}>Hele listen over folk som påvirker</Link>
          </p>
        </div>
      ) : null}
      {tab === "politikere" ? (
        <div>
          {people.length === 0 ? <p className="empty">Ingen politiker i kortene er koblet rett til dette problemet ennå.</p> : (
            <table className="desk-table">
              <thead>
                <tr>
                  <th>Person</th>
                  <th>Stemme</th>
                  <th className="num">Penger</th>
                </tr>
              </thead>
              <tbody>
                {people.map((person) => (
                  <PoliticianRow key={person.id} person={person} problemId={card.id} onOpen={onOpen} />
                ))}
              </tbody>
            </table>
          )}
        </div>
      ) : null}
      {tab === "filmer" ? (
        <div>
          {relatedFilms.length === 0 ? <p className="empty">Vi har ikke en bekreftet film for dette problemet ennå.</p> : null}
          {relatedFilms.map((film) => {
            const video = youtubeId(film.url);
            return (
              <article key={film.id} className="film">
                {video ? <img src={`https://i.ytimg.com/vi/${video}/hqdefault.jpg`} alt="" /> : null}
                <h3>{film.title}</h3>
                <p className="note">
                  {film.maker}. {film.affiliation}
                </p>
                <p>{film.what_it_claims}</p>
                {video ? (
                  <iframe title={film.title} src={`https://www.youtube-nocookie.com/embed/${video}`} allowFullScreen />
                ) : (
                  <p>
                    <a href={film.url}>Åpne filmen</a>
                  </p>
                )}
              </article>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

function percentIn(text: string): number | null {
  const match = text.match(/(\d{1,2}(?:[.,]\d+)?)\s*%|(\d{1,2}(?:[.,]\d+)?)\s*prosent/);
  if (!match) return null;
  const value = Number((match[1] ?? match[2]).replace(",", "."));
  if (!Number.isFinite(value) || value > 100) return null;
  return value;
}

function WhoLives({ card }: { card: Card }) {
  const blocks = [
    ["Hvor mange", card.population],
    ["Inntekt og skole", card.demographics],
    ["Helse", card.health_outcomes],
  ] as const;
  const any = blocks.some(([, block]) => block && block.claims.length);
  if (!any) return <p>Kortet har ikke tall for innbyggere, inntekt eller sykdom.</p>;
  return (
    <div>
      <div className="tiles">
        {blocks.map(([title, block]) =>
          block?.claims.slice(0, 2).map((claim) => {
            const share = percentIn(claim.text);
            return (
              <article key={title + claim.id}>
                <small>
                  <i className={`dot ${claim.status}`} title={STATUS_WORD[claim.status]} /> {title}
                </small>
                <p>{claim.text}</p>
                {share != null ? (
                  <span className="bar" aria-hidden>
                    <span style={{ width: `${share}%` }} />
                  </span>
                ) : null}
                <SourceChip claim={claim} />
              </article>
            );
          }),
        )}
      </div>
      <details className="tech">
        <summary>For journalister</summary>
        {blocks.map(([title, block]) =>
          block ? (
            <p key={title}>
              {title}: {block.geography} {block.vintage} {block.comparison}
            </p>
          ) : null,
        )}
      </details>
    </div>
  );
}

function PoliticianRow({ person, problemId, onOpen }: { person: Card; problemId: string; onOpen: (id: string) => void }) {
  const billIds = new Set(edges.filter((edge) => edge.type === "relates_to" && edge.to === problemId).map((edge) => edge.from));
  const votes = edges.filter((edge) => edge.type === "voted_on" && edge.from === person.id && billIds.has(edge.to));
  const said = edges.filter((edge) => edge.type === "stated" && edge.from === person.id && (edge.to === problemId || billIds.has(edge.to)));
  const money = edges.filter((edge) => edge.type === "contributed_to" && edge.to === person.id);
  let badge = "Sier vs. stemmer · ikke i listen";
  if (votes.length && said.length) badge = "Sier vs. stemmer";
  else if (votes.length) badge = "Sier vs. stemmer · bare stemme";
  else if (said.length) badge = "Sier vs. stemmer · bare uttalelse";
  const vote = votes[0]?.vote;
  const voteLabel = vote === "yes" ? "Ja" : vote === "no" ? "Nei" : vote === "nvr" ? "Ikke stemt" : "Ikke i listen";
  const voteClass = vote === "yes" ? "yes" : vote === "no" ? "no" : "muted";
  const gift = money[0] ? dollars(money[0].amount_usd) : "–";
  return (
    <tr onClick={() => onOpen(person.id)}>
      <td>
        <span className="who">
          <span className="avatar">{initials(person.name)}</span>
          <span>
            <strong>{person.name}</strong>
            <small className="clamp">{person.summary[0]?.text}</small>
            <b className="chip">{badge}</b>
          </span>
        </span>
      </td>
      <td>
        <span className={`chip ${voteClass}`}>{voteLabel}</span>
      </td>
      <td className="num mono">{gift}</td>
    </tr>
  );
}

const EDGE_RANK: Record<string, number> = {
  contributed_to: 0,
  voted_on: 1,
  stated: 2,
  represents: 3,
  lobbied_on: 4,
  relates_to: 5,
  employed_by: 6,
  firm_roster: 7,
};

function graphFor(nodeId: string, label: string, kind: string, cards: Map<string, Card>) {
  const near = edges
    .filter((edge) => edge.from === nodeId || edge.to === nodeId)
    .sort((a, b) => (EDGE_RANK[a.type] ?? 9) - (EDGE_RANK[b.type] ?? 9))
    .slice(0, 10);
  const graphNodes = new Map<string, { id: string; name: string; type: string }>();
  graphNodes.set(nodeId, { id: nodeId, name: label, type: kind });
  for (const edge of near) {
    for (const id of [edge.from, edge.to]) {
      if (graphNodes.has(id)) continue;
      const known = nodeById(id);
      const linked = known?.card_id ? cards.get(known.card_id) : cards.get(id);
      graphNodes.set(id, {
        id,
        name: linked ? plainTitle(linked) : known?.name ?? id,
        type: known?.type ?? (linked?.type === "lawmaker" ? "politician" : linked?.type) ?? "organization",
      });
    }
  }
  return {
    near,
    nodes: [...graphNodes.values()],
    edges: near.map((edge) => ({ id: edge.id, from: edge.from, to: edge.to, label: edgeCaption(edge) })),
  };
}

function EntityView({
  card,
  cards,
  onOpen,
  onBack,
}: {
  card: Card;
  cards: Map<string, Card>;
  onOpen: (id: string) => void;
  onBack: () => void;
}) {
  const node = nodeForCard(card.id);
  const nodeId = node?.id ?? card.id;
  const graph = graphFor(nodeId, plainTitle(card), card.type === "lawmaker" ? "politician" : card.type, cards);
  return (
    <div>
      <button type="button" className="back" onClick={onBack}>
        Tilbake
      </button>
      <p className="kicker">{TYPE_LABEL[card.type]}</p>
      <h2>{plainTitle(card)}</h2>
      {card.type === "lawmaker" ? <span className="avatar lg">{initials(card.name)}</span> : null}
      {card.summary.map((claim) => (
        <p key={claim.id} className="lead">
          <i className={`dot ${claim.status}`} title={STATUS_WORD[claim.status]} />
          {claim.text} <SourceChip claim={claim} />
        </p>
      ))}
      <h3>Koblinger</h3>
      <MiniGraph nodes={graph.nodes} edges={graph.edges} activeId={nodeId} onPick={onOpen} />
      <ul className="plain">
        {card.links.map((link) => {
          const target = cards.get(link.target_id);
          return (
            <li key={link.target_id}>
              <button type="button" className="textbtn" onClick={() => onOpen(link.target_id)}>
                {target ? plainTitle(target) : link.target_id}
              </button>
              . {link.text}
            </li>
          );
        })}
      </ul>
      <details className="tech">
        <summary>For journalister</summary>
        <p>Kort-id: {card.id}</p>
        {card.claims.slice(0, 3).map((claim) => (
          <p key={claim.id}>{claim.text}</p>
        ))}
      </details>
    </div>
  );
}

function NodeView({
  node,
  cards,
  onOpen,
  onBack,
}: {
  node: NetNode;
  cards: Map<string, Card>;
  onOpen: (id: string) => void;
  onBack: () => void;
}) {
  const graph = graphFor(node.id, node.name, node.type, cards);
  const plain =
    node.type === "lobbyist"
      ? `${node.name} står i registeret som lobbyist${node.firm_name ? ` hos ${node.firm_name}` : ""}. Kundene under er firmaets liste, ikke en saksliste for personen.`
      : `${node.name} står i registeret over folk og firmaer som påvirker politikerne i California.`;
  const status = (node.sources?.[0] ? "confirmed" : "not_verified") as Claim["status"];
  const claim = asClaim(node.id, plain, status, node.sources ?? []);
  return (
    <div>
      <button type="button" className="back" onClick={onBack}>
        Tilbake
      </button>
      <p className="kicker">{KIND[node.type] ?? "Oppføring"}</p>
      <h2>{node.name}</h2>
      {node.type === "lobbyist" || node.type === "politician" ? <span className="avatar lg">{initials(node.name)}</span> : null}
      <p className="lead">
        <i className={`dot ${status}`} title={STATUS_WORD[status]} />
        {plain} {node.sources && node.sources.length > 0 ? <SourceChip claim={claim} /> : null}
      </p>
      <h3>Koblinger</h3>
      <MiniGraph nodes={graph.nodes} edges={graph.edges} activeId={node.id} onPick={onOpen} />
      <details className="tech">
        <summary>For journalister</summary>
        <p>Node-id: {node.id}</p>
        {node.detail ? <p>{node.detail}</p> : null}
      </details>
    </div>
  );
}
