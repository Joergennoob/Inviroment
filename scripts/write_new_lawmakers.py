#!/usr/bin/env python3
"""Write plain-language lawmaker cards and district polygons for people in the vote tables."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"
LAYER = ROOT / "public" / "data" / "layers" / "districts.geojson"
SLDU = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/5/query"
SLDL = "https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Legislative/MapServer/6/query"
DAY = "2026-10-28"
HANDBOOK = "https://www.senate.ca.gov/system/files/2026-09/joint_handbook_2025-26_web_1.pdf"

ARCH = {
    "sb1137": "http://web.archive.org/web/20250920054954/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220SB1137",
    "ab1864": "http://web.archive.org/web/20260117220802/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240AB1864",
    "ab3233": "http://web.archive.org/web/20250918105303/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240AB3233",
    "ab617": "http://web.archive.org/web/20250531134318/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201720180AB617",
    "sb200": "http://web.archive.org/web/20250529021927/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201920200SB200",
    "ab1647": "http://web.archive.org/web/20250919093406/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201720180AB1647",
    "sb1168": "http://web.archive.org/web/20250314163210/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201320140SB1168",
    "abx2": "http://web.archive.org/web/20260308020621/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320242AB1",
    "sb1486": "http://web.archive.org/web/20250918170037/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220SB1486",
    "sb305": "http://web.archive.org/web/20260118213538/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202320240SB305",
    "sb1044": "http://web.archive.org/web/20250918223637/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201920200SB1044",
    "ab1817": "http://web.archive.org/web/20250525034750/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=202120220AB1817",
    "sb380": "http://web.archive.org/web/20250923160035/https://leginfo.legislature.ca.gov/faces/billVotesClient.xhtml?bill_id=201520160SB380",
}
LIVE = {}
for key, archive in ARCH.items():
    marker = archive.find("https://leginfo")
    if marker < 0:
        marker = archive.find("http://leginfo")
    LIVE[key] = archive[marker:]

ZIP = "https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip"
ZIP_A = "http://web.archive.org/web/20260930110449/https://campaignfinance.cdn.sos.ca.gov/dbwebexport.zip"
GROVE = "https://sr12.senate.ca.gov/content/senator-grove-reacts-signing-senate-bill-1137"
GONZ = "https://sd33.senate.ca.gov/news/senator-gonzalez-and-senator-limons-historic-bill-end-neighborhood-oil-and-gas-drilling-signed"
STERN = "https://sd27.senate.ca.gov/news/sen-stern-asm-schiavo-look-expedite-closure-aliso-canyon-discounts-energy-upgrades-san"


def src_hand():
    return src(HANDBOOK, "California Legislature Handbook 2025-26", "California State Senate", "", "PDF-en er lest 2026-10-28. Wayback er ikke slått opp.")


def src_vote(key):
    return src(LIVE[key], f"Stemmeliste {key}", "California Legislative Counsel", ARCH[key], "Leginfo svarte 403 direkte. Listen er lest i arkivet.")


def src_money():
    return src(ZIP, "CAL-ACCESS LCCM_CD, uttrekk 28. oktober 2026", "California Secretary of State", ZIP_A, "Gaven er en rad i tabellen, koblet til giveren via regnskapsforsiden.")


def src(url, title, publisher, archive, note):
    return {"url": url, "title": title, "publisher": publisher, "retrieved": DAY, "archive_url": archive, "archive_note": note}


def claim(cid, text, status, sources, note=""):
    return {"id": cid, "text": text, "status": status, "note": note, "sources": sources}


def empty(field, searched):
    return {"field": field, "searched": searched, "result": "not_found", "urls": [HANDBOOK], "retrieved": DAY}


def fetch(layer, code):
    url = SLDU if layer == "sldu" else SLDL
    field = "SLDU" if layer == "sldu" else "SLDL"
    query = urllib.parse.urlencode({
        "where": f"STATE='06' AND {field}='{code}'",
        "outFields": f"GEOID,{field}",
        "returnGeometry": "true",
        "outSR": "4326",
        "maxAllowableOffset": "0.02",
        "geometryPrecision": "4",
        "f": "json",
    })
    request = urllib.request.Request(url + "?" + query, headers={"User-Agent": "InviromentResearch/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = json.loads(response.read().decode())
    rings = []
    geoid = code
    for feature in payload.get("features") or []:
        geoid = str(feature["attributes"].get("GEOID") or code)
        for ring in feature["geometry"]["rings"]:
            if ring[0] != ring[-1]:
                ring = ring + [ring[0]]
            rings.append([[round(x, 4), round(y, 4)] for x, y in ring])
    if not rings:
        raise SystemExit(f"no geometry {code}")
    geometry = {"type": "Polygon", "coordinates": rings}
    return geometry, geoid, url.split("?")[0]


# id, name, party, where, service, layer, code, map label, sentences (sid, text, source keys), links, questions
# source keys: h, money, grove, gonz, stern, or a vote key
PEOPLE = [
    ("lawmaker-shannon-grove", "Shannon Grove", "republikaner",
     "Hun er senator for et område med deler av Fresno, Kern og Tulare.",
     "Hun satt i forsamlingen fra desember 2010 til 2016, og i senatet fra desember 2018.",
     "sldu", "012", "SD 12",
     [("s2", "Da senatet vedtok loven om avstand mellom oljebrønner og hus, stemte hun nei. Det var 25 ja og 10 nei.", ["sb1137"]),
      ("s3", "Dagen loven ble signert, skrev kontoret hennes at loven ville stanse mange brønner.", ["grove"]),
      ("s4", "Ni dager før nei-stemmen ga oljeselskapet California Resources 4 900 dollar til valgkampen hennes. Det viser rekkefølgen. Det viser ikke at pengene styrte stemmen.", ["money", "sb1137"]),
      ("s5", "I 2014 stemte etternavnet Grove nei til de tre lovene om grunnvann. Fornavnet står ikke på listen. Håndboken sier at hun satt i forsamlingen da.", ["sb1168", "h"])],
     [("problem", "ca-problem-oil-gas-proximity", "Hun stemte nei til avstand fra oljebrønner."),
      ("problem", "ca-problem-groundwater-overdraft", "Etternavnet Grove stemte nei i 2014."),
      ("bill", "bill-sb-1137", "Nei-stemmen."),
      ("organization", "org-crc", "Gaven ni dager før.")],
     ["Om maiteksten i oljeloven var den samme som den endelige."]),
    ("lawmaker-melissa-hurtado", "Melissa Hurtado", "demokrat",
     "Hun er senator for et område med deler av Fresno, Kern, Kings og Tulare.",
     "Hun ble valgt i 2018 og tatt i ed i desember 2018.",
     "sldu", "016", "SD 16",
     [("s2", "Hun stemte nei da senatet vedtok loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten, og sto som den som la saken fram i senatet.", ["ab1864"]),
      ("s4", "Oljeselskapet California Resources ga 2 500 dollar til valgkampen hennes ni dager før nei-stemmen om oljebrønner. Phillips 66 ga 5 900 dollar i mars 2026, etterpå.", ["money"])],
     [("problem", "ca-problem-oil-gas-proximity", "Nei til avstandsloven."),
      ("problem", "ca-problem-pesticides", "Ja til varsling ved skoler."),
      ("bill", "bill-sb-1137", "Nei-stemmen."),
      ("organization", "org-crc", "Gaven før olje-stemmen.")],
     ["Vi fant ingen melding der hun forklarer nei-stemmen om olje."]),
    ("lawmaker-monique-limon", "Monique Limón", "demokrat",
     "Hun er senator for et område med San Luis Obispo, Santa Barbara og Ventura.",
     "Håndboken fører henne som senator for distrikt 21.",
     "sldu", "021", "SD 21",
     [("s2", "Hun stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Dagen loven ble signert, sa hun at hun var stolt av å ha stått sammen med Lena Gonzalez. Sitatet står på Gonzalez sin side.", ["gonz"]),
      ("s4", "Hun stemte også ja til varsling når det sprøytes nær skoler.", ["ab1864"])],
     [("problem", "ca-problem-oil-gas-proximity", "Ja, og hun var medforfatter."),
      ("bill", "bill-sb-1137", "Ja-stemmen."),
      ("lawmaker", "lawmaker-lena-gonzalez", "De la fram loven sammen.")],
     []),
    ("lawmaker-henry-stern", "Henry Stern", "demokrat",
     "Han er senator for et område i Los Angeles og Ventura, der gasslageret Aliso Canyon ligger.",
     "Håndboken sier at han har sittet siden desember 2016.",
     "sldu", "027", "SD 27",
     [("s2", "I desember 2024 sa han at gasslageret bør stenges, og at en plan om å bruke det til 2039 er feil.", ["stern"]),
      ("s3", "I 2022 falt et forslag han hadde lagt fram, med 5 ja og 12 nei. Hans eget navn står på nei-listen. Vi har ikke et referat som forklarer hvorfor.", ["sb1486"]),
      ("s4", "Året etter stemte han ja til et fond etter lekkasjen. Hele senatet stemte ja.", ["sb305"])],
     [("problem", "ca-problem-aliso-canyon", "Han vil stenge lageret."),
      ("problem", "ca-problem-oil-gas-proximity", "Han stemte ja til avstand fra oljebrønner.")],
     ["Hvorfor han stemte nei til sitt eget forslag i 2022."]),
    ("lawmaker-benjamin-allen", "Benjamin Allen", "demokrat",
     "Han er senator for et område i Los Angeles. Kontoret i distriktet ligger i El Segundo, ved et raffineri.",
     "Håndboken fører ham som senator for distrikt 24.",
     "sldu", "024", "SD 24",
     [("s2", "Han la fram loven som begrenser brannskum med PFAS, og stemte ja. Senatet var nesten enstemmig.", ["sb1044"]),
      ("s3", "Han stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s4", "Han stemte ja til loven om å ha mer drivstoff på lager ved raffineriene.", ["abx2"])],
     [("problem", "ca-problem-pfas", "Loven om brannskum."),
      ("problem", "ca-problem-refineries", "Ja til drivstofflager."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja til avstand fra brønner.")],
     []),
    ("lawmaker-heath-flora", "Heath Flora", "republikaner",
     "Han sitter i forsamlingen for et område med deler av San Joaquin, Stanislaus og nabofylker.",
     "Håndboken sier at han har sittet siden desember 2016.",
     "sldl", "009", "AD 9",
     [("s2", "Han stemte nei til loven som gir lokalsamfunn mer å si om skitten luft.", ["ab617"]),
      ("s3", "Han stemte nei til å måle luft ved gjerdet rundt raffinerier.", ["ab1647"]),
      ("s4", "Før nei-stemmen om oljebrønner i 2022 ga Marathon, California Resources og Berry penger til valgkampen hans.", ["money"])],
     [("problem", "ca-problem-san-joaquin-air", "Nei til lokalsamfunn og luft."),
      ("problem", "ca-problem-refineries", "Nei til måling ved gjerdet."),
      ("bill", "bill-ab-617", "Nei-stemmen om luft."),
      ("bill", "bill-ab-1647", "Nei-stemmen om raffinerier.")],
     ["Vi fant ingen melding der han forklarer nei-stemmene."]),
    ("lawmaker-jasmeet-bains", "Jasmeet Kaur Bains", "demokrat",
     "Hun sitter i forsamlingen for Kern, der det bores mye olje.",
     "Håndboken sier at hun har sittet siden desember 2022.",
     "sldl", "035", "AD 35",
     [("s2", "Hun stemte nei til å la lokalsamfunn si mer om oljeboring.", ["ab3233"]),
      ("s3", "Hun stemte nei til loven om lager av drivstoff ved raffineriene.", ["abx2"]),
      ("s4", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"])],
     [("problem", "ca-problem-oil-gas-proximity", "Nei til lokal kontroll."),
      ("problem", "ca-problem-refineries", "Nei til drivstofflager."),
      ("problem", "ca-problem-pesticides", "Ja til varsling ved skoler.")],
     ["Vi fant ingen melding der hun forklarer nei-stemmene om olje. I gavelisten vi leste, står hun ikke som mottaker fra oljeselskapene."]),
    ("lawmaker-steve-padilla", "Steve Padilla", "demokrat",
     "Han er senator for et område der hele Imperial fylke ligger, rundt Salton Sea.",
     "Håndboken sier at han har sittet siden desember 2022.",
     "sldu", "018", "SD 18",
     [("s2", "Han stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"]),
      ("s3", "Han stemte ja til å la lokalsamfunn si mer om oljeboring.", ["ab3233"]),
      ("s4", "Han stemte ja til loven om lager av drivstoff ved raffineriene.", ["abx2"])],
     [("problem", "ca-problem-salton-sea", "Distriktet dekker Imperial."),
      ("problem", "ca-problem-pesticides", "Ja til varsling.")],
     ["Vi fant ikke en egen lov bare om Salton Sea med hans stemme."]),
    ("lawmaker-jeff-gonzalez", "Jeff Gonzalez", "republikaner",
     "Han sitter i forsamlingen for Imperial fylke og deler av Riverside og San Bernardino, ved Salton Sea.",
     "Håndboken fører ham som medlem for distrikt 36.",
     "sldl", "036", "AD 36",
     [("s2", "Han står ikke på stemmelistene fra sommeren 2024. De avstemningene var før han satt.", ["ab1864"]),
      ("s3", "Oljeselskapet Marathon ga 2 500 dollar til valgkampen hans 30. september 2024, og 4 000 dollar 24. mars 2026.", ["money"]),
      ("s4", "Vi har ingen stemme fra ham å legge ved siden av pengene, fordi han ikke satt da lovene vi leste ble vedtatt.", ["h"])],
     [("problem", "ca-problem-salton-sea", "Distriktet dekker Imperial."),
      ("organization", "org-marathon", "Gaver til valgkampen.")],
     ["Nøyaktig dato han avla ed."]),
    ("lawmaker-anna-caballero", "Anna M. Caballero", "demokrat",
     "Hun er senator for et område med deler av Fresno, Madera, Merced og Tulare.",
     "Håndboken sier at hun har vært i lovgiveren fra desember 2016.",
     "sldu", "014", "SD 14",
     [("s2", "Hun stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"]),
      ("s4", "Hun stemte ja til drikkevannsfondet i 2019.", ["sb200"])],
     [("problem", "ca-problem-san-joaquin-air", "Distriktet ligger i dalen."),
      ("problem", "ca-problem-drinking-water", "Ja til fondet."),
      ("bill", "bill-sb-200", "Ja-stemmen."),
      ("bill", "bill-sb-1137", "Ja til avstand fra brønner.")],
     ["Vi fant ingen pressemelding fra henne om disse lovene."]),
    ("lawmaker-pilar-schiavo", "Pilar Schiavo", "demokrat",
     "Hun sitter i forsamlingen for et område i Los Angeles som dekker Porter Ranch og Aliso Canyon.",
     "Håndboken sier at hun har sittet siden desember 2022.",
     "sldl", "040", "AD 40",
     [("s2", "I desember 2024 sa hun at gasslageret bør stenges. Sitatet står på senator Stern sin side.", ["stern"]),
      ("s3", "På den endelige avstemningen om lager av drivstoff stemte hun ikke.", ["abx2"]),
      ("s4", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"])],
     [("problem", "ca-problem-aliso-canyon", "Hun vil stenge lageret."),
      ("lawmaker", "lawmaker-henry-stern", "De uttalte seg sammen.")],
     []),
    ("lawmaker-lori-wilson", "Lori D. Wilson", "demokrat",
     "Hun sitter i forsamlingen for et område med deler av Contra Costa og Solano, der det ligger raffinerier.",
     "Håndboken sier at hun har sittet siden april 2022.",
     "sldl", "011", "AD 11",
     [("s2", "Hun stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Oljeselskapet Marathon ga 2 000 dollar til valgkampen hennes i mars 2022, før ja-stemmen.", ["money"]),
      ("s4", "Hun stemte ja til loven om lager av drivstoff ved raffineriene.", ["abx2"])],
     [("problem", "ca-problem-oil-gas-proximity", "Ja, selv etter en gave fra Marathon."),
      ("problem", "ca-problem-refineries", "Ja til drivstofflager."),
      ("organization", "org-marathon", "Gaven før ja-stemmen.")],
     []),
    ("lawmaker-esmeralda-soria", "Esmeralda Z. Soria", "demokrat",
     "Hun sitter i forsamlingen for deler av Fresno, Madera og Merced.",
     "Håndboken sier at hun har sittet siden desember 2022.",
     "sldl", "027", "AD 27",
     [("s2", "Hun stemte nei til loven om lager av drivstoff ved raffineriene.", ["abx2"]),
      ("s3", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"]),
      ("s4", "California Resources ga 5 500 dollar til valgkampen hennes 28. august 2024, før nei-stemmen om drivstoff i oktober.", ["money"])],
     [("problem", "ca-problem-pesticides", "Ja til varsling."),
      ("problem", "ca-problem-refineries", "Nei til drivstofflager."),
      ("organization", "org-crc", "Gaven i august 2024.")],
     ["Vi fant ingen melding der hun forklarer nei-stemmen om drivstoff."]),
    ("lawmaker-john-laird", "John Laird", "demokrat",
     "Han er senator for Monterey, San Benito, Santa Cruz og deler av San Luis Obispo.",
     "Håndboken fører ham som senator for distrikt 17.",
     "sldu", "017", "SD 17",
     [("s2", "Han la fram den endelige avstemningen om lokal kontroll med olje i senatet, og stemte ja.", ["ab3233"]),
      ("s3", "Han stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s4", "Han stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"])],
     [("problem", "ca-problem-oil-gas-proximity", "Ja til avstand og til lokal kontroll."),
      ("problem", "ca-problem-pesticides", "Ja til varsling."),
      ("bill", "bill-sb-1137", "Ja-stemmen.")],
     []),
    ("lawmaker-damon-connolly", "Damon Connolly", "demokrat",
     "Han sitter i forsamlingen for Marin og deler av San Francisco og Sonoma.",
     "Håndboken sier at han har sittet siden desember 2022.",
     "sldl", "012", "AD 12",
     [("s2", "Han la fram loven om å varsle når det sprøytes nær skoler, og stemte ja.", ["ab1864"]),
      ("s3", "Han stemte ja til loven om lager av drivstoff ved raffineriene.", ["abx2"]),
      ("s4", "Han stemte ja til å la lokalsamfunn si mer om oljeboring.", ["ab3233"])],
     [("problem", "ca-problem-pesticides", "Han la fram varslingsloven."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja til lokal kontroll.")],
     []),
    ("lawmaker-joaquin-arambula", "Joaquin Arambula", "demokrat",
     "Han sitter i forsamlingen for deler av Fresno.",
     "Håndboken sier at han har sittet siden april 2016.",
     "sldl", "031", "AD 31",
     [("s2", "Han stemte ja til loven som gir lokalsamfunn mer å si om skitten luft.", ["ab617"]),
      ("s3", "På den endelige avstemningen om måling ved raffinerigjerdet stemte han ikke.", ["ab1647"]),
      ("s4", "På oljeloven i 2022 stemte han ikke.", ["sb1137"])],
     [("problem", "ca-problem-san-joaquin-air", "Ja til loven om lokal luft."),
      ("bill", "bill-ab-617", "Ja-stemmen."),
      ("problem", "ca-problem-drinking-water", "Distriktet ligger i dalen.")],
     ["Vi fant ingen melding som forklarer hvorfor han ikke stemte om oljebrønnene."]),
    ("lawmaker-suzette-valladares", "Suzette Martinez Valladares", "republikaner",
     "Hun er senator for et område i Los Angeles og San Bernardino.",
     "Hun satt i forsamlingen fra desember 2020 til 2022, og i senatet fra desember 2024.",
     "sldu", "023", "SD 23",
     [("s2", "I august 2022, da hun satt i forsamlingen, stemte hun nei til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Åtte dager før ga California Resources 3 000 dollar til valgkampen hennes.", ["money"]),
      ("s4", "Hun stemte ja til å begrense PFAS i tekstiler.", ["ab1817"])],
     [("problem", "ca-problem-oil-gas-proximity", "Nei til avstandsloven."),
      ("problem", "ca-problem-pfas", "Ja til tekstil-loven."),
      ("organization", "org-crc", "Gaven før nei-stemmen.")],
     []),
    ("lawmaker-rosilicie-ochoa-bogh", "Rosilicie Ochoa Bogh", "republikaner",
     "Hun er senator for deler av Riverside og San Bernardino.",
     "Håndboken sier at hun har sittet siden desember 2020.",
     "sldu", "019", "SD 19",
     [("s2", "Hun stemte nei til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "California Resources ga 4 900 dollar til en valgkampkomité i hennes navn 22. august 2022, ni dager før.", ["money"]),
      ("s4", "Hun stemte nei til loven om lager av drivstoff.", ["abx2"])],
     [("problem", "ca-problem-oil-gas-proximity", "Nei til avstandsloven."),
      ("problem", "ca-problem-south-coast-air", "Distriktet ligger i luftbassenget i sør."),
      ("organization", "org-crc", "Gaven før nei-stemmen.")],
     ["Vi fant ingen melding der hun forklarer nei-stemmen."]),
    ("lawmaker-tim-grayson", "Tim Grayson", "demokrat",
     "Han er nå senator for deler av Contra Costa og Alameda. Før desember 2024 satt han i forsamlingen.",
     "Håndboken sier at han har vært i lovgiveren siden desember 2016.",
     "sldu", "009", "SD 9",
     [("s2", "På oljeloven i august 2022 stemte han ikke. Han satt da i forsamlingen.", ["sb1137"]),
      ("s3", "California Resources ga 4 900 dollar til valgkampen hans 22. august 2022, like før den avstemningen.", ["money"]),
      ("s4", "På loven om lager av drivstoff i oktober 2024 stemte han ikke.", ["abx2"])],
     [("problem", "ca-problem-refineries", "Distriktet ligger ved raffinerier øst for bukta."),
      ("problem", "ca-problem-oil-gas-proximity", "Han stemte ikke."),
      ("organization", "org-crc", "Gaven like før.")],
     ["Kartet viser senatdistriktet han har nå, ikke forsamlingsdistriktet han stemte fra i 2022."]),
    ("lawmaker-marie-alvarado-gil", "Marie Alvarado-Gil", "republikaner",
     "Hun er senator for et stort område med blant annet Stanislaus, Merced og fjellfylkene.",
     "Håndboken sier at hun har sittet siden desember 2022. Der står hun som republikaner.",
     "sldu", "004", "SD 4",
     [("s2", "Hun stemte nei til å la lokalsamfunn si mer om oljeboring.", ["ab3233"]),
      ("s3", "Hun stemte nei til loven om lager av drivstoff.", ["abx2"]),
      ("s4", "Valero ga 3 000 dollar til valgkampen hennes 13. februar 2023, før disse stemmene i 2024.", ["money"])],
     [("problem", "ca-problem-groundwater-overdraft", "Distriktet dekker dal og fjell med grunnvann."),
      ("problem", "ca-problem-oil-gas-proximity", "Nei til lokal kontroll."),
      ("organization", "org-valero", "Gaven i 2023.")],
     []),
    ("lawmaker-buffy-wicks", "Buffy Wicks", "demokrat",
     "Hun sitter i forsamlingen for deler av Alameda og Contra Costa, ved raffineriene øst for bukta.",
     "Håndboken sier at hun har sittet siden desember 2018.",
     "sldl", "014", "AD 14",
     [("s2", "Hun stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Hun stemte ja til loven om lager av drivstoff ved raffineriene.", ["abx2"]),
      ("s4", "I uttrekket av gaver fra oljeselskapene vi søkte, står ikke navnet hennes.", ["money"])],
     [("problem", "ca-problem-refineries", "Ja til drivstofflager."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja til avstand fra brønner."),
      ("bill", "bill-sb-1137", "Ja-stemmen.")],
     []),
    ("lawmaker-steve-bennett", "Steve Bennett", "demokrat",
     "Han sitter i forsamlingen for Ventura.",
     "Håndboken fører ham som medlem for distrikt 38.",
     "sldl", "038", "AD 38",
     [("s2", "Han stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Han stemte ja til loven om lager av drivstoff.", ["abx2"]),
      ("s4", "Han stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"])],
     [("problem", "ca-problem-oil-gas-proximity", "Ja til avstandsloven."),
      ("bill", "bill-sb-1137", "Ja-stemmen.")],
     []),
    ("lawmaker-mike-gipson", "Mike A. Gipson", "demokrat",
     "Han sitter i forsamlingen for et område sør i Los Angeles, nær havn og raffineri.",
     "Håndboken sier at han har sittet siden desember 2014.",
     "sldl", "065", "AD 65",
     [("s2", "Han stemte ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Marathon ga 3 500 dollar til valgkampen hans 26. september 2024, altså etter ja-stemmen i 2022.", ["money"]),
      ("s4", "På den endelige avstemningen om lokal kontroll med olje i 2024 stemte han ikke.", ["ab3233"])],
     [("problem", "ca-problem-refineries", "Distriktet ligger ved havn og raffineri."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja i 2022."),
      ("organization", "org-marathon", "Gaven kom etter 2022-stemmen.")],
     []),
    ("lawmaker-eloise-gomez-reyes", "Eloise Gómez Reyes", "demokrat",
     "Hun er senator for San Bernardino. Før desember 2024 satt hun i forsamlingen.",
     "Håndboken sier at hun var i lovgiveren fra desember 2016, og senator fra desember 2024.",
     "sldu", "029", "SD 29",
     [("s2", "I 2022, da hun satt i forsamlingen, stemte hun ja til loven om avstand mellom oljebrønner og hus.", ["sb1137"]),
      ("s3", "Hun stemte ja til loven om lager av drivstoff i oktober 2024.", ["abx2"]),
      ("s4", "Hun stemte ja til loven om lokal luft i 2017.", ["ab617"])],
     [("problem", "ca-problem-south-coast-air", "Distriktet ligger i sør."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja til avstandsloven."),
      ("bill", "bill-ab-617", "Ja i 2017.")],
     ["Kartet viser senatdistriktet hun har nå, ikke forsamlingsdistriktet hun stemte fra."]),
    ("lawmaker-caroline-menjivar", "Caroline Menjivar", "demokrat",
     "Hun er senator for Burbank og San Fernando-dalen i Los Angeles.",
     "Håndboken sier at hun har sittet siden desember 2022.",
     "sldu", "020", "SD 20",
     [("s2", "Hun stemte ja til å varsle skoler når det sprøytes i nærheten.", ["ab1864"]),
      ("s3", "På loven om lager av drivstoff stemte hun ikke.", ["abx2"]),
      ("s4", "Hun stemte ja til å la lokalsamfunn si mer om oljeboring.", ["ab3233"])],
     [("problem", "ca-problem-pesticides", "Ja til varsling."),
      ("problem", "ca-problem-oil-gas-proximity", "Ja til lokal kontroll.")],
     []),
]


def sources_for(keys):
    out = []
    for key in keys:
        if key == "h":
            out.append(src_hand())
        elif key == "money":
            out.append(src_money())
        elif key == "grove":
            out.append(src(GROVE, "Grove om signeringen av SB 1137", "Kontoret til Shannon Grove", "", "Siden er lest 2026-10-28."))
        elif key == "gonz":
            out.append(src(GONZ, "Signering av SB 1137, sitat fra Limón", "Kontoret til Lena Gonzalez", "", "Siden er lest 2026-10-28."))
        elif key == "stern":
            out.append(src(STERN, "Stern og Schiavo om Aliso Canyon", "Kontoret til Henry Stern", "", "Siden er lest 2026-10-28."))
        else:
            out.append(src_vote(key))
    return out


def main() -> None:
    layer = json.loads(LAYER.read_text(encoding="utf-8"))
    have = {feature["properties"]["card_id"] for feature in layer["features"]}
    for person in PEOPLE:
        pid, name, party, where, service, layer_name, code, label, sentences, links, questions = person
        base, geoid, url = fetch(layer_name, code)
        note = f"Valgkretsen {label} fra folketellingen i 2024. Det er området personen representerer, ikke området med forurensning."
        geometry = {
            **base,
            "source_name": "US Census TIGERweb 2024",
            "source_record_id": geoid,
            "source_url": url,
            "retrieved": DAY,
            "note": note,
        }
        summary = [claim("s1", f"{name} er {party}. {where} {service}", "confirmed", [src_hand()])]
        for sid, text, keys in sentences:
            summary.append(claim(sid, text, "confirmed", sources_for(keys)))
        if not 3 <= len(summary) <= 5:
            raise SystemExit(f"{pid} summary {len(summary)}")
        card = {
            "schema_version": "1.0.0",
            "id": pid,
            "type": "lawmaker",
            "name": name,
            "state": "CA",
            "updated": DAY,
            "rank": None,
            "org_kind": None,
            "summary": summary,
            "claims": [claim("c1", "Tallene og datoene står i stemmelisten og i håndboken. Sammendraget over er de samme faktaene med vanlige ord.", "confirmed", [src_hand()])],
            "links": [{"rel": rel, "target_id": target, "text": text} for rel, target, text in links],
            "geometry": geometry,
            "map_features": [],
            "checked_empty": [empty("public_statement", "En egen pressemelding ut over den som er sitert i sammendraget, er ikke åpnet for denne personen i denne runden.")],
            "open_questions": questions,
        }
        (CARDS / f"{pid}.json").write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if pid not in have:
            layer["features"].append({
                "type": "Feature",
                "geometry": {"type": base["type"], "coordinates": base["coordinates"]},
                "properties": {
                    "card_id": pid,
                    "name": label,
                    "layer": "districts",
                    "source_name": "US Census TIGERweb 2024",
                    "source_record_id": geoid,
                    "source_url": url,
                    "source_retrieved": DAY,
                    "source_note": note,
                },
            })
        print("wrote", pid, geoid)
    LAYER.write_text(json.dumps(layer, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print("features", len(layer["features"]))


if __name__ == "__main__":
    main()
