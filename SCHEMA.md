# Kortskjema

Versjon `1.0.0`. Maskinlesbar kontrakt: `schema/card.schema.json`. Validering: `python3 scripts/validate_cards.py`.

Kode, filnavn og JSON-nøkler er ASCII. Teksten i kortene er norsk bokmål.

## Fil

`data/cards/<id>.json` og en generert `data/cards/<id>.md`. Id-en er små bokstaver og bindestrek, og den er filnavnet.

## Typer

| type | Bruk |
| --- | --- |
| problem | Et miljøproblem, med valgfri rang 1–10 og geometri |
| organization | Selskap, bransjeforening, etat eller vannverk. `org_kind` sier hvilken |
| lobbying_firm | Et lobbyfirma, ikke arbeidsgiveren som betaler |
| lawmaker | Folkevalgt, bare det lovsiden eller senatssiden sier |
| bill | Lovforslag med kapittel, stemmetall og forfatter |

## Påstand

Både `summary` (3–5 punkter) og `claims` er lister av:

```json
{
  "id": "s1",
  "text": "Setningen som kan sjekkes.",
  "status": "confirmed",
  "note": "",
  "sources": [
    {
      "url": "https://...",
      "title": "Dokumenttittel",
      "publisher": "US EPA",
      "retrieved": "2026-10-28",
      "archive_url": "https://web.archive.org/web/...",
      "archive_note": "Wayback availability fant et øyeblikksbilde."
    }
  ]
}
```

Status er `confirmed`, `indication`, `not_found` eller `not_verified`. `indication` krever `note`.

## Lenker

`links` peker på andre kort med `target_id`. Validatoren krever at målet finnes.

## Plassering

`geometry` er et GeoJSON-geometriobjekt pluss `source_name`, `source_record_id`, `source_url`, `retrieved` og `note`. `map_features` er det som tegnes. Mangler geometri på et problem, skal `checked_empty` ha feltet `geometry` og si hva som ble søkt.

## Tomme søk og åpne spørsmål

`checked_empty` er søk uten treff. `open_questions` er det som ikke ble nådd, skrevet som spørsmål, ikke som gjetning.

## Generert

`python3 scripts/render_markdown.py` skriver Markdown. `python3 scripts/build_geojson.py` skriver `public/data/map.geojson` og `public/data/cards.json`. `python3 scripts/coverage.py` skriver dekningstabellen. `python3 scripts/archive_sources.py` fyller Wayback-felt som er tomme.
