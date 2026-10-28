#!/usr/bin/env python3
"""Replace card summaries with plain Norwegian. Sources stay on the claims."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"


def load(cid: str) -> dict:
    return json.loads((CARDS / f"{cid}.json").read_text(encoding="utf-8"))


def save(card: dict) -> None:
    (CARDS / f"{card['id']}.json").write_text(
        json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def all_claims(card: dict) -> list[dict]:
    found = list(card["summary"]) + list(card["claims"])
    for name in ("population", "demographics", "health_outcomes"):
        block = card.get(name)
        if block:
            found.extend(block["claims"])
    return found


def sources_for(card: dict, *ids: str) -> list[dict]:
    by_id = {claim["id"]: claim for claim in all_claims(card)}
    found = []
    seen = set()
    for cid in ids:
        claim = by_id.get(cid)
        if claim is None:
            raise SystemExit(f"{card['id']} mangler krav {cid}")
        for source in claim["sources"]:
            if source["url"] in seen:
                continue
            seen.add(source["url"])
            found.append(json.loads(json.dumps(source)))
    if not found:
        raise SystemExit(f"{card['id']} fikk ingen kilder")
    return found


def claim(cid: str, text: str, sources: list[dict]) -> dict:
    return {"id": cid, "text": text, "status": "confirmed", "note": "", "sources": sources}


def set_summary(card: dict, items: list[tuple[str, tuple[str, ...]]]) -> None:
    card["summary"] = [
        claim(f"plain-{index}", text, sources_for(card, *ids))
        for index, (text, ids) in enumerate(items, start=1)
    ]


def rewrite_texts(card: dict, texts: list[str]) -> None:
    if len(texts) != len(card["summary"]):
        raise SystemExit(f"{card['id']} har {len(card['summary'])} sammendrag, fikk {len(texts)}")
    for item, text in zip(card["summary"], texts):
        item["text"] = text


def main() -> None:
    problems()
    others()
    print("summaries rewritten")


def problems() -> None:
    sample = load("ca-problem-south-coast-air")
    if any(item["id"] == "plain-1" for item in sample["summary"]):
        return
    card = load("ca-problem-south-coast-air")
    set_summary(card, [
        ("Luften rundt Los Angeles er for skitten til å klare den føderale grensen for ren luft. EPA regnet med om lag 16 millioner mennesker i området i 2010. Mye av forurensningen kommer fra biler og tunge lastebiler, og raffinerier er blant de største faste utslippene.", ("s1", "s3")),
        ("Området klarer ikke grensen for fint svevestøv, de minste partiklene i luften. Målingen ligger på 13,2. Det klarer heller ikke grensen for bakkenær ozon, en gass som irriterer lungene.", ("s1", "s2")),
        ("I 2018 sto tunge lastebiler for 27 prosent av NOx, en gass som er med på å lage både ozon og støv. Veitrafikk sto for 44 prosent.", ("s3",)),
        ("I ett boligområde i Los Angeles er andelen barn født med lav vekt høyere enn i 90 av 100 områder i California. Vi vet ikke om luften er årsaken.", ("r2-ca-problem-south-coast-air-sum",)),
        ("Når hele luftområdet sammenlignes med resten av California, er ikke astma eller kols høyere. Vi vet ikke om luften er årsaken til sykdom der tallene likevel skiller seg ut.", ("r4-sc-boundary",)),
    ])
    save(card)

    card = load("ca-problem-san-joaquin-air")
    set_summary(card, [
        ("I den lange jordbruksdalen fra Stockton til Bakersfield er luften den skitneste i USA, målt som fint svevestøv. EPA regnet med om lag 4 millioner mennesker der i 2010. Dalen har bedt om mer tid til å klare grensen, til slutten av 2030.", ("s1", "s2", "c2")),
        ("Området klarer ikke grensen for fint svevestøv, og heller ikke en eldre grense for ozon. Støvmålingen er høyere enn i Los Angeles-området.", ("s1", "s3", "c4")),
        ("Dalfeber, en sykdom man kan få av sopp i støv, er langt vanligere her. I Kern fylke var raten om lag 14 ganger så høy som i hele California i 2022.", ("r3-sjv-vf",)),
        ("I selve luftområdet er andelen voksne uten videregående skole om lag halvannen gang så høy som i resten av California. Vi vet ikke om luften er årsaken.", ("r4-sjv-boundary",)),
        ("I ett boligområde i Fresno er astmabesøk på legevakt verre enn i 97 av 100 områder i California. For hele dalen er astmatallene høyere, men ikke dobbelt så høye. Vi vet ikke om luften er årsaken.", ("r2-ca-problem-san-joaquin-air-sum", "r4-sjv-places")),
    ])
    save(card)

    card = load("ca-problem-drinking-water")
    set_summary(card, [
        ("Noen offentlige vannverk leverer vann som bryter helsereglene. Ved utgangen av 2024 gjaldt det 390 verk og om lag 800 000 mennesker. De vanligste grunnene var arsen, et industrikjemikalie og nitrat. Gjødsel er den største kilden til nitrat i grunnvannet i de hardest rammede jordbruksdalene.", ("s1", "s3", "c2")),
        ("Om lag 8 av 10 slike verk ligger i områder staten kaller økonomisk vanskeligstilte. Halvparten ligger i områder der de fleste innbyggerne ikke er hvite.", ("s2",)),
        ("De aller fleste i California, 98 prosent, fikk likevel vann som holdt mål i 2024. Om lag 1,5 millioner mennesker var på verk som staten sier står i fare.", ("s4",)),
        ("En nyere liste fra oktober 2026 har 416 verk. Deres eget folketall er om lag 430 000. Det er ikke det samme tallet som 800 000 fra 2024, fordi listen endrer seg.", ("r3-dw-tracts",)),
        ("Der verkene som feiler ligger, er det flere uten videregående skole enn hos verk som holder mål. Vi vet ikke om vannet er årsaken.", ("r4-dw-health",)),
    ])
    save(card)

    card = load("ca-problem-oil-gas-proximity")
    set_summary(card, [
        ("En lov fra 2022 sier at nye olje- og gassbrønner ikke skal bores nærmere enn om lag 1 kilometer fra boliger, skoler og andre sårbare steder. Etaten som passer på brønnene, har ikke selv telt hvor mange som bor der. Vår egen telling gir om lag 3 millioner mennesker og om lag 1,1 millioner boliger.", ("s1", "r2-oil-people", "r3-oil-buffer")),
        ("Om lag 700 offentlige skoler og om lag 200 private skoler ligger innenfor den avstanden.", ("r3-oil-buffer",)),
        ("Kern fylke pumpet det aller meste av oljen i California i 2023. Chevron og Aera betalte de største avgiftene til tilsynsetaten.", ("s3",)),
        ("Oljeselskapenes felles organisasjon brukte om lag 19 millioner dollar på å påvirke politikerne i denne toårsperioden.", ("c3",)),
        ("Sykdomstallene for nabolag nær brønner er ikke høyere enn i resten av California. Vi vet ikke om brønnene er årsaken.", ("r2-oil-health",)),
    ])
    save(card)

    card = load("ca-problem-pesticides")
    set_summary(card, [
        ("I 2022 ble det sprøytet om lag 180 millioner pund virksomt stoff i California. Mest gikk ut i jordbruksfylkene Fresno, Kern og Tulare. De som bor og jobber der, er nærmest sprøytingen.", ("s1", "s2")),
        ("Fresno og Kern hadde hver over 25 millioner pund. Tulare hadde om lag 18 millioner og Monterey om lag 9 millioner.", ("s2",)),
        ("I ett boligområde i Fresno er astmabesøk på legevakt verre enn i 98 av 100 områder i California. Vi vet ikke om sprøytemidlene er årsaken.", ("r2-ca-problem-pesticides-sum",)),
        ("I de fire fylkene med mest sprøyting er andelen uten videregående skole om lag halvannen gang så høy som i resten av California. Vi vet ikke om sprøytingen er årsaken.", ("r3-pest-ces",)),
        ("Staten registrerte om lag 1 000 sykdomstilfeller som kan henge sammen med sprøytemidler i 2022. Los Angeles hadde flest, og de fleste der kom ikke fra jordbruk.", ("r3-pest-pisp",)),
    ])
    save(card)

    card = load("ca-problem-salton-sea")
    set_summary(card, [
        ("Innsjøen Salton Sea krymper fordi vann som før rant dit, brukes andre steder. Tørr sjøbunn kan blåse opp som støv. Vannverket Imperial Irrigation District flytter inntil en stor mengde vann i året, og det er det som blotlegger bunnen.", ("s1",)),
        ("En målerapport sier at om lag 38 000 acre sjøbunn lå bart ved utgangen av 2024. Statens egen årsrapport gir ikke ett samlet tall for den bare bunnen.", ("r2-salton-playa",)),
        ("Innenfor om lag en mil fra strandlinjen bor om lag 12 000 mennesker. Det er mye færre enn hele Imperial fylke, der EPA regnet om lag 150 000 mennesker i 2010.", ("r4-salt-mile", "r2-salton-pop")),
        ("I hele Imperial fylke er astmabesøk på legevakt om lag 1,7 ganger så høye som i resten av California, og flere voksne mangler videregående skole. Vi vet ikke om støvet er årsaken.", ("r3-salt-ces",)),
        ("Dalfeber er ikke vanligere i Imperial enn i California som helhet. I 2022 var raten lavere der enn i delstaten.", ("r3-salt-vf-cancer",)),
    ])
    save(card)

    card = load("ca-problem-refineries")
    set_summary(card, [
        ("Raffinerier lager drivstoff tett på boliger i Los Angeles-området. En lov fra 2017 sier at eieren skal måle luften ved gjerdet, og at naboene skal kunne se tallene.", ("s1",)),
        ("Chevron-raffineriet i El Segundo har brutt miljøregler så ofte at det føderale tilsynet kaller det et alvorlig brudd.", ("s3",)),
        ("Phillips 66 kunngjorde i 2024 at raffineriet i Wilmington og Carson skulle stanse driften mot slutten av 2025. Selve stansen er beskrevet på selskapets eget kort.", ("r2-ref-ops",)),
        ("Torrance-raffineriet drives av Torrance Refining, et selskap PBF kjøpte i 2016.", ("r2-ref-ops",)),
        ("Innenfor en mil bor noen tusen mennesker ved hvert av de tre anleggene. Sykdomstallene der er ikke høyere enn i resten av California. Vi vet ikke om raffineriet er årsaken.", ("r2-ref-health",)),
    ])
    save(card)

    card = load("ca-problem-aliso-canyon")
    set_summary(card, [
        ("I 2015 og 2016 lekket et stort gasslager over bydelen Porter Ranch i Los Angeles. Lageret eies av gasselskapet SoCalGas. Det er den største metanlekkasjen som er dokumentert i USA.", ("s1", "s2", "s4")),
        ("Lekkasjen varte fra oktober 2015 til februar 2016. Utslippet var om lag 100 000 tonn metan, en kraftig klimagass.", ("s1", "s2")),
        ("Mengden tilsvarer omtrent det 190 000 boliger i Los Angeles bruker av gass på ett år. Det er en sammenligning, ikke et tall på hvor mange som ble evakuert.", ("s3",)),
        ("Myndighetene lar lageret fortsatt holde om lag 69 milliarder kubikkfot gass. Et forslag om å senke taket er ikke vedtatt.", ("r2-aliso-cpuc", "r3-aliso-scope")),
        ("Boligområdet nærmest lageret er relativt velstående, og de vanlige sykdomstallene der skiller seg ikke ut. Vi vet ikke om lekkasjen ga varig sykdom. Det er ikke målt i disse tallene.", ("aliso-demo", "aliso-asthma")),
    ])
    save(card)

    card = load("ca-problem-pfas")
    set_summary(card, [
        ("PFAS er en gruppe kjemikalier som nesten ikke brytes ned. De er brukt i blant annet brannskum og industri, og kan havne i drikkevann. Delstaten har pålagt testing av brønner.", ("s1", "s2")),
        ("Etaten selv sier om lag 3 600 til 4 000 brønner, ikke ett fast tall. En liste fra oktober 2026 har om lag 11 000 kilder og om lag 4 000 vannverk. Det er en annen liste.", ("s1", "s2", "r3-pfas-rows")),
        ("Om lag halvparten av kildene, 5 500, har et kartpunkt. Resten har vi ikke koordinat for.", ("r4-pfas-geo",)),
        ("Vi vet ikke hvor mange mennesker som drikker vann over en grense. Det tallet står ikke i dokumentene som er lest.", ("s4", "r2-pfas-health")),
    ])
    save(card)

    card = load("ca-problem-groundwater-overdraft")
    set_summary(card, [
        ("Noen grunnvannsbasseng tappes raskere enn de fylles. Da kan bakken synke, saltvann komme inn, og brønner gå tørre. Delstatens vannetat har pekt ut 21 slike basseng. Elleve ligger i San Joaquin-dalen.", ("s1", "s2", "s3")),
        ("En lov fra 2014 pålegger lokale planer som skal stoppe overtappingen.", ("s1",)),
        ("Om lag 4 millioner mennesker bor innenfor disse bassengene, etter vår telling av folketellingsblokker. Etaten har ikke selv publisert et folketall.", ("r4-gw-basins", "r2-ca-problem-groundwater-overdraft-pop")),
        ("Der er andelen voksne uten videregående skole om lag halvannen gang så høy som i resten av California. Vi vet ikke om grunnvannet er årsaken.", ("r4-gw-basins",)),
    ])
    save(card)


def others() -> None:
    if load("org-chevron")["summary"][0]["text"].startswith("Chevron betalte det høyeste"):
        return
    rewrites = {
        "bill-ab-1647": [
            "Dette er loven som sier at luften skal måles ved gjerdet rundt raffinerier, og at naboene skal kunne se tallene. Den ble vedtatt i 2017. Forfatteren var Al Muratsuchi.",
            "Forsamlingen stemte 57 mot 19. Senatet stemte 28 mot 11.",
            "Eieren av raffineriet skal betale for målingen, med ett unntak hvis målestasjonen også brukes til andre formål.",
            "Vi har ikke sjekket om hvert eneste raffineri faktisk har målingen i drift i 2026.",
        ],
        "bill-ab-1739": None,
        "bill-ab-617": [
            "Dette er loven som sier at delstaten skal følge ekstra med på lufta i nabolag som allerede har mye forurensning. Cristina Garcia la den fram i 2017.",
            "Forsamlingen stemte 50 mot 24. Senatet stemte 27 mot 13.",
            "Loven gjelder hele California, ikke bare ett luftområde. Den kan brukes både rundt Los Angeles og i San Joaquin-dalen.",
        ],
        "bill-sb-1137": None,
        "bill-sb-1168": None,
        "bill-sb-1319": None,
        "bill-sb-200": [
            "Dette er loven som opprettet et fond for trygt drikkevann. Bill Monning la den fram i 2019.",
            "Senatet stemte 38 mot 1. Forsamlingen stemte 68 mot 0. Nesten alle var enige.",
            "Fondet får inntil om lag 130 millioner dollar i året fra klimakvoten, fram til midten av 2030.",
            "Listen over vannverk som ikke holder mål, er en del av dette programmet.",
        ],
        "org-chevron": [
            "Chevron er et av de største oljeselskapene i California. Raffineriet i El Segundo ligger ved kysten i Los Angeles, og selskapet pumper mye olje i delstaten.",
            "I denne toårsperioden har Chevron brukt om lag 19 millioner dollar på å påvirke politikere i California.",
            "Selskapet har også gitt flere millioner dollar i kampanjebidrag. Den største mottakeren er en valgkampgruppe for oljebransjen.",
            "Raffineriet i El Segundo har brutt miljøregler så ofte at det føderale tilsynet kaller det et alvorlig brudd.",
        ],
        "org-crc": [
            "California Resources er et oljeselskap som pumper mest i San Joaquin-dalen og ved Los Angeles. I 2024 ble Aera, et annet stort oljeselskap, en del av konsernet.",
            "Selskapet sier selv at det driver om lag 9 000 brønner. De to største feltene de nevner, er Elk Hills og Wilmington.",
            "I denne toårsperioden har de brukt om lag 1,5 millioner dollar på lobbyvirksomhet.",
            "De har gitt om lag 1,5 millioner dollar til den samme olje-valgkampgruppen som Chevron, pluss en halv million til en annen kampanje.",
        ],
        "org-wspa": [
            "Dette er oljeselskapenes felles organisasjon i vesten. De påvirker lover og etater på vegne av bransjen.",
            "I denne toårsperioden har de brukt om lag 19 millioner dollar på lobbyvirksomhet. Det er blant de høyeste beløpene i oljekategorien.",
            "I ett kvartal betalte de blant annet lobbyfirmaene Carpenter Garcia Sievers, Greenberg Traurig og Pillsbury.",
            "De har skrevet hvilke lovforslag de jobber med, men ikke om de er for eller mot. Kampanjebidragene deres er små sammenlignet med lobbyregningen.",
        ],
        "org-phillips66": None,
        "org-pbf": None,
        "org-torrance-refining": None,
        "org-valero": [
            "Valero driver raffineriet i Benicia, ved bukta nord for San Francisco. Selskapet har brukt om lag en halv million dollar på lobbyvirksomhet i denne toårsperioden.",
            "Det føderale registeret har et kartpunkt for raffineriet i Benicia.",
            "Et annet treff med samme navn ligger på feil breddegrad og er ikke brukt.",
        ],
        "org-marathon": [
            "Marathon Petroleum har brukt om lag 1,3 millioner dollar på lobbyvirksomhet i California i denne toårsperioden.",
            "Vi fant ikke et raffineripunkt i California under navnet Marathon i søket som ble kjørt.",
            "Et fond som heter Marathon Asset Management er et annet selskap og er ikke tatt med.",
        ],
        "org-sempra": [
            "Sempra eier gasselskapene SoCalGas og SDG&E. SoCalGas eier gasslageret Aliso Canyon, der den store lekkasjen skjedde.",
            "Konsernet har brukt om lag 3,3 millioner dollar på lobbyvirksomhet i denne toårsperioden.",
            "Det føderale registeret har et kartpunkt for lageret i Porter Ranch.",
            "Lobbybeløpet gjelder hele konsernet. Det er ikke delt opp på Aliso Canyon.",
        ],
        "org-calgem": None,
        "org-cipa": [
            "Dette er en forening for mindre oljeselskaper. De har brukt om lag 700 000 dollar på lobbyvirksomhet i denne toårsperioden.",
            "De står i samme oljekategori som Chevron og oljeorganisasjonen WSPA.",
            "Vi har ikke koblet foreningen til en bestemt brønn eller en bestemt lovavstemning ut over lobbytallet.",
        ],
        "org-berry": [
            "Berry Corporation er et oljeselskap. De har brukt om lag 180 000 dollar på lobbyvirksomhet i denne toårsperioden.",
            "Vi har ikke et tall for hvor mye olje de pumper, og ikke et kartpunkt for et anlegg.",
            "Treff på blåbær- og jordbærkommisjoner med samme søkeord er andre organisasjoner og er ikke tatt med.",
        ],
        "org-epa": [
            "EPA er det føderale miljøtilsynet. De sier hvilke områder som ikke klarer grensen for ren luft, og hvor mange som bodde der i 2010.",
            "De har også anleggsregisteret som gir kartpunkt for raffinerier og gasslageret Aliso Canyon.",
            "EPA skrev i 2026 at San Joaquin-dalen har det høyeste nivået av fint svevestøv i landet.",
        ],
        "org-carb": None,
        "org-scaqmd": [
            "Dette er luftkontoret for området rundt Los Angeles. De sier at området ikke klarer grensen for ozon.",
            "I deres regnskap kom mye av den forurensende gassen NOx fra lastebiler. Raffinerier var blant de største faste kildene.",
            "De har målt utslipp ved seks raffinerier, men kalte anleggene A til F i sammendraget. Vi kan derfor ikke si hvilket tall som hører til hvilket selskap.",
        ],
        "org-sjvapcd": [
            "Dette er luftkontoret for San Joaquin-dalen. De har hovedansvaret for planene som skal få dalen innenfor grensen for ren luft.",
            "De vedtok i 2024 en plan som ber om utsettelse til slutten av 2030 for fint svevestøv.",
            "De tar faste anlegg og støv fra bakken. Delstatens lufttilsyn tar biler og lastebiler.",
        ],
        "org-swrcb": [
            "Dette er delstatens vanntilsyn. De fører listen over vannverk som ikke holder helsereglene.",
            "De har også pålagt testing av kjemikaliene PFAS i drikkevannsbrønner.",
            "Rapporten om Salton Sea er sendt til dette styret.",
        ],
        "org-dwr": None,
        "org-dpr": [
            "Dette er delstatens tilsyn med sprøytemidler. De publiserer hvor mange pund som er brukt, fylke for fylke.",
            "I 2022 var summen om lag 180 millioner pund. Fresno, Kern og Tulare lå høyest.",
            "Pundtallet trekker opp stoffer som brukes i store mengder, som svovel. Det er ikke det samme som hvor giftig hvert stoff er.",
        ],
        "org-oehha": [
            "OEHHA er delstatens kontor for helsefare. De lager CalEnviroScreen, et kart som rangerer nabolag etter forurensning og helse.",
            "Et høyt tall betyr at nabolaget ligger dårligere an enn de fleste andre i California. Det er ikke en diagnose på en enkelt person.",
            "Når vi skriver at vi ikke vet om miljøet er årsaken, er det fordi dette kartet viser sammenheng, ikke bevis.",
        ],
        "org-iid": [
            "Imperial Irrigation District er vannverket ved Salton Sea. De flytter vann som før rant til innsjøen, og det blotlegger sjøbunn som kan bli til støv.",
            "De har brukt om lag 300 000 dollar på lobbyvirksomhet i denne toårsperioden.",
            "Statens årsrapport om innsjøen er ikke skrevet av vannverket. Den er sendt til vanntilsynet.",
        ],
        "org-farm-bureau": [
            "Dette er bøndenes organisasjon i California. De har brukt om lag 1,4 millioner dollar på lobbyvirksomhet i denne toårsperioden.",
            "Vi har ikke et dokument som sier at organisasjonen står bak et bestemt nitratutslipp eller et bestemt sprøytemiddel.",
            "De er med fordi de er en stor jordbruksstemme i de samme fylkene som har mest sprøyting og nitrat.",
        ],
        "org-western-growers": [
            "Western Growers er en organisasjon for grønnsak- og fruktdyrkere. De har brukt om lag 1,2 millioner dollar på lobbyvirksomhet i denne toårsperioden.",
            "Vi har ikke kjørt et eget søk på kampanjebidragene deres.",
            "Vi har ikke koblet pengene til et bestemt sprøytemiddel eller et bestemt fylke.",
        ],
        "org-corteva": [
            "Corteva er et selskap som lager såvarer og plantevern. De har brukt om lag 140 000 dollar på lobbyvirksomhet i denne toårsperioden.",
            "Sprøytemiddelstatistikken nevner ikke Corteva. Vi kan derfor ikke si at de står for pundene i Fresno eller Kern.",
            "Vi har ikke kjørt et eget søk på kampanjebidragene deres.",
        ],
        "lawmaker-lena-gonzalez": None,
        "lawmaker-al-muratsuchi": None,
        "lawmaker-fran-pavley": None,
        "lawmaker-roger-dickinson": None,
        "lawmaker-bill-monning": None,
        "lawmaker-cristina-garcia": None,
        "firm-carpenter-garcia-sievers": [
            "Dette er et lobbyfirma i Sacramento. Oljeorganisasjonen WSPA betalte dem 90 000 dollar i ett kvartal i 2025.",
            "I det offentlige registeret står også andre oppdragsgivere, blant annet Hyundai, Medtronic og en asfaltforening. Ingen av dem er en miljøorganisasjon.",
            "Vi kan derfor ikke si at firmaet jobber for begge sider i oljesaker. Registeret viser bare hvem som har betalt.",
        ],
        "firm-greenberg-traurig": [
            "Dette er et stort advokat- og lobbyfirma. WSPA betalte dem 37 500 dollar i ett kvartal i 2025.",
            "Andre oppdragsgivere i registeret er en skolekjede og et eiendomsselskap. Ingen av dem er en miljøorganisasjon.",
            "Beløpet er det WSPA betalte, ikke firmaets hele omsetning.",
        ],
        "firm-pillsbury": [
            "Dette er et advokat- og lobbyfirma. WSPA betalte dem om lag 59 000 dollar i ett kvartal i 2025, inkludert utlegg.",
            "En annen oppdragsgiver i registeret er en forening for gjenvunnet materiale. Det er ikke en miljøorganisasjon i oljesaken.",
            "Beløpet er det WSPA betalte, ikke firmaets hele omsetning.",
        ],
        "firm-leacox": [
            "Dette er et lite lobbyfirma. WSPA betalte dem 6 000 dollar i ett kvartal i 2025.",
            "Vi fant ikke en liste over andre oppdragsgivere i uttrekket for 2024–2026. Det betyr ikke at de ikke har noen.",
            "Vi kan derfor ikke si om de også jobber for en miljøorganisasjon.",
        ],
    }
    for cid, texts in rewrites.items():
        if texts is None:
            continue
        card = load(cid)
        rewrite_texts(card, texts)
        save(card)
    sourced_rewrites()


def add_claim(card: dict, cid: str, text: str, url: str, title: str, publisher: str) -> None:
    if any(item["id"] == cid for item in all_claims(card)):
        return
    card["claims"].append(
        {
            "id": cid,
            "text": text,
            "status": "confirmed",
            "note": "",
            "sources": [
                {
                    "url": url,
                    "title": title,
                    "publisher": publisher,
                    "retrieved": "2026-10-28",
                    "archive_url": "",
                    "archive_note": "Wayback-feltet fylles av scripts/archive_sources.py.",
                }
            ],
        }
    )


def sourced_rewrites() -> None:
    card = load("bill-ab-1739")
    set_summary(card, [
        ("Dette er en av tre lover fra 2014 som skulle stanse at grunnvann tappes for hardt. Roger Dickinson la den fram. Fran Pavley var medforslagsstiller.", ("s1",)),
        ("Forsamlingen stemte 47 mot 28. Senatet stemte 26 mot 11.", ("s2",)),
        ("Oljeselskapet Chevron skrev i et lobby-skjema at de jobbet med denne loven. Skjemaet sier ikke om de var for eller mot.", ("r3-ab1739-lobby",)),
    ])
    save(card)

    card = load("bill-sb-1137")
    set_summary(card, [
        ("Dette er loven som sier at nye oljebrønner ikke skal bores nærmere enn om lag 1 kilometer fra boliger og skoler. Lena Gonzalez og Monique Limón la den fram. Den ble vedtatt i 2022.", ("s1", "s3")),
        ("Senatet stemte 25 mot 10. Forsamlingen stemte 46 mot 24.", ("s2",)),
        ("Et folkeavstemningsforslag stanset loven en periode. Den begynte å gjelde igjen da forslaget ble trukket i 2024.", ("s4",)),
        ("Oljebransjens organisasjon skrev senere at de jobbet med loven. Skjemaet sier ikke om de var for eller mot.", ("r3-sb1137-wspa",)),
    ])
    save(card)

    card = load("bill-sb-1168")
    set_summary(card, [
        ("Dette er hovedloven fra 2014 om at grunnvann ikke skal tappes for hardt. Fran Pavley la den fram, og hun stemte selv ja.", ("s1", "s3")),
        ("Senatet stemte 25 mot 10 da loven ble ferdig. Forsamlingen stemte 47 mot 27.", ("s2",)),
        ("Chevron, Aera og oljeorganisasjonen deres skrev ikke denne loven på skjemaene vi leste. En grunnvannsforening og en miljøorganisasjon gjorde det. Ingen skrev om de var for eller mot.", ("r3-sb1168-lobby",)),
    ])
    save(card)

    card = load("bill-sb-1319")
    set_summary(card, [
        ("Dette er en søsterlov til grunnvannsloven fra 2014. Fran Pavley la den fram.", ("s1",)),
        ("Senatet stemte 24 mot 10. Forsamlingen stemte 48 mot 26.", ("s2",)),
        ("Oljeorganisasjonen WSPA, Chevron og Aera skrev at de jobbet med loven. Skjemaene sier ikke om de var for eller mot.", ("r3-sb1319-lobby",)),
    ])
    save(card)

    card = load("org-phillips66")
    set_summary(card, [
        ("Phillips 66 har raffineriet i Wilmington og Carson, sør i Los Angeles. De har brukt om lag 2 millioner dollar på lobbyvirksomhet i denne toårsperioden.", ("s1", "s3")),
        ("Selskapet skriver at de sluttet å lage drivstoff der i slutten av 2025, og at anlegget er lagt i ro. Lufttilsynet sier det samme, og at lagertanker fortsatt brukes.", ("r3-psx-10k", "r4-psx-idle")),
        ("Vi har ikke et dokument som sier at alle tanker er tømt.", ("r4-psx-idle",)),
        ("ConocoPhillips er et annet selskap i registrene. De pengene er ikke lagt sammen med Phillips 66.", ("s2",)),
    ])
    save(card)

    card = load("org-pbf")
    set_summary(card, [
        ("PBF er oljeselskapet som kjøpte raffineriet i Torrance i 2016. To av selskapets filer har brukt til sammen om lag 1 million dollar på lobbyvirksomhet.", ("s1", "r2-pbf-own")),
        ("Det føderale tilsynet skrev i 2025 at Torrance Refining driver anlegget.", ("r2-pbf-own",)),
        ("Et annet treff på navnet PBF er en frisørorganisasjon. Den har ingenting med raffineriet å gjøre.", ("s2",)),
    ])
    save(card)

    card = load("org-torrance-refining")
    set_summary(card, [
        ("Dette selskapet driver raffineriet i Torrance, sør i Los Angeles. Adressen er 3700 West 190th Street.", ("s1",)),
        ("Det føderale anleggsregisteret har et kartpunkt for anlegget.", ("s1",)),
        ("Miljøtilsynet skrev i 2025 at selskapet driver anlegget.", ("r2-torr-op",)),
    ])
    save(card)

    card = load("org-calgem")
    set_summary(card, [
        ("CalGEM er delstatens tilsyn med olje- og gassbrønner. De fører regnskap over hvor oljen pumpes.", ("s1",)),
        ("I 2023 kom det meste av oljen fra Kern fylke, om lag 90 millioner fat. Los Angeles fylke hadde om lag 9 millioner fat.", ("s2",)),
        ("De beskriver at loven om avstand til boliger ble stanset av et folkeavstemningsforslag og begynte å gjelde igjen i 2024.", ("s3",)),
    ])
    save(card)

    card = load("org-carb")
    set_summary(card, [
        ("CARB er delstatens lufttilsyn. De har ansvar for utslipp fra biler og lastebiler. De lokale luftkontorene tar faste anlegg.", ("s1",)),
        ("De regnet ut at gasslekkasjen ved Aliso Canyon var om lag 100 000 tonn metan.", ("s2",)),
        ("De har også ansvar for en lov om ekstra oppfølging av lufta i nabolag med mye forurensning.", ("s3",)),
    ])
    save(card)

    card = load("org-dwr")
    set_summary(card, [
        ("Dette er delstatens vannetat. De peker ut grunnvannsbasseng som tappes for hardt.", ("s1",)),
        ("De har pekt ut 21 slike basseng. Elleve ligger i San Joaquin-dalen.", ("s2",)),
        ("Hvis tappingen fortsetter, kan bakken synke og saltvann komme inn i brønnene.", ("s3",)),
    ])
    save(card)

    handbook = "https://www.assembly.ca.gov/sites/assembly.ca.gov/files/Publications/Legislative%20Handbook%202013%e2%80%9314.pdf"
    seating = "https://www.assembly.ca.gov/assemblymembers/member-seating-chart"
    for cid, text, url, title in (
        ("lawmaker-al-muratsuchi", "Fortegnelsen over medlemmer viser Al Muratsuchi som representant for forsamlingsdistrikt 66 i Los Angeles fylke.", seating, "Member seating chart, California State Assembly"),
        ("lawmaker-fran-pavley", "Lovhåndboken for 2013–14 oppgir Fran Pavley som senator for senatdistrikt 27.", handbook, "California Legislature handbook 2013-14"),
        ("lawmaker-bill-monning", "Lovhåndboken for 2013–14 oppgir William W. Monning som senator for senatdistrikt 17.", handbook, "California Legislature handbook 2013-14"),
        ("lawmaker-roger-dickinson", "Lovhåndboken for 2013–14 oppgir Roger Dickinson som representant for forsamlingsdistrikt 7.", handbook, "California Legislature handbook 2013-14"),
        ("lawmaker-cristina-garcia", "Lovhåndboken for 2013–14 oppgir Cristina Garcia som representant for forsamlingsdistrikt 58.", handbook, "California Legislature handbook 2013-14"),
    ):
        person = load(cid)
        add_claim(person, "r5-district", text, url, title, "California State Assembly")
        save(person)

    card = load("lawmaker-lena-gonzalez")
    set_summary(card, [
        ("Lena Gonzalez er senator for distrikt 33, som dekker deler av Los Angeles fylke, blant annet Long Beach. Hun la fram loven om avstand mellom oljebrønner og boliger.", ("s1", "s2", "s3")),
        ("Hun stemte ja da senatet vedtok den loven. Avstemningen var 25 mot 10.", ("s4",)),
        ("Distriktet dekker Southeast Los Angeles, Long Beach og havnen, ifølge hennes egen side.", ("s2",)),
    ])
    save(card)

    card = load("lawmaker-al-muratsuchi")
    set_summary(card, [
        ("Al Muratsuchi sitter i underhuset for distrikt 66 i Los Angeles fylke. Han la fram loven om luftmåling ved raffinerier.", ("r5-district", "s1")),
        ("Forsamlingen vedtok loven med 57 mot 19 i 2017.", ("s2",)),
        ("Han er også medforslagsstiller på loven om avstand mellom oljebrønner og boliger.", ("s3",)),
    ])
    save(card)

    card = load("lawmaker-fran-pavley")
    set_summary(card, [
        ("Fran Pavley var senator for distrikt 27 da grunnvannslovene ble vedtatt i 2014. Hun la fram to av lovene og stemte ja til den ene.", ("r5-district", "s1", "s3")),
        ("Hun var også medforslagsstiller på den tredje loven.", ("s2",)),
        ("Hun er med her som forfatter i 2014, ikke som sittende senator i 2026.", ("s4",)),
    ])
    save(card)

    card = load("lawmaker-roger-dickinson")
    set_summary(card, [
        ("Roger Dickinson satt i underhuset for distrikt 7 da grunnvannslovene ble vedtatt. Han la fram en av de tre lovene.", ("r5-district", "s1")),
        ("Forsamlingen vedtok loven med 47 mot 28. Hans egen stemme er ikke lest av fra stemmelisten.", ("s2",)),
        ("Den offisielle historikken sier at han la fram en av de andre grunnvannslovene for avstemning i underhuset.", ("c1",)),
    ])
    save(card)

    card = load("lawmaker-bill-monning")
    set_summary(card, [
        ("Bill Monning var senator for distrikt 17. Han la fram loven som opprettet fondet for trygt drikkevann.", ("r5-district", "s1")),
        ("Senatet vedtok loven med 38 mot 1.", ("s2",)),
        ("Han er med her som forfatter, ikke som sittende senator i 2026.", ("s4",)),
    ])
    save(card)

    card = load("lawmaker-cristina-garcia")
    set_summary(card, [
        ("Cristina Garcia satt i underhuset for distrikt 58 i Los Angeles fylke. Hun la fram loven om ekstra luftoppfølging i belastede nabolag.", ("r5-district", "s1")),
        ("Forsamlingen vedtok loven med 50 mot 24 i 2017.", ("s2",)),
        ("Vi har ikke sjekket om hun sitter i forsamlingen i 2026.", ("s3",)),
    ])
    save(card)


if __name__ == "__main__":
    main()
