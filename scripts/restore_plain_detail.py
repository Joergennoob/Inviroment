#!/usr/bin/env python3
"""Keep exact sourced sentences under the plain summaries, and align summary text with its sources."""

from __future__ import annotations

import json
import subprocess
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"


def load(cid: str) -> dict:
    return json.loads((CARDS / f"{cid}.json").read_text(encoding="utf-8"))


def save(card: dict) -> None:
    (CARDS / f"{card['id']}.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def all_items(card: dict) -> list[dict]:
    found = list(card["summary"]) + list(card["claims"])
    for name in ("population", "demographics", "health_outcomes"):
        block = card.get(name)
        if block:
            found.extend(block.get("claims") or [])
    return found


def restore_exact_summaries() -> int:
    added = 0
    for path in sorted(CARDS.glob("*.json")):
        card = json.loads(path.read_text(encoding="utf-8"))
        old = json.loads(
            subprocess.check_output(["git", "show", f"HEAD:data/cards/{path.name}"], cwd=ROOT)
        )
        texts = {item["text"] for item in all_items(card)}
        ids = {item["id"] for item in all_items(card)}
        for item in old["summary"]:
            if item["text"] in texts:
                continue
            clone = deepcopy(item)
            if clone["id"] in ids:
                clone["id"] = f"kept-{clone['id']}"
            while clone["id"] in ids:
                clone["id"] += "-2"
            card["claims"].append(clone)
            ids.add(clone["id"])
            texts.add(clone["text"])
            added += 1
        save(card)
    return added


def set_texts(cid: str, texts: list[str]) -> None:
    card = load(cid)
    if len(texts) != len(card["summary"]):
        raise SystemExit(f"{cid} har {len(card['summary'])} sammendrag, fikk {len(texts)}")
    for item, text in zip(card["summary"], texts):
        item["text"] = text
    save(card)


def graft_source(cid: str, summary_index: int, claim_id: str, note: str = "") -> None:
    card = load(cid)
    source_claim = next(item for item in all_items(card) if item["id"] == claim_id)
    item = card["summary"][summary_index]
    urls = {source["url"] for source in item["sources"]}
    for source in source_claim["sources"]:
        if source["url"] not in urls:
            item["sources"].append(deepcopy(source))
            urls.add(source["url"])
    item["note"] = note
    save(card)


def main() -> None:
    added = restore_exact_summaries()
    print(f"restored {added} exact summary claims")

    set_texts(
        "org-crc",
        [
            "California Resources pumper mest i San Joaquin-dalen og deretter ved Los Angeles. Selskapet sier at det driver om lag 9 000 brønner. Elk Hills og Wilmington er de to største feltene de nevner.",
            "I juli 2024 ble Aera, et annet stort oljeselskap, en del av California Resources.",
            "I sesjonen 2025–2026 har de brukt om lag 1,5 millioner dollar på lobbyvirksomhet.",
            "De har gitt om lag 1,5 millioner dollar til valgkampkomiteen Coalition to Restore California's Middle Class, og en halv million dollar til en annen kampanje.",
        ],
    )
    graft_source("org-crc", 1, "r2-crc-merger")
    graft_source("org-crc", 3, "r2-crc-recip")

    set_texts(
        "org-chevron",
        [
            "Chevron betalte det høyeste oljegebyret til delstaten i 2023, om lag 21 millioner dollar.",
            "I sesjonen 2025–2026 har Chevron brukt om lag 19 millioner dollar på lobbyvirksomhet i California.",
            "Selskapet har også gitt flere millioner dollar i kampanjebidrag. Den største mottakeren er valgkampkomiteen Coalition to Restore California's Middle Class, med om lag 3,8 millioner dollar.",
            "Raffineriet i El Segundo har brudd som det føderale tilsynet kaller alvorlige. Bøtene er om lag 1,1 millioner dollar.",
        ],
    )
    graft_source("org-chevron", 2, "r2-chev-recip")

    set_texts(
        "org-wspa",
        [
            "Western States Petroleum Association er oljebransjens organisasjon. I sesjonen 2025–2026 har de brukt om lag 19 millioner dollar på lobbyvirksomhet.",
            "Et arkiv fra juli 2026 viser fem kvartaler. Summen av dem er lavere enn totalen fra oktober. Vi har ikke en rapport som forklarer forskjellen.",
            "I ett kvartal betalte de blant annet lobbyfirmaene Carpenter Garcia Sievers, Greenberg Traurig og Pillsbury.",
            "Kampanjebidragene deres er små ved siden av lobbyregningen. Den største kampanjestrengen er om lag 26 000 dollar.",
        ],
    )

    set_texts(
        "org-sempra",
        [
            "Sempra og de tilknyttede selskapene SoCalGas og SDG&E har brukt om lag 3,3 millioner dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Gasslekkasjen ved Aliso Canyon var på et lager som tilhører SoCalGas.",
            "Det føderale registeret har et kartpunkt for lageret i Porter Ranch.",
            "Lobbybeløpet gjelder hele konsernet. Det er ikke delt opp på Aliso Canyon.",
        ],
    )

    set_texts(
        "org-epa",
        [
            "EPA er det føderale miljøtilsynet. De sier hvilke områder som ikke klarer grensen for ren luft, og hvor mange som bodde der i 2010.",
            "De skrev i 2025 at San Joaquin-dalen ikke klarte en eldre ozongrense, og i 2026 at dalen har landets høyeste nivå av fint svevestøv, de minste partiklene i luften.",
            "De har også anleggsregisteret som gir kartpunkt for raffinerier og gasslageret Aliso Canyon.",
        ],
    )

    set_texts(
        "org-marathon",
        [
            "Marathon Petroleum har brukt om lag 1,3 millioner dollar på lobbyvirksomhet i California i sesjonen 2025–2026.",
            "Et fond som heter Marathon Asset Management er et annet selskap og er ikke tatt med.",
            "Vi fant ikke et raffineripunkt i California under navnet Marathon i søket som ble kjørt.",
        ],
    )

    set_texts(
        "org-farm-bureau",
        [
            "California Farm Bureau står i jordbrukskategorien. De har brukt om lag 1,4 millioner dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Den største kampanjestrengen er om lag 117 000 dollar. Vi har ikke lagt sammen alle strengene.",
            "Vi har ikke et dokument som sier at organisasjonen står bak et bestemt nitratutslipp eller et bestemt sprøytemiddel. De er med fordi de er en stor jordbruksfiler i de samme fylkene.",
        ],
    )

    set_texts(
        "org-valero",
        [
            "Valero Services har brukt om lag en halv million dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Det føderale registeret har et kartpunkt for Valero-raffineriet i Benicia.",
            "Et annet treff med samme navn ligger på feil breddegrad og er ikke brukt.",
        ],
    )

    set_texts(
        "org-berry",
        [
            "Berry Corporation er et oljeselskap. De har brukt om lag 180 000 dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Treff på blåbær- og jordbærkommisjoner med samme søkeord er andre organisasjoner og er ikke tatt med.",
            "Vi har ikke et tall for hvor mye olje de pumper. De er med fordi de står i oljekategorien, ikke fordi en oljemengde er bekreftet.",
        ],
    )

    set_texts(
        "org-cipa",
        [
            "Dette er en forening for uavhengige oljeselskaper. De har brukt om lag 700 000 dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "De står i samme oljekategori som Chevron og oljeorganisasjonen WSPA.",
            "Vi har ikke koblet foreningen til en bestemt brønn eller en bestemt lovavstemning ut over lobbytallet.",
        ],
    )

    set_texts(
        "org-corteva",
        [
            "Corteva står i industrikategorien hos valgmyndigheten. De har brukt om lag 140 000 dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Sprøytemiddelstatistikken nevner ikke Corteva. Vi kan derfor ikke si at de står for pundene i Fresno eller Kern.",
            "Vi har ikke kjørt et eget søk på kampanjebidragene deres.",
        ],
    )

    set_texts(
        "org-western-growers",
        [
            "Western Growers står i jordbrukskategorien. De har brukt om lag 1,2 millioner dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Vi har ikke kjørt et eget søk på kampanjebidragene deres.",
            "Vi har ikke koblet pengene til et bestemt sprøytemiddel eller et bestemt fylke.",
        ],
    )

    set_texts(
        "org-oehha",
        [
            "OEHHA er delstatens kontor for helsefare i miljøet. De lager CalEnviroScreen, et kart som rangerer nabolag etter forurensning og helse.",
            "Kartdataene ble hentet 28. oktober 2026. Feltet for opphavsrett i metadataene er tomt. Områdene er merket med et nummer for hvert boligområde.",
            "Kartet siler områder. Det måler ikke at en bestemt person er syk. Vi bruker det til å sammenligne steder, ikke som en diagnose.",
        ],
    )

    set_texts(
        "org-dpr",
        [
            "Dette er delstatens tilsyn med sprøytemidler. I 2022 ble det brukt om lag 180 millioner pund virksomt stoff.",
            "Fresno, Kern og Tulare hadde de høyeste pundtallene i fylkeslisten.",
            "Pundtallet trekker opp stoffer som brukes i store mengder, som svovel. Det samme jordet kan telles flere ganger. Pund er ikke det samme som hvor giftig stoffet er.",
        ],
    )

    set_texts(
        "org-scaqmd",
        [
            "Dette er luftkontoret for området rundt Los Angeles. De sier at området ikke klarer grensen for ozon, en gass som irriterer lungene.",
            "I 2018 sto tunge lastebiler for 27 prosent av NOx, en gass som er med på å lage ozon. Raffinering var blant de største faste kildene, etter fyring i bygninger.",
            "De har målt utslipp ved seks raffinerier, men kalte anleggene A til F i sammendraget. Vi kan derfor ikke si hvilket tall som hører til hvilket selskap.",
        ],
    )

    set_texts(
        "org-iid",
        [
            "Imperial Irrigation District er vannverket ved Salton Sea. De flytter inntil om lag 300 000 acre-fot vann i året, og det blotlegger sjøbunn som kan bli til støv. Acre-fot er et amerikansk mål for vannmengde.",
            "De har brukt om lag 300 000 dollar på lobbyvirksomhet i sesjonen 2025–2026.",
            "Statens årsrapport om innsjøen er ikke skrevet av vannverket. Den er sendt til vanntilsynet.",
        ],
    )

    set_texts(
        "firm-carpenter-garcia-sievers",
        [
            "Oljeorganisasjonen WSPA betalte firmaet 90 000 dollar i ett kvartal i 2025. Til da på året var summen om lag 180 000 dollar.",
            "Adressen i skjemaet er Sacramento.",
            "I registeret for 2024–2026 står også andre oppdragsgivere, blant annet Hyundai, Medtronic og en asfaltforening. Ingen av dem er en miljøorganisasjon, så vi sier ikke at firmaet jobber for begge sider.",
        ],
    )

    set_texts(
        "firm-greenberg-traurig",
        [
            "WSPA betalte lobbyfirmaet Greenberg Traurig 37 500 dollar i ett kvartal i 2025.",
            "Beløpet er det WSPA betalte, ikke firmaets hele omsetning.",
            "Andre oppdragsgivere i registeret er en skolekjede og et eiendomsselskap. Ingen av dem er en miljøorganisasjon, så vi sier ikke at firmaet jobber for begge sider.",
        ],
    )

    set_texts(
        "firm-pillsbury",
        [
            "WSPA betalte lobbyfirmaet Pillsbury om lag 59 000 dollar i ett kvartal i 2025, inkludert utlegg.",
            "Skjemaet viser ikke at firmaet jobbet med en bestemt lov.",
            "En annen oppdragsgiver er en forening for gjenvunnet materiale. Det er ikke en miljøorganisasjon, så vi sier ikke at firmaet jobber for begge sider.",
        ],
    )

    set_texts(
        "firm-leacox",
        [
            "WSPA betalte Leacox & Associates 6 000 dollar i ett kvartal i 2025.",
            "Beløpet er lite ved siden av det WSPA betalte Carpenter Garcia Sievers i samme skjema.",
            "Vi fant ikke andre oppdragsgivere i uttrekket for 2024–2026. Det betyr ikke at de ikke har noen. Vi kan derfor ikke si om de også jobber for en miljøorganisasjon.",
        ],
    )

    replacements = {
        "ca-problem-south-coast-air": (
            "Når hele luftområdet sammenlignes med resten av California, er ikke astma eller kols høyere. Vi vet ikke om luften er årsaken til sykdom der tallene likevel skiller seg ut.",
            "Når hele luftområdet sammenlignes med resten av California, er ikke astma eller kols, en lungesykdom, høyere. Vi vet ikke om luften er årsaken til sykdom der tallene likevel skiller seg ut.",
        ),
        "ca-problem-refineries": (
            "Chevron-raffineriet i El Segundo har brutt miljøregler så ofte at det føderale tilsynet kaller det et alvorlig brudd.",
            "Det føderale tilsynet kaller bruddene ved Chevron-raffineriet i El Segundo et alvorlig brudd.",
        ),
        "ca-problem-aliso-canyon": (
            "Myndighetene lar lageret fortsatt holde om lag 69 milliarder kubikkfot gass. Et forslag om å senke taket er ikke vedtatt.",
            "Myndighetene lar lageret fortsatt holde om lag 69 milliarder kubikkfot gass. Kubikkfot er et amerikansk rommål. Et forslag om å senke taket er ikke vedtatt.",
        ),
        "ca-problem-salton-sea": (
            "En målerapport sier at om lag 38 000 acre sjøbunn lå bart ved utgangen av 2024. Statens egen årsrapport gir ikke ett samlet tall for den bare bunnen.",
            "En målerapport sier at om lag 38 000 acre sjøbunn lå bart ved utgangen av 2024. En acre er et amerikansk flatemål. Statens egen årsrapport gir ikke ett samlet tall for den bare bunnen.",
        ),
    }
    for cid, (old, new) in replacements.items():
        card = load(cid)
        hits = [item for item in card["summary"] if item["text"] == old]
        if len(hits) != 1:
            raise SystemExit(f"{cid} fant {len(hits)} treff for setningen som skulle byttes")
        hits[0]["text"] = new
        save(card)
    print("summary texts aligned")


if __name__ == "__main__":
    main()
