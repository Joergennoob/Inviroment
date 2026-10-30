/** Camera and sidebar labels. The numbers repeat the problem cards. They are not new measurements. */

export type PanelTab = "hva" | "rammes" | "penger" | "politikere" | "filmer";

export const PROBLEM_LAYERS: Record<string, string[]> = {
  "ca-problem-south-coast-air": ["pm25", "ozone"],
  "ca-problem-san-joaquin-air": ["pm25", "valley-fever"],
  "ca-problem-drinking-water": ["failing-water"],
  "ca-problem-oil-gas-proximity": ["oil-zone", "wells", "schools"],
  "ca-problem-pesticides": ["pesticide"],
  "ca-problem-salton-sea": ["salton-line", "salton-ring"],
  "ca-problem-refineries": ["circles", "facilities"],
  "ca-problem-aliso-canyon": ["circles", "facilities"],
  "ca-problem-pfas": ["pfas"],
  "ca-problem-groundwater-overdraft": ["basins"],
};

export const PROBLEM_CAMERA: Record<string, { lng: number; lat: number; zoom: number }> = {
  "ca-problem-south-coast-air": { lng: -117.9, lat: 33.95, zoom: 7.2 },
  "ca-problem-san-joaquin-air": { lng: -119.8, lat: 36.5, zoom: 6.6 },
  "ca-problem-drinking-water": { lng: -119.6, lat: 36.6, zoom: 6.2 },
  "ca-problem-oil-gas-proximity": { lng: -119.4, lat: 35.3, zoom: 6.4 },
  "ca-problem-pesticides": { lng: -119.7, lat: 36.3, zoom: 6.6 },
  "ca-problem-salton-sea": { lng: -115.85, lat: 33.3, zoom: 8.2 },
  "ca-problem-refineries": { lng: -118.28, lat: 33.86, zoom: 8.6 },
  "ca-problem-aliso-canyon": { lng: -118.55, lat: 34.31, zoom: 11 },
  "ca-problem-pfas": { lng: -119.5, lat: 36.7, zoom: 6 },
  "ca-problem-groundwater-overdraft": { lng: -119.8, lat: 36.2, zoom: 6.4 },
};

/** Short line for the sidebar. Wording follows the first summary on each problem card. */
export const HEADLINE: Record<string, string> = {
  "ca-problem-south-coast-air": "16 millioner i området",
  "ca-problem-san-joaquin-air": "3,8 millioner i dalen",
  "ca-problem-drinking-water": "812 000 får utrygt vann",
  "ca-problem-oil-gas-proximity": "Om lag 3 millioner nær brønner",
  "ca-problem-pesticides": "181 millioner pund i 2022",
  "ca-problem-salton-sea": "Mye mindre vann til innsjøen",
  "ca-problem-refineries": "Luft skal måles ved gjerdet",
  "ca-problem-aliso-canyon": "Om lag 100 000 tonn metan",
  "ca-problem-pfas": "3 600 brønner testes",
  "ca-problem-groundwater-overdraft": "Om lag 4 millioner bor der",
};

/** Short place line already present in the plain title. Not a new location claim. */
export const PLACE: Record<string, string> = {
  "ca-problem-south-coast-air": "Rundt Los Angeles",
  "ca-problem-san-joaquin-air": "Jordbruksdalen",
  "ca-problem-drinking-water": "Vannverk i delstaten",
  "ca-problem-oil-gas-proximity": "Nær hus og skoler",
  "ca-problem-pesticides": "På jordene",
  "ca-problem-salton-sea": "Salton Sea",
  "ca-problem-refineries": "Tett på boliger",
  "ca-problem-aliso-canyon": "Gasslageret",
  "ca-problem-pfas": "Brønner som testes",
  "ca-problem-groundwater-overdraft": "Vann under bakken",
};

const RANK: Record<string, number> = {
  "ca-problem-south-coast-air": 1,
  "ca-problem-san-joaquin-air": 2,
  "ca-problem-drinking-water": 3,
  "ca-problem-oil-gas-proximity": 4,
  "ca-problem-pesticides": 5,
  "ca-problem-salton-sea": 6,
  "ca-problem-refineries": 7,
  "ca-problem-aliso-canyon": 8,
  "ca-problem-pfas": 9,
  "ca-problem-groundwater-overdraft": 10,
};

/** Yellow at rank 10, orange in the middle, dark red at rank 1. */
export function severityColor(rank: number): string {
  const clamped = Math.min(10, Math.max(1, rank));
  const t = (10 - clamped) / 9;
  const yellow = [253, 230, 138];
  const orange = [249, 115, 22];
  const dark = [127, 29, 29];
  const [a, b, u] = t < 0.5 ? [yellow, orange, t / 0.5] : [orange, dark, (t - 0.5) / 0.5];
  const mix = a.map((channel, index) => Math.round(channel + (b[index] - channel) * u));
  return `#${mix.map((channel) => channel.toString(16).padStart(2, "0")).join("")}`;
}

export function problemColor(id: string): string {
  return severityColor(RANK[id] ?? 5);
}

export const LAYER_RANK: Record<string, number> = {
  pm25: 1,
  ozone: 1,
  "valley-fever": 2,
  "failing-water": 3,
  "oil-zone": 4,
  wells: 4,
  schools: 4,
  pesticide: 5,
  "salton-line": 6,
  "salton-ring": 6,
  circles: 7,
  facilities: 7,
  pfas: 9,
  basins: 10,
};

export function layerColor(id: string): string {
  return id === "districts" ? "#6B7075" : severityColor(LAYER_RANK[id] ?? 5);
}

export function headlineParts(text: string): { figure: string; unit: string } {
  const approx = /^om lag\s+/i.test(text);
  const body = text.replace(/^om lag\s+/i, "");
  const match = body.match(/^(\d[\d\s.,]*)\s*(.*)$/);
  if (!match) return { figure: "–", unit: text };
  return { figure: `${approx ? "~" : ""}${match[1].trim()}`, unit: match[2] };
}

export function mapPoint(id: string): string {
  const camera = PROBLEM_CAMERA[id];
  if (!camera) return "";
  const lat = Math.abs(camera.lat).toFixed(2).replace(".", ",");
  const lng = Math.abs(camera.lng).toFixed(2).replace(".", ",");
  return `${lat}° N  ${lng}° V`;
}

export function youtubeId(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes("youtu.be")) return parsed.pathname.slice(1) || null;
    const id = parsed.searchParams.get("v");
    return id || null;
  } catch {
    return null;
  }
}

export function initials(name: string): string {
  const parts = name.split(/\s+/).filter((part) => part.length > 1 && part[0] === part[0].toUpperCase());
  const letters = (parts.length ? parts : name.split(/\s+/)).slice(0, 2).map((part) => part[0]);
  return letters.join("").toUpperCase();
}

export const STATUS_WORD: Record<string, string> = {
  confirmed: "bekreftet",
  indication: "indikasjon",
  not_found: "ikke funnet",
  not_verified: "ikke ferdig sjekket",
};

export function voteWord(vote?: string): string {
  if (vote === "yes") return "ja";
  if (vote === "no") return "nei";
  if (vote === "nvr") return "ikke stemt";
  return "";
}

export function dollars(amount?: string): string {
  if (!amount) return "";
  const value = Number(amount);
  if (!Number.isFinite(value)) return "";
  return `${new Intl.NumberFormat("nb-NO").format(value)} dollar`;
}
