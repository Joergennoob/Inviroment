# Miljøkart California

Åpent, kildebelagt kart over miljøproblemer i amerikanske delstater. Første innhold er California. Inngangen er stedet og skaden. Derfra går kortene til selskap, lobbyutgifter, kampanjebidrag, lovforslag, stemmetall og etater. Hver påstand har status og lenke.

Tekst til leseren er bokmål. Kode, filnavn og JSON-nøkler er engelsk ASCII.

## Reglene, kort

- Journalisten skal kunne sjekke påstanden uten å stole på oss. Hver påstand har URL, hentedato, arkivlenke der Internet Archive har en, og status `confirmed`, `indication`, `not_found` eller `not_verified`.
- Primærkilder først: Cal-Access, leginfo, CARB, CalGEM, State Water Board, OEHHA, DPR, DWR, EPA, SEC. Nyheter og organisasjoner brukes ikke som sitert kilde.
- Tomme søk skrives ned. Et sjekket nullfunn er et funn.
- Bare gratis kilder. Ingen hemmeligheter. Ingen kontakt med personer. Ingen sensitive personopplysninger.
- Nøytral ordlyd. Etatens egen kategori siteres, den utvides ikke.
- Kode er MIT. Kortdata er CC BY 4.0. Se RULES.md, LICENSE, LICENSE-DATA og ATTRIBUTION.md.

## Slik sjekker en journalist en påstand

1. Åpne kortet, i `data/cards/<id>.md` eller i kartet.
2. Les statusmerket. `Bekreftet` skal hvile på dokumentet lenken peker på.
3. Åpne kildelenken. Sammenlign setningen med dokumentet, ikke med dette sammendraget.
4. Hvis siden er endret, åpne arkivlenken.
5. Mangler arkivlenken, står grunnen i `archive_note`, som regel at Wayback og Save Page Now feilet den dagen.
6. Plassering har en egen linje, «Kilde for plassering», med etat og post-id. Et tract er ikke hele luftbassenget.

## Kjøre kartet

Krever Node.js 22 og npm.

```bash
npm install
npm run build
```

Bygget skriver et statisk nettsted til `out/`. Det kan legges på Vercel eller en hvilken som helst statisk vert. Det er ikke deployet herfra.

Lokalt, etter bygget:

```bash
npx --yes serve out
```

Utvikling: `npm run dev`, deretter http://localhost:3000.

Python 3.12, bare standardbiblioteket, for kortene:

```bash
python3 scripts/validate_cards.py
python3 scripts/render_markdown.py
python3 scripts/build_geojson.py
python3 scripts/coverage.py
python3 scripts/render_overview.py
```

`scripts/archive_sources.py` spør Wayback om kilder som mangler arkiv-URL. `scripts/write_cards.py` regenererer JSON-kortene fra forfatterskriptet og bør ikke kjøres hvis kortene er redigert for hånd etterpå.

GitHub Actions kjører validering, sjekk av genererte filer og `npm ci && npm run build`.

## Innhold

Rangeringen og begrunnelsen: `data/ca/oversikt.md`. Dekning, hva som er sjekket per kort: `data/coverage.md`. Skjema: `SCHEMA.md`.

Bakgrunnskartet er [OpenFreeMap](https://openfreemap.org/) (stil `liberty`), uten API-nøkkel. OpenStreetMap-attribusjon vises i kartet.
