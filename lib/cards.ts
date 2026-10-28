import bundle from "../data/site/cards.json";
import type { Bundle, Card } from "./types";

const data = bundle as Bundle;

export function allCards(): Card[] {
  return data.cards;
}

export function cardById(id: string): Card | undefined {
  return data.cards.find((card) => card.id === id);
}

export function problems(): Card[] {
  return data.cards
    .filter((card) => card.type === "problem")
    .sort((a, b) => (a.rank ?? 99) - (b.rank ?? 99));
}
