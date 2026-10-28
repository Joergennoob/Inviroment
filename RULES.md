# Regler

Disse reglene gjelder alle kort og all tekst som påstår et faktum.

## Verifiserbart

En journalist skal kunne sjekke hvert faktum uten å stole på dette depotet. Hver påstand har:

- direkte URL til dokumentet eller registerposten, ikke bare forsiden til etaten
- datoen URL-en ble hentet (`YYYY-MM-DD`)
- en Wayback-URL når Internet Archive har eller tar imot et øyeblikksbilde
- status: `confirmed`, `indication`, `not_found` eller `not_verified`

`confirmed` krever en primærkilde, eller at to uavhengige kilder sier det samme. `indication` er en sekundær kilde eller et navnetreff, og feltet `note` skal si hvorfor det ikke er bekreftet og hvilken primærkilde som ville lukket det. `not_found` betyr at kilden er sjekket og svaret var tomt. `not_verified` betyr at påstanden er sett, men ikke ført tilbake til dokumentet som kan bære den.

## Primærkilder først

Foretrekk Cal-Access (California Secretary of State), leginfo.legislature.ca.gov, CARB, CalGEM, State Water Resources Control Board, OEHHA CalEnviroScreen, DPR, DWR, CARB, South Coast AQMD, EPA (Green Book, ECHO, FRS, TRI), EIA og SEC. Nyheter, interesseorganisasjoner og søkemotorutdrag kan brukes til å finne dokumentet. De skal ikke være den siterte kilden. Finnes påstanden bare der, sett `indication` eller `not_verified` og skriv hvilken primærkilde som mangler.

## Kart

Hvert kartobjekt har med seg hvor geometrien kommer fra: etat, post-id og URL. Et census tract er ikke grensen for et helt luftbasseng. Et raffineripunkt er ikke bassenget. Det skal stå i notatet.

## Tomme felt

Et tomt felt skal si hva som ble søkt. «Søkt i Cal-Access, ingen treff på navnet AERA i sesjon 2025-2026» er et funn. Å la feltet stå tomt uten søk er ikke lov.

## Åpne kilder

Bare gratis og åpne kilder. Ingen betalte API-er og ingen betalte modellkall i datainnsamlingen. Ingen hemmeligheter i depotet.

## Personer

Ikke ta kontakt med noen. Ikke ta med helse, religion, legning eller andre sensitive personopplysninger. Navn på folkevalgte og navnestrenger i offentlige bidragsregistre er med fordi de er offentlige registre. Ikke legg til biografi utover det siden selv sier, og ikke tolk et navn i parentes i en bidragsstreng som en rolle.

## Språk

Nøytralt. Beskriv det dokumentet sier. Ikke skriv at noen har gjort noe galt utover den kategorien etaten selv bruker, for eksempel EPAs «Significant Violation».

## Lisens

Kode er MIT. Kortdata er CC BY 4.0. Se LICENSE, LICENSE-DATA og ATTRIBUTION.md.
