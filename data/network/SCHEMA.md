# Nettverksskjema

Versjon `1.0.0`. Filene er `nodes.json` og `edges.json`.

Dette er ikke kortskjemaet i `schema/card.schema.json`. En node kan peke på et kort med `card_id`. Mangler kortet, er `card_id` tom.

## Node

`id`, `type`, `name`, `card_id`, `problems`, `detail`, `sources`.

`type` er `problem`, `organization`, `lobbying_firm`, `lobbyist`, `politician`, `bill` eller `proceeding`.

`problems` er id-er til problemkortene noden er knyttet til.

Lobbyistnoden har i tillegg `firm_id`, `firm_name` og `clients`. `clients` er oppdragsgiverne firmaet er registrert for i sesjonen. Det er ikke et bevis for at personen arbeidet med hver sak.

## Kant

`id`, `type`, `from`, `to`, `status`, `note`, `detail`, `sources`.

`status` er `confirmed`, `indication`, `not_found` eller `not_verified`. `indication` krever `note`.

`sources` har samme felt som kortene: `url`, `title`, `publisher`, `retrieved`, `archive_url`, `archive_note`.

| type | Betydning |
| --- | --- |
| `employed_by` | Lobbyist er registrert på firmaet eller hos oppdragsgiveren |
| `represents` | Firmaet er registrert for oppdragsgiveren |
| `firm_roster` | Lobbyisten sitter på et firma som er registrert for oppdragsgiveren. Det er en registrering, ikke en personlig saksliste |
| `contributed_to` | Oppdragsgiveren har ført et bidrag til komiteen på skjema 635 |
| `voted_on` | Navnet står på en navngitt avstemning |
| `stated` | Et offisielt nettsted gjengir en uttalelse |
| `relates_to` | Lovforslagets tittel på stemmesiden knytter det til problemet |
| `lobbied_on` | Et innlevert skjema nevner saken. Posisjon bare der skjemaet sier det |

Bidrag er sammenfall i tid. Skjemaet sier ikke at pengene endret en stemme.

## Kilde for koblingene

Sesjon 2025 i `FILER_LINKS_CD` i Secretary of State sitt rådata-uttrekk `dbwebexport.zip`, hentet 2026-10-28. Aktive rader har `ACTIVE_FLG` Y og tom `TERMINATION_DT`.

Retningen er lest slik, og sjekket mot kjente filer-id-er:

- `12004`: A er firma, B er oppdragsgiver. Kodeordet i `LOOKUP_CODES_CD` er «CLIENT (WHO IS AN EMPLOYER) OF A FIRM».
- `12008`: A er firma, B er lobbyist. Kodeordet er «LOBBYIST OF A FIRM». A treffer de samme firma-id-ene som i 12004.
- `12002`: A er oppdragsgiver, B er intern lobbyist. Kodeordet er «IN-HOUSE LOBBYIST OF AN EMPLOYER».

Navnet er siste rad i `FILERNAME_CD` for filer-id-en, etter ikrafttredelsesdato. En gammel navnestreng kan derfor henge igjen. Den er ikke rettet mot et nyere handelsnavn med mindre et skjema selv bruker det nyere navnet.
