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

export const STRIPE: Record<string, string> = {
  "ca-problem-south-coast-air": "#c45c26",
  "ca-problem-san-joaquin-air": "#a36b12",
  "ca-problem-drinking-water": "#1d4e89",
  "ca-problem-oil-gas-proximity": "#1f4d3a",
  "ca-problem-pesticides": "#6b3f69",
  "ca-problem-salton-sea": "#1a6b7a",
  "ca-problem-refineries": "#9a4318",
  "ca-problem-aliso-canyon": "#6b4a32",
  "ca-problem-pfas": "#5c3d8a",
  "ca-problem-groundwater-overdraft": "#3d6b8a",
};

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
