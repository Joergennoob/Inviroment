export const LAYER_TITLE: Record<string, string> = {
  pm25: "For mye fint støv i luften",
  ozone: "For mye ozon i luften",
  basins: "Vann under bakken som tømmes",
  "failing-water": "Vannverk som bryter reglene",
  pesticide: "Sprøytemidler i 2022",
  "valley-fever": "Dalfeber i 2022",
  "salton-line": "Kanten av innsjøen Salton Sea",
  "salton-ring": "Nær innsjøen Salton Sea",
  circles: "Nærområdet rundt raffinerier og gasslageret",
  "oil-zone": "Omtrent 1 km fra oljebrønner",
  wells: "Olje- og gassbrønner",
  schools: "Skoler nær oljebrønner",
  pfas: "Steder med evighetskjemikalier",
  facilities: "Raffinerier og gasslager",
  districts: "Politikernes valgkretser",
};

export const CARD_TITLE: Record<string, string> = {
  "ca-problem-south-coast-air": "Skitten luft rundt Los Angeles",
  "ca-problem-san-joaquin-air": "Skitten luft i jordbruksdalen",
  "ca-problem-drinking-water": "Vannverk som ikke gir trygt vann",
  "ca-problem-oil-gas-proximity": "Oljebrønner for nær hus og skoler",
  "ca-problem-pesticides": "Sprøytemidler på jordene",
  "ca-problem-salton-sea": "Innsjøen som tørker og lager støv",
  "ca-problem-refineries": "Raffinerier tett på boliger",
  "ca-problem-aliso-canyon": "Den store gasslekkasjen",
  "ca-problem-pfas": "Kjemikalier som nesten ikke forsvinner",
  "ca-problem-groundwater-overdraft": "Vann under bakken som tømmes",
  "bill-ab-1647": "Loven om å måle luft ved raffinerier",
  "bill-ab-1739": "En av lovene om vann under bakken",
  "bill-ab-617": "Loven om ekstra oppsyn med skitten luft",
  "bill-sb-1137": "Loven om avstand mellom oljebrønner og hus",
  "bill-sb-1168": "Hovedloven om vann under bakken",
  "bill-sb-1319": "Søsterloven om vann under bakken",
  "bill-sb-200": "Loven om et fond for trygt drikkevann",
  "org-epa": "Miljøtilsynet i USA",
  "org-oehha": "Californias miljøhelsekontor",
  "org-calgem": "Californias oljetilsyn",
  "org-carb": "Californias lufttilsyn",
  "org-dwr": "Californias vannetat",
  "org-dpr": "Californias tilsyn med sprøytemidler",
  "org-swrcb": "Californias vanntilsyn",
  "org-scaqmd": "Luftkontoret rundt Los Angeles",
  "org-sjvapcd": "Luftkontoret i jordbruksdalen",
  "org-wspa": "Oljeselskapenes felles organisasjon",
  "org-cipa": "Foreningen for mindre oljeselskaper",
  "org-farm-bureau": "Bøndenes organisasjon",
  "org-iid": "Vannverket ved Salton Sea",
};

export function plainTitle(card: { id: string; name: string }): string {
  return CARD_TITLE[card.id] ?? card.name;
}

export function officialName(card: { id: string; name: string }): string | null {
  const plain = CARD_TITLE[card.id];
  if (!plain || plain === card.name) return null;
  return card.name;
}

export type GlossaryEntry = { word: string; means: string };

export const GLOSSARY: GlossaryEntry[] = [
  {
    word: "Nabolag (census tract)",
    means: "Et lite område som den amerikanske folketellingen bruker. Ofte om lag 4 000 innbyggere. Vi bruker det når en etat har tall for et nabolag, ikke for en hel by.",
  },
  {
    word: "Område der luften blir liggende (luftbasseng)",
    means: "Et område der luften blir liggende fordi fjell rundt holder den inne. Rundt Los Angeles er et slikt område. Skitten luft blåser ikke bare videre.",
  },
  {
    word: "Vann under bakken (grunnvannsbasseng)",
    means: "Et område der det ligger vann under bakken. Det brukes til drikkevann og jordbruk. Hvis man pumper mer enn det som renner inn, tømmes lageret.",
  },
  {
    word: "Farget felt (polygon)",
    means: "Et farget område på kartet. Det er ikke et hus eller en prikk. Det viser hvor et problem gjelder.",
  },
  {
    word: "Klarer ikke grensen for ren luft (nonattainment)",
    means: "Luften er for skitten. Den er over grensen som miljøtilsynet i USA har satt.",
  },
  {
    word: "Californias oversikt over nabolag (CalEnviroScreen)",
    means: "Californias offisielle oversikt over hvor forurenset og belastet hvert nabolag er. Et høyt tall betyr at nabolaget ligger dårligere an enn de fleste andre. Det er ikke en diagnose på en person.",
  },
  {
    word: "Californias miljøhelsekontor (OEHHA)",
    means: "Kontoret som lager oversikten over nabolagene. De jobber med helsefare fra forurensning.",
  },
  {
    word: "Anleggsregisteret (FRS)",
    means: "Listen til miljøtilsynet i USA over fabrikker, raffinerier og gasslager, med et punkt på kartet.",
  },
  {
    word: "Eksosgass (NOx)",
    means: "En skitten gass fra biler, lastebiler og fabrikker. Den er med på å lage både fint støv og ozon.",
  },
  {
    word: "Fint støv (PM2.5)",
    means: "De minste partiklene i luften, så små at du nesten ikke ser dem. De kan komme ned i lungene.",
  },
  {
    word: "Ozon",
    means: "En gass nede ved bakken som irriterer lungene. Den lages når sol treffer eksos. Høyt oppe i atmosfæren er ozon noe annet.",
  },
  {
    word: "Verre enn X av 100 (persentil)",
    means: "En plassering. «Verre enn 90 av 100» betyr at bare 10 av 100 områder i California ligger dårligere an.",
  },
  {
    word: "Miljøtilsynet i USA (EPA)",
    means: "Den føderale etaten som setter grenser for ren luft og fører register over anlegg.",
  },
  {
    word: "Evighetskjemikalier (PFAS)",
    means: "En gruppe kjemikalier som nesten ikke brytes ned. De er brukt i blant annet brannskum og kan havne i drikkevann.",
  },
  {
    word: "Dalfeber",
    means: "En sykdom man kan få av sopp i støv. Den er vanligere i tørre deler av California.",
  },
  {
    word: "Pund og acre",
    means: "Amerikanske mål. Ett pund er omtrent et halvt kilo. En acre er et flatemål, omtrent fire norske mål. En acre-fot er nok vann til å dekke en acre med en fot vann.",
  },
  {
    word: "Kubikkfot og fat",
    means: "Amerikanske mål. Kubikkfot er et rommål for gass. Ett fat olje er omtrent 159 liter.",
  },
  {
    word: "Metan",
    means: "Hovedstoffet i naturgass. Det er også en gass som varmer opp kloden.",
  },
  {
    word: "Raffineri",
    means: "En fabrikk som lager bensin og annet drivstoff av olje.",
  },
  {
    word: "Lobbyvirksomhet",
    means: "Å betale noen for å påvirke politikere og etater. Beløpet er det som er rapportert, ikke et bevis på at en lov ble kjøpt.",
  },
  {
    word: "Senatet og forsamlingen",
    means: "De to delene av delstatsparlamentet i California. Begge må si ja før en lov kan bli vedtatt.",
  },
  {
    word: "I dokumentet",
    means: "Setningen står i et offentlig dokument vi har lenket til. Det betyr ikke at miljøet er bevist som årsak til sykdom.",
  },
];

const TRACT_PLAIN: Record<string, string> = {
  "6037204920":
    "Dette fargede feltet er ett nabolag i Los Angeles. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor sier at dette nabolaget er hardt belastet av forurensning. Feltet er ikke hele området rundt Los Angeles, der fjell holder luften inne.",
  "6019001100":
    "Dette fargede feltet er ett nabolag i Fresno. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor ga dette nabolaget den høyeste samlede belastningen i uttrekket vi leste. Feltet er ikke hele jordbruksdalen.",
  "6019001000":
    "Dette fargede feltet er ett nabolag i Fresno. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor bruker det som et eksempel på mye sprøytemiddel. Det er ikke et kart over all sprøyting.",
  "6019001500":
    "Dette fargede feltet er ett nabolag i Fresno. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor viser her hvor skittent drikkevannet er i oversikten deres. Det er ikke et navngitt vannverk fra listen over verk som bryter reglene.",
  "6029006201":
    "Dette fargede feltet er ett nabolag i Kern. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Nabolaget ligger i et fylke der vann under bakken tømmes for hardt. Feltet er ikke selve grensen for det vannlageret.",
  "6025012100":
    "Dette fargede feltet er ett nabolag i Imperial, ved innsjøen Salton Sea. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor har tall for nabolaget. Streken er ikke kanten av innsjøen.",
};

function placeLabel(name: string): string {
  if (name.startsWith("South Coast")) return "området rundt Los Angeles";
  if (name.startsWith("San Joaquin")) return "jordbruksdalen fra Stockton til Bakersfield";
  if (name.startsWith("Imperial")) return "Imperial, fylket ved innsjøen Salton Sea";
  return name;
}

export function explainPlacement(input: {
  featureName: string;
  sourceName: string;
  recordId: string;
  note: string;
  layer?: string;
}): { headline: string; plain: string } {
  const { featureName, recordId, note, layer } = input;
  if (TRACT_PLAIN[recordId]) {
    return { headline: "Ett nabolag", plain: TRACT_PLAIN[recordId] };
  }
  if (layer === "pm25" || /PM2\.5|PM2,5/.test(featureName)) {
    const bowl = featureName.startsWith("South Coast")
      ? " Rundt Los Angeles ligger fjell som holder luften inne, så skitten blir liggende."
      : "";
    return {
      headline: `For mye fint støv i ${placeLabel(featureName)}`,
      plain: `Det fargede feltet er ${placeLabel(featureName)}. Der er det for mye fint støv. Fint støv er de minste partiklene i luften, så små at du nesten ikke ser dem. Miljøtilsynet i USA sier at området ikke klarer grensen for ren luft.${bowl}`,
    };
  }
  if (layer === "ozone" || /ozon/i.test(featureName)) {
    return {
      headline: `For mye ozon i ${placeLabel(featureName)}`,
      plain: `Det fargede feltet er ${placeLabel(featureName)}. Der er det for mye ozon, en gass nede ved bakken som irriterer lungene. Miljøtilsynet i USA sier at området ikke klarer grensen for ren luft.`,
    };
  }
  if (layer === "basins" || /grunnvannsbasseng/i.test(note)) {
    return {
      headline: featureName,
      plain: "Det fargede feltet er et område der vannet under bakken tømmes raskere enn det fylles. Vannet brukes til drikke og jordbruk. Californias vannetat har pekt det ut. Kanten på kartet er forenklet.",
    };
  }
  if (layer === "failing-water") {
    return {
      headline: "Et vannverk som bryter reglene",
      plain: "Det fargede feltet er området til et vannverk som ikke holder reglene for trygt drikkevann. Californias vanntilsyn har det på listen.",
    };
  }
  if (layer === "pesticide") {
    return {
      headline: featureName.replace(" County", ""),
      plain: "Fylket er farget etter hvor mye sprøytemiddel som ble brukt i 2022. Mørkere betyr mer. Et pund er omtrent et halvt kilo. Tallene kommer fra Californias tilsyn med sprøytemidler. Kartet viser fylket, ikke hvert jorde.",
    };
  }
  if (layer === "valley-fever") {
    return {
      headline: featureName.replace(" County", ""),
      plain: "Fylket er farget etter hvor vanlig dalfeber var i 2022. Dalfeber er en sykdom man kan få av sopp i støv. Tallene kommer fra Californias helsemyndighet.",
    };
  }
  if (layer === "salton-line" || /strandlinje/i.test(note)) {
    return {
      headline: "Kanten av innsjøen",
      plain: "Streken er kanten av innsjøen Salton Sea. Den viser ikke den tørre sjøbunnen.",
    };
  }
  if (layer === "salton-ring" || /fra strandlinjen/i.test(note)) {
    return {
      headline: "Nær innsjøen",
      plain: "Feltet er omtrent en engelsk mil, om lag 1,6 kilometer, ut fra kanten av innsjøen. Det er et rutenett vi har laget, ikke en grense en etat har tegnet.",
    };
  }
  if (layer === "circles" || /Radiusen er valgt/i.test(note)) {
    return {
      headline: featureName,
      plain: "Sirkelen er tegnet av oss rundt anlegget, så du ser hvem som bor nær det. En engelsk mil er om lag 1,6 kilometer. Det er ikke en grense som en etat har tegnet.",
    };
  }
  if (layer === "oil-zone") {
    return {
      headline: "Nær olje- og gassbrønner",
      plain: "Feltet er omtrent 1 kilometer rundt olje- og gassbrønner. Det er et forenklet rutenett, ikke en nøyaktig sirkel rundt hver brønn.",
    };
  }
  if (layer === "wells") {
    return {
      headline: "En olje- eller gassbrønn",
      plain: "Prikken er en olje- eller gassbrønn som er i bruk, eller som står stille men ikke er stengt for godt. Californias oljetilsyn har registrert den.",
    };
  }
  if (layer === "schools") {
    return {
      headline: "En skole",
      plain: "Prikken er en skole som ligger nærmere enn om lag 1 kilometer fra en olje- eller gassbrønn.",
    };
  }
  if (layer === "pfas") {
    return {
      headline: "Et sted som skal testes",
      plain: "Prikken er et sted der drikkevann kan hentes. Det står på listen over steder som skal testes for evighetskjemikalier, stoffer som nesten ikke forsvinner. Prikken er ikke et prøvesvar.",
    };
  }
  if (layer === "facilities" || /Latitude83|FRS|registry id/i.test(note)) {
    return {
      headline: featureName,
      plain: "Prikken er et anlegg, for eksempel et raffineri eller et gasslager. Miljøtilsynet i USA har registrert det i anleggsregisteret sitt.",
    };
  }
  if (layer === "districts") {
    return {
      headline: featureName,
      plain: "Feltet er valgkretsen til en politiker i delstaten, området personen er valgt fra.",
    };
  }
  if (/census tract/i.test(note) || /census tract/i.test(featureName)) {
    return {
      headline: "Ett nabolag",
      plain: "Dette fargede feltet er ett nabolag. Et nabolag her er et lite område som den amerikanske folketellingen bruker, om lag 4 000 innbyggere. Californias miljøhelsekontor har tall for det. Feltet er ikke hele problemområdet.",
    };
  }
  return {
    headline: featureName,
    plain: "Vi viser stedet fordi en offentlig etat har oppgitt det. De nøyaktige navnene og numrene ligger under.",
  };
}
