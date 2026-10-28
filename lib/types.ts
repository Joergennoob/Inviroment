export type Status = "confirmed" | "indication" | "not_found" | "not_verified";

export type Source = {
  url: string;
  title: string;
  publisher: string;
  retrieved: string;
  archive_url: string;
  archive_note: string;
};

export type Claim = {
  id: string;
  text: string;
  status: Status;
  note: string;
  sources: Source[];
};

export type Geometry = {
  type: "Point" | "Polygon" | "MultiPolygon";
  coordinates: number[] | number[][] | number[][][] | number[][][][];
  source_name: string;
  source_record_id: string;
  source_url: string;
  retrieved: string;
  note: string;
};

export type Card = {
  schema_version: string;
  id: string;
  type: "problem" | "organization" | "lobbying_firm" | "lawmaker" | "bill";
  name: string;
  state: "CA";
  updated: string;
  rank: number | null;
  org_kind: string | null;
  summary: Claim[];
  claims: Claim[];
  links: { rel: string; target_id: string; text: string }[];
  geometry: Geometry | null;
  map_features: { layer: string; name: string; geometry: Geometry }[];
  checked_empty: {
    field: string;
    searched: string;
    result: "not_found" | "not_verified";
    urls: string[];
    retrieved: string;
  }[];
  open_questions: string[];
  population?: AreaBlock;
  demographics?: AreaBlock;
  health_outcomes?: AreaBlock;
};

export type AreaBlock = {
  geography: string;
  vintage: string;
  comparison: string;
  claims: Claim[];
};

export type Bundle = { cards: Card[] };

export const STATUS_LABEL: Record<Status, string> = {
  confirmed: "I dokumentet",
  indication: "Bare et hint",
  not_found: "Fant ikke",
  not_verified: "Ikke ferdig sjekket",
};

export const TYPE_LABEL: Record<Card["type"], string> = {
  problem: "Et problem",
  organization: "Selskap eller etat",
  lobbying_firm: "Firma som påvirker politikere",
  lawmaker: "Politiker",
  bill: "En lov",
};
