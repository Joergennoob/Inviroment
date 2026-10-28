# Metoder for befolkning, demografi og helse

Oppdatert 2026-10-28. Tallene ligger på problemkortene. Dette notatet sier hvordan sammenligningen er laget, så den kan gjøres om igjen.

## Geografi

Hvert problem har to lag der kildene tillater det:

1. Etatens eget område og folketall, med årgang. Eksempel: EPA Green Book 2010 for et nonattainment-område, eller State Water Boards failing-liste per 31. desember 2024.
2. Ett navngitt census tract som eksempel inne i eller ved området. Traktet er ikke hele problemet.

CalEnviroScreen 4.0 bruker 2010-traktgrenser og ACS 2015–2019. ACS 5-år 2023 bruker 2020-traktgrenser. Der samme tract-id finnes i begge, er begge tallene tatt med og merket med årgang. Der data.census.gov svarer tomt for 2010-id-en i 2023-tabellen, er det logget. Det er ikke laget noen egen omkoding mellom årgangene.

Anleggstrakter i 9800-serien rundt raffinerier har 0 eller svært få beboere i ACS. De er ikke brukt som portrett av nabolaget.

## Demografi

Kilde er US Census Bureau, American Community Survey 5-år 2019–2023, hentet 2026-10-28 fra `https://data.census.gov/api/access/data/table` uten API-nøkkel. Tabeller:

| Mål | Tabell |
| --- | --- |
| Folketall | B01003 |
| Median husholdningsinntekt | B19013 |
| Fattigdom | B17001, andel B17001_002E / B17001_001E |
| Utdanning 25 år og eldre | B15003. Uten videregående: sum av B15003_002E–B15003_016E delt på B15003_001E. Bachelor eller høyere: B15003_022E–B15003_025E delt på samme nevner |
| Språklig isolasjon | C16002. (C16002_004E + 007E + 010E + 013E) / C16002_001E |
| Alder | B01001. Under 5 år: (B01001_003E + B01001_027E) / B01001_001E. 65 år og eldre: B01001_020E–025E og 044E–049E delt på B01001_001E |
| Etnisk fordeling | B03002. Hispanic: B03002_012E. Ikke-hispanic hvit: B03002_003E. Svart: B03002_004E. Asiatisk: B03002_006E. Alle delt på B03002_001E |
| Uten helseforsikring | S2701, felt S2701_C05_001E |

Boligbyrde er ikke regnet på nytt fra ACS i denne runden. Den er tatt fra CalEnviroScreen 4.0-indikatoren housing burden, som OEHHA bygger på ACS/CHAS for 2015–2019. Rapporten er `calenviroscreen40reportf2021.pdf`.

Sammenligningsgruppen for ACS er hele California i samme tabell og samme årgang. Et avvik er kalt merkbart bare hvis andelen er minst 1,5 ganger delstatens, minst 10 prosentpoeng høyere, eller inntekten er høyst to tredeler av delstatens median. Lavere utdanning enn delstaten bruker samme 1,5-regel på andelen uten videregående.

## Helse

CalEnviroScreen 4.0 rangerer hvert trakt mot alle census tracts i California. Persentil 90 betyr at trakten ligger i den tidelen med høyest indikatorverdi. Terskelen for «merkbart» i dette depotet er persentil 90 eller høyere.

Indikatorene, slik OEHHA beskriver dem i rapporten:

- Astma: aldersjusterte akuttmottakbesøk per 10 000, fra sporingsprogrammet til CDPH. Aldersjusteringen bruker 2000 US Standard Population.
- Hjerte- og karsykdom: akuttmottak for hjerteinfarkt, aldersjustert.
- Lav fødselsvekt: andel levendefødte under 2 500 gram.

Persentilen sier at trakten skiller seg fra det typiske California-traktet. Den sier ikke at miljøproblemet er årsaken. Inntekt, røyking og yrke er ikke justert bort. Der en etat eller en studie i CalEnviroScreen-rapporten sier at et stoff kan utløse anfall eller henger sammen med fødselsvekt, er det sitert som det studien sier, ikke som en årsak for akkurat dette trakten.

CDC PLACES, NCI State Cancer Profiles, CDPH sin valley fever-rapport for 2022 og DPR Pesticide Illness Surveillance Program for 2022 er hentet inn. Tallene står på kortene. De er ikke brukt som bevis på at miljøproblemet er årsaken.

## CalGEM-brønner

Antall brønner i health protection zone er telt 2026-10-28 i CalGEM WellSTAR MapServer, lag 0, feltet `inHPZ`. Spørringen er `returnCountOnly` mot `https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/MapServer/0/query`. «Verified HPZ» er etatens egen kategori. Tjenesten har ikke folketall, boliger eller skoler.

## Egen beregning innenfor 3 200 fot

CalGEM har ikke publisert folk, boliger eller skoler innenfor 3 200 fot. `scripts/setback_3200.py` regner det selv og skriver `data/derived/setback_3200.json`.

- Brønner: WellSTAR, status Active eller Idle, ett punkt per API-nummer, koordinat i California. Pluggede brønner er utelatt.
- Folk og boligenheter: Census 2020, PL 94-171, geografisk header `cageo2020.pl`, summary level 750. En blokk teller med når det indre punktet ligger innenfor 3 200 fot. Avstanden er ekvirektangulær, 69,172 miles per breddegrad.
- Skoler: NCES EDGE, offentlige skoler 2023–24, `STATE='CA'`. CDE-filen `pubschls.txt` ga en omdirigeringsløkke og er ikke brukt. Private skoler er ikke med.
- Et 2020-tract er merket når minst én bebodd blokk i tracten ligger innenfor avstanden. Tractet er videre enn bufferen og er bare brukt til PLACES-sammenligningen.

Samme skript regner også 1 engelsk mil rundt punktene for El Segundo, Torrance og Wilmington, og 5 engelske mil rundt FRS-punktet for Aliso Canyon. Radiene er valgt her.

## Område mot resten av California

`scripts/area_health.py` skriver `data/derived/area_health.json`.

CDC PLACES, GIS-vennlig tract-fil `yjkw-uj5s`, 2025-utgivelse, er rå prevalens blant voksne for 2023: nåværende astma, KOLS, koronar hjertesykdom, kreft unntatt hudkreft, og diagnostisert diabetes. Vekten er feltet `totalpopulation` fra Census 2020. Filen har ikke aldersjustert prevalens. Et modellestimat fra BRFSS er ikke en telling av diagnoser, og CDC advarer mot å bruke PLACES til å vurdere lokale tiltak.

CalEnviroScreen 4.0 er vektet med `ACS2019TotalPop`. Den brukes bare der området er fylker, fordi 2010-tract ikke er koblet til 2020-tract.

Fylkesutvalg, med forbeholdet på kortet:

- South Coast: Los Angeles, Orange, Riverside og San Bernardino. Luftbassenget er mindre.
- San Joaquin-luft og grunnvann: San Joaquin, Stanislaus, Merced, Madera, Fresno, Tulare, Kings og hele Kern. Øst-Kern og bassenggrensene er ikke skilt ut.
- Sprøytemidler: Fresno, Kern, Tulare og Monterey, de fire fylkene med flest pund i DPR 2022.
- Salton Sea: Imperial County. Nordbredden i Riverside er utenfor.
- Drikkevann: en tract-liste for failing-systemene er ikke funnet. Snittet er ikke laget.
- PFAS: ordren er delstatsdekkende. Kilde-listen er telt, men ikke geokodet til tract.

Kreftinsidens er NCI State Cancer Profiles, alle kreftformer, begge kjønn, aldersjustert til 2000 US standard population, 2019–2023, hentet 2026-10-28. Det er NCIs tabell, ikke en eksport fra CAL*Explorer. Valley fever er CDPH sin epidemiologiske rapport for 2022. PISP er DPR sin fylkestabell for 2022. Rater per 100 000 for PISP er vår divisjon med Census 2020-folketall fra PLACES, og året for teller og nevner er ikke det samme.
