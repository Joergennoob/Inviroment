#!/usr/bin/env python3
"""Simpler summary lines. Sources on each line stay put."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "data" / "cards"

LINES: dict[str, list[str]] = {
    "ca-problem-south-coast-air": [
        "Luften rundt Los Angeles er for skitten. Den klarer ikke regelen for ren luft som USA har satt. Miljøtilsynet i USA regnet med om lag 16 millioner mennesker der i 2010. Mye av skitten kommer fra biler og store lastebiler. Fabrikker som lager bensin, kalt raffinerier, slipper også ut mye.",
        "Området har for mye fint støv. Det er de minste partiklene i luften, så små at du nesten ikke ser dem. Målingen ligger på 13,2. Området har også for mye ozon, en gass nede ved bakken som irriterer lungene.",
        "I 2018 kom 27 av 100 deler av en skitten eksosgass fra store lastebiler. Gassen kalles NOx, og den er med på å lage både det fine støvet og ozon. All trafikk på veiene sto for 44 av 100 deler.",
        "I ett nabolag i Los Angeles blir flere barn født for små enn i 90 av 100 nabolag i California. Vi vet ikke om luften er grunnen.",
        "Når vi ser på hele området rundt Los Angeles, er ikke astma eller kols vanligere enn i resten av California. Kols er en lungesykdom. Vi vet ikke om luften er grunnen der tallene likevel er annerledes.",
    ],
    "ca-problem-san-joaquin-air": [
        "I den lange jordbruksdalen fra Stockton til Bakersfield er luften den skitneste i USA, målt som fint støv. Fint støv er de minste partiklene, så små at du nesten ikke ser dem. Miljøtilsynet i USA regnet med om lag 4 millioner mennesker der i 2010. Dalen har bedt om mer tid, til slutten av 2030, for å klare grensen for ren luft.",
        "Området har for mye fint støv, og det klarer heller ikke en eldre grense for ozon, en gass som irriterer lungene. Støvet er verre enn rundt Los Angeles.",
        "Dalfeber, en sykdom man kan få av sopp i støv, er langt vanligere her. I Kern fylke ble om lag 14 ganger så mange syke, sett i forhold til folketallet, som i hele California i 2022.",
        "I selve området der luften er skitten, er det om lag halvannen gang så mange voksne uten videregående skole som i resten av California. Vi vet ikke om luften er grunnen.",
        "I ett nabolag i Fresno er legevaktbesøk for astma verre enn i 97 av 100 nabolag i California. For hele dalen er astma vanligere, men ikke dobbelt så vanlig. Vi vet ikke om luften er grunnen.",
    ],
    "ca-problem-drinking-water": [
        "Noen offentlige vannverk leverer vann som bryter reglene for helse. Ved utgangen av 2024 gjaldt det 390 verk og om lag 800 000 mennesker. De vanligste grunnene var arsen, et giftig stoff, et kjemikalie fra industri, og nitrat. Nitrat er et stoff fra gjødsel. Gjødsel er den største kilden til nitrat i vannet under bakken i de hardest rammede jordbruksdalene.",
        "Om lag 8 av 10 slike verk ligger i områder staten kaller økonomisk vanskeligstilte, altså steder der folk har lite penger. Halvparten ligger i områder der de fleste innbyggerne ikke er hvite.",
        "De aller fleste i California, 98 av 100, fikk likevel vann som holdt mål i 2024. Om lag 1,5 millioner mennesker var på verk som staten sier står i fare.",
        "En nyere liste fra oktober 2026 har 416 verk. Deres eget folketall er om lag 430 000. Det er ikke det samme tallet som 800 000 fra 2024, fordi listen endrer seg.",
        "Der verkene som bryter reglene ligger, er det flere uten videregående skole enn hos verk som holder mål. Vi vet ikke om vannet er grunnen.",
    ],
    "ca-problem-oil-gas-proximity": [
        "En lov fra 2022 sier at nye olje- og gassbrønner ikke skal bores nærmere enn om lag 1 kilometer fra boliger, skoler og andre steder der folk er ekstra sårbare. Oljetilsynet har ikke selv telt hvor mange som bor der. Vår egen telling gir om lag 3 millioner mennesker og om lag 1,1 millioner boliger.",
        "Om lag 700 offentlige skoler og om lag 200 private skoler ligger innenfor den avstanden.",
        "Kern fylke pumpet det aller meste av oljen i California i 2023. Chevron og Aera betalte de største avgiftene til oljetilsynet.",
        "Oljeselskapenes felles organisasjon brukte om lag 19 millioner dollar på å betale folk for å påvirke politikerne i denne toårsperioden.",
        "Sykdomstallene for nabolag nær brønner er ikke høyere enn i resten av California. Vi vet ikke om brønnene er grunnen.",
    ],
    "ca-problem-pesticides": [
        "I 2022 ble det sprøytet om lag 180 millioner pund av selve giften i sprøytemidlene i California. Ett pund er omtrent et halvt kilo. Mest gikk ut i jordbruksfylkene Fresno, Kern og Tulare. De som bor og jobber der, er nærmest sprøytingen.",
        "Fresno og Kern hadde hver over 25 millioner pund. Tulare hadde om lag 18 millioner og Monterey om lag 9 millioner.",
        "I ett nabolag i Fresno er legevaktbesøk for astma verre enn i 98 av 100 nabolag i California. Vi vet ikke om sprøytemidlene er grunnen.",
        "I de fire fylkene med mest sprøyting er det om lag halvannen gang så mange uten videregående skole som i resten av California. Vi vet ikke om sprøytingen er grunnen.",
        "Delstaten registrerte om lag 1 000 sykdomstilfeller som kan henge sammen med sprøytemidler i 2022. Los Angeles hadde flest, og de fleste der kom ikke fra jordbruk.",
    ],
    "ca-problem-salton-sea": [
        "Innsjøen Salton Sea krymper fordi vann som før rant dit, brukes andre steder. Tørr sjøbunn kan blåse opp som støv. Vannverket der flytter inntil en stor mengde vann i året, og det er det som legger bunnen bar.",
        "En målerapport sier at om lag 38 000 acre sjøbunn lå bart ved utgangen av 2024. En acre er et amerikansk flatemål. Delstatens egen årsrapport gir ikke ett samlet tall for den bare bunnen.",
        "Innenfor om lag en engelsk mil, det vil si om lag 1,6 kilometer, fra kanten av innsjøen bor om lag 12 000 mennesker. Det er mye færre enn hele Imperial fylke, der miljøtilsynet i USA regnet om lag 150 000 mennesker i 2010.",
        "I hele Imperial fylke er legevaktbesøk for astma om lag 1,7 ganger så høye som i resten av California, og flere voksne mangler videregående skole. Vi vet ikke om støvet er grunnen.",
        "Dalfeber, en sykdom man kan få av sopp i støv, er ikke vanligere i Imperial enn i California som helhet. I 2022 var andelen lavere der enn i delstaten.",
    ],
    "ca-problem-refineries": [
        "Raffinerier er fabrikker som lager bensin. De ligger tett på boliger i Los Angeles-området. En lov fra 2017 sier at eieren skal måle luften ved gjerdet, og at naboene skal kunne se tallene.",
        "Miljøtilsynet i USA kaller bruddene ved Chevron-raffineriet i El Segundo alvorlige.",
        "Phillips 66 kunngjorde i 2024 at raffineriet i Wilmington og Carson skulle stanse driften mot slutten av 2025. Selve stansen er beskrevet på selskapets eget kort.",
        "Torrance-raffineriet drives av Torrance Refining, et selskap PBF kjøpte i 2016.",
        "Innenfor en engelsk mil, om lag 1,6 kilometer, bor noen tusen mennesker ved hvert av de tre anleggene. Sykdomstallene der er ikke høyere enn i resten av California. Vi vet ikke om raffineriet er grunnen.",
    ],
    "ca-problem-aliso-canyon": [
        "I 2015 og 2016 lekket et stort gasslager over bydelen Porter Ranch i Los Angeles. Lageret eies av gasselskapet SoCalGas. Det er den største lekkasjen av metan som er dokumentert i USA. Metan er hovedstoffet i naturgass, og en gass som varmer opp kloden.",
        "Lekkasjen varte fra oktober 2015 til februar 2016. Utslippet var om lag 100 000 tonn metan.",
        "Mengden tilsvarer omtrent det 190 000 boliger i Los Angeles bruker av gass på ett år. Det er en sammenligning, ikke et tall på hvor mange som måtte flytte.",
        "Myndighetene lar lageret fortsatt holde om lag 69 milliarder kubikkfot gass. Kubikkfot er et amerikansk rommål. Et forslag om å senke taket er ikke vedtatt.",
        "Folk i boligområdet nærmest lageret tjener ganske godt, og de vanlige sykdomstallene der skiller seg ikke ut. Vi vet ikke om lekkasjen ga varig sykdom. Det er ikke målt i disse tallene.",
    ],
    "ca-problem-pfas": [
        "Evighetskjemikalier, kalt PFAS, er stoffer som nesten ikke brytes ned. De er brukt i blant annet brannskum og fabrikker, og kan havne i drikkevann. Delstaten har pålagt testing av brønner.",
        "Etaten selv sier om lag 3 600 til 4 000 brønner, ikke ett fast tall. En liste fra oktober 2026 har om lag 11 000 steder og om lag 4 000 vannverk. Det er en annen liste.",
        "Om lag halvparten av stedene, 5 500, har et punkt på kartet. Resten vet vi ikke hvor ligger.",
        "Vi vet ikke hvor mange mennesker som drikker vann over en grense. Det tallet står ikke i dokumentene som er lest.",
    ],
    "ca-problem-groundwater-overdraft": [
        "Noen steder tømmes vannet under bakken raskere enn det fylles. Vannet brukes til drikke og jordbruk. Da kan bakken synke, saltvann komme inn, og brønner gå tørre. Californias vannetat har pekt ut 21 slike områder. Elleve ligger i jordbruksdalen.",
        "En lov fra 2014 sier at lokalsamfunnene må lage planer som skal stoppe tømmingen.",
        "Om lag 4 millioner mennesker bor i disse områdene, etter vår telling av små ruter fra folketellingen. Etaten har ikke selv gitt ut et folketall.",
        "Der er det om lag halvannen gang så mange voksne uten videregående skole som i resten av California. Vi vet ikke om vannet under bakken er grunnen.",
    ],
    "org-epa": [
        "Dette er miljøtilsynet i USA. De sier hvilke områder som ikke klarer grensen for ren luft, og hvor mange som bodde der i 2010.",
        "De skrev i 2025 at jordbruksdalen ikke klarte en eldre grense for ozon, en gass som irriterer lungene. I 2026 skrev de at dalen har landets høyeste nivå av fint støv, de minste partiklene i luften.",
        "De har også en liste over anlegg som gir et punkt på kartet for raffinerier og gasslageret Aliso Canyon.",
    ],
    "org-oehha": [
        "Dette er Californias miljøhelsekontor. De lager den offisielle oversikten over hvor forurenset og belastet hvert nabolag er. Oversikten heter CalEnviroScreen.",
        "Kartdataene ble hentet 28. oktober 2026. Feltet for opphavsrett er tomt. Områdene er merket med et nummer for hvert nabolag.",
        "Oversikten sammenligner steder. Den måler ikke at en bestemt person er syk. Et høyt tall betyr at nabolaget ligger dårligere an enn de fleste andre.",
    ],
    "org-calgem": [
        "Dette er Californias oljetilsyn. De fører regnskap over hvor oljen pumpes.",
        "I 2023 kom det meste av oljen fra Kern fylke, om lag 90 millioner fat. Ett fat er omtrent 159 liter. Los Angeles fylke hadde om lag 9 millioner fat.",
        "De beskriver at loven om avstand til boliger ble stanset av et forslag om folkeavstemning og begynte å gjelde igjen i 2024.",
    ],
    "org-carb": [
        "Dette er Californias lufttilsyn. De har ansvar for utslipp fra biler og lastebiler. De lokale luftkontorene tar fabrikker og andre faste anlegg.",
        "De regnet ut at gasslekkasjen ved Aliso Canyon var om lag 100 000 tonn metan. Metan er hovedstoffet i naturgass.",
        "De har også ansvar for en lov om ekstra oppfølging av lufta i nabolag med mye forurensning.",
    ],
    "org-dwr": [
        "Dette er Californias vannetat. De peker ut steder der vannet under bakken tappes for hardt. Vannet brukes til drikke og jordbruk.",
        "De har pekt ut 21 slike områder. Elleve ligger i jordbruksdalen.",
        "Hvis tappingen fortsetter, kan bakken synke og saltvann komme inn i brønnene.",
    ],
    "org-dpr": [
        "Dette er Californias tilsyn med sprøytemidler. I 2022 ble det brukt om lag 180 millioner pund av selve giften. Ett pund er omtrent et halvt kilo.",
        "Fresno, Kern og Tulare hadde de høyeste tallene i fylkeslisten.",
        "Pundtallet trekker opp stoffer som brukes i store mengder, som svovel. Det samme jordet kan telles flere ganger. Hvor mange pund det er, er ikke det samme som hvor giftig stoffet er.",
    ],
    "org-scaqmd": [
        "Dette er luftkontoret for området rundt Los Angeles. De sier at området ikke klarer grensen for ozon, en gass som irriterer lungene.",
        "I 2018 kom 27 av 100 deler av en skitten eksosgass, kalt NOx, fra store lastebiler. Gassen er med på å lage ozon. Raffinerier, fabrikker som lager bensin, var blant de største faste kildene, etter fyring i bygninger.",
        "De har målt utslipp ved seks raffinerier, men kalte anleggene A til F i sammendraget. Vi kan derfor ikke si hvilket tall som hører til hvilket selskap.",
    ],
    "org-sjvapcd": [
        "Dette er luftkontoret for jordbruksdalen. De har hovedansvaret for planene som skal få dalen innenfor grensen for ren luft.",
        "De vedtok i 2024 en plan som ber om utsettelse til slutten av 2030 for fint støv, de minste partiklene i luften.",
        "De tar fabrikker og støv fra bakken. Delstatens lufttilsyn tar biler og lastebiler.",
    ],
    "org-swrcb": [
        "Dette er Californias vanntilsyn. De fører listen over vannverk som ikke holder reglene for helse.",
        "De har også pålagt testing av evighetskjemikalier, kalt PFAS, i drikkevannsbrønner. Det er stoffer som nesten ikke forsvinner.",
        "Rapporten om innsjøen Salton Sea er sendt til dette styret.",
    ],
    "org-wspa": [
        "Dette er oljeselskapenes felles organisasjon. I perioden 2025 til 2026 har de brukt om lag 19 millioner dollar på å betale folk for å påvirke politikere.",
        "Et arkiv fra juli 2026 viser fem kvartaler. Summen av dem er lavere enn totalen fra oktober. Vi har ikke en rapport som forklarer forskjellen.",
        "I ett kvartal betalte de blant annet firmaene Carpenter Garcia Sievers, Greenberg Traurig og Pillsbury for å påvirke politikere.",
        "Pengene de ga til valgkamp, er små ved siden av det de betalte for påvirkning. Den største valgkampstrengen er om lag 26 000 dollar.",
    ],
    "bill-sb-1319": [
        "Dette er en søsterlov til loven fra 2014 om vann under bakken. Fran Pavley la den fram.",
        "I delstatsparlamentet stemte senatet 24 mot 10. Forsamlingen stemte 48 mot 26.",
        "Oljeselskapenes felles organisasjon, Chevron og Aera skrev at de jobbet med loven. Skjemaene sier ikke om de var for eller mot.",
    ],
    "bill-sb-200": [
        "Dette er loven som opprettet et fond for trygt drikkevann. Bill Monning la den fram i 2019.",
        "I delstatsparlamentet stemte senatet 38 mot 1. Forsamlingen stemte 68 mot 0. Nesten alle var enige.",
        "Fondet får inntil om lag 130 millioner dollar i året fra pengene bedrifter betaler for å slippe ut klimagass, fram til midten av 2030.",
        "Listen over vannverk som ikke holder mål, er en del av dette programmet.",
    ],
    "bill-ab-1647": [
        "Dette er loven som sier at luften skal måles ved gjerdet rundt raffinerier, fabrikker som lager bensin, og at naboene skal kunne se tallene. Den ble vedtatt i 2017. Al Muratsuchi la den fram.",
        "I delstatsparlamentet stemte forsamlingen 57 mot 19. Senatet stemte 28 mot 11.",
        "Eieren av raffineriet skal betale for målingen, med ett unntak hvis målestasjonen også brukes til andre formål.",
        "Vi har ikke sjekket om hvert eneste raffineri faktisk har målingen i drift i 2026.",
    ],
    "bill-ab-617": [
        "Dette er loven som sier at delstaten skal følge ekstra med på lufta i nabolag som allerede har mye forurensning. Cristina Garcia la den fram i 2017.",
        "I delstatsparlamentet stemte forsamlingen 50 mot 24. Senatet stemte 27 mot 13.",
        "Loven gjelder hele California, ikke bare ett område. Den kan brukes både rundt Los Angeles og i jordbruksdalen.",
    ],
    "bill-ab-1739": [
        "Dette er en av tre lover fra 2014 som skulle stanse at vann under bakken tappes for hardt. Roger Dickinson la den fram. Fran Pavley var med og la den fram.",
        "I delstatsparlamentet stemte forsamlingen 47 mot 28. Senatet stemte 26 mot 11.",
        "Oljeselskapet Chevron skrev i et skjema om betalt påvirkning at de jobbet med denne loven. Skjemaet sier ikke om de var for eller mot.",
    ],
    "bill-sb-1137": [
        "Dette er loven som sier at nye oljebrønner ikke skal bores nærmere enn om lag 1 kilometer fra boliger og skoler. Lena Gonzalez og Monique Limón la den fram. Den ble vedtatt i 2022.",
        "I delstatsparlamentet stemte senatet 25 mot 10. Forsamlingen stemte 46 mot 24.",
        "Et forslag om folkeavstemning stanset loven en periode. Den begynte å gjelde igjen da forslaget ble trukket i 2024.",
        "Oljeselskapenes felles organisasjon skrev senere at de jobbet med loven. Skjemaet sier ikke om de var for eller mot.",
    ],
    "bill-sb-1168": [
        "Dette er hovedloven fra 2014 om at vann under bakken ikke skal tappes for hardt. Fran Pavley la den fram, og hun stemte selv ja.",
        "I delstatsparlamentet stemte senatet 25 mot 10 da loven ble ferdig. Forsamlingen stemte 47 mot 27.",
        "Chevron, Aera og oljeselskapenes felles organisasjon skrev ikke denne loven på skjemaene vi leste. En forening for vann under bakken og en miljøorganisasjon gjorde det. Ingen skrev om de var for eller mot.",
    ],
}


def apply(card_id: str) -> None:
    path = CARDS / f"{card_id}.json"
    card = json.loads(path.read_text(encoding="utf-8"))
    texts = LINES[card_id]
    if len(texts) != len(card["summary"]):
        raise SystemExit(f"{card_id} har {len(card['summary'])} linjer, fikk {len(texts)}")
    for item, text in zip(card["summary"], texts):
        item["text"] = text
    path.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ids = sys.argv[1:]
    if not ids:
        raise SystemExit("oppgi kort-id")
    for card_id in ids:
        apply(card_id)
    print("updated", " ".join(ids))


if __name__ == "__main__":
    main()
