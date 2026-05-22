# copyCatcher Frontend

Frontend för **copyCatcher**, en React-applikation byggd med Vite. Applikationen låter användaren skicka in en URL, hämta analysdata från en backend och visa resultat samt statistik över potentiella copycat-/counterfeit-träffar.

## Tekniker

Projektet använder bland annat:

- React
- Vite
- React Router
- React Bootstrap
- Bootstrap
- Material UI
- MUI X Charts
- React Icons
- ESLint

## Funktioner

- Inloggningssida med formulär
- Sökvy där användaren kan ange en URL
- API-anrop till backend för att skrapa/analysera en URL
- Resultatsida som visar hittade produktbilder
- Sortering av resultat efter risk eller namn
- Statistikvy med cirkeldiagram
- Konfigurerbar backend-URL via miljövariabel
- Dockerfile för att köra frontend i container

## Kom igång

### Förkrav

Du behöver ha installerat:

- Node.js
- npm

Kontrollera installationen med:

```bash
node -v
npm -v
```

### Installation

Installera projektets beroenden:

```bash
npm install
```

### Starta utvecklingsservern

```bash
npm run dev
```

Öppna sedan adressen som visas i terminalen, vanligtvis:

```txt
http://localhost:5173
```

## Scripts

```bash
npm run dev
```

Startar Vite utvecklingsserver.

```bash
npm run build
```

Bygger projektet för produktion. Builden hamnar i `dist/`.

```bash
npm run preview
```

Förhandsvisar produktionsbygget lokalt.

```bash
npm run lint
```

Kör ESLint på projektet.

## Miljövariabler

Frontend använder en miljövariabel för att veta vilken backend den ska prata med.

Skapa en `.env`-fil i projektets rotmapp:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Om variabeln inte sätts används standardvärdet:

```txt
http://localhost:8000
```

I Vite måste miljövariabler som används i frontend börja med `VITE_`.

## API-koppling

API-anropen finns samlade i:

```txt
src/api.js
```

Filen innehåller två centrala funktioner:

### `scrapeUrl(url)`

Skickar en URL till backend:

```txt
GET /scrape_url?url=<url>
```

Implementationens viktiga delar:

- använder `encodeURIComponent` för att skicka URL:en säkert som query-parameter
- har en timeout på 5 minuter med `AbortController`
- kastar tydliga fel om backend svarar med felstatus
- returnerar JSON-data från backend

### `getStats()`

Hämtar statistik från backend:

```txt
GET /data/stats
```

Används på statistiksidan för att visa sammanfattningar i diagram.

## Routing

Routing hanteras med `react-router-dom`.

Huvudrutterna finns i:

```txt
src/App.jsx
```

| Route         | Sida       | Beskrivning                      |
| ------------- | ---------- | -------------------------------- |
| `/`           | Login      | Visar inloggningssidan           |
| `/search`     | Search     | Sida där användaren anger en URL |
| `/results`    | Results    | Visar resultat från analysen     |
| `/statistics` | Statistics | Visar statistik från backend     |

Navigationsmenyn visas inte på login-sidan, utan bara på övriga sidor.

## Viktiga implementationer

### Sökflöde

Sökflödet börjar i:

```txt
src/pages/search.jsx
```

När användaren skickar in en URL:

1. `SearchBar` skickar queryn till `handleSearch`.
2. `handleSearch` anropar `scrapeUrl(query)`.
3. Resultatet skickas vidare till resultatsidan med `navigate`.
4. Resultatsidan öppnas med queryn i URL:en och backend-data i route state.

```js
navigate("/results?query=" + encodeURIComponent(query), {
  state: { data: result },
});
```

Sidan hanterar även laddningsläge och felmeddelanden.

### Resultatnormalisering

Resultatsidan finns i:

```txt
src/pages/results.jsx
```

Backend-data kan komma i olika format. Därför normaliseras datan innan den renderas.

Viktiga funktioner:

- `unwrapBackendData(data)` plockar ut data från exempelvis `data.data` eller `data.result`.
- `getImageUrl(item)` försöker hitta bild-URL från flera möjliga fältnamn.
- `formatPredictionName(prediction)` gör prediktioner mer läsbara.
- `normalizeBackendProducts(data, query)` gör om backend-svaret till en enhetlig produktlista.

Detta gör frontend mer tolerant mot variationer i backend-svaret.

### Sortering av resultat

I `results.jsx` kan användaren sortera resultaten efter:

- högst copycat-risk
- lägst copycat-risk
- namn A–Ö
- namn Ö–A

Sorteringen styrs av React state:

```js
const [sortType, setSortType] = useState("risk-high");
```

### Statistik

Statistiksidan finns i:

```txt
src/pages/statistics.jsx
```

Den hämtar statistik från backend med `getStats()` och visar flera cirkeldiagram:

- sparade bildresultat
- senaste skrapning
- webbplatser med counterfeits
- skrapning med flest flaggade bilder

Diagrammen skapas med komponenten:

```txt
src/components/PieChart.jsx
```

Statistiksidan hanterar även laddningsläge och fel om backend inte går att nå.

### Diagramkomponent

`PieChart.jsx` använder `@mui/x-charts` för att rendera cirkeldiagram.

Komponenten tar emot data i formatet:

```js
[
  { label: "Counterfeits", value: 10 },
  { label: "Non-counterfeits", value: 90 },
];
```

### Sökkomponent

`SearchBar.jsx` är en återanvändbar komponent som använder React Bootstrap och en sökikon från `react-icons`.

Den tar emot en prop:

```js
onSearch;
```

När formuläret skickas körs `onSearch(query)`.

### Login

Login-komponenten finns i:

```txt
src/components/LoginBox.jsx
```

Den innehåller ett formulär för e-post och lösenord. I nuläget gör den ingen riktig autentisering, utan navigerar användaren direkt till `/search` efter submit.

## Projektstruktur

```txt
.
├── Dockerfile
├── eslint.config.js
├── index.html
├── package.json
├── vite.config.js
├── public/
│   └── vite.svg
└── src/
    ├── api.js
    ├── App.jsx
    ├── main.jsx
    ├── App.css
    ├── index.css
    ├── components/
    │   ├── LoginBox.jsx
    │   ├── PercentageBar.jsx
    │   ├── PieChart.jsx
    │   ├── Protected_route.jsx
    │   ├── SearchBar.jsx
    │   └── test_data.jsx
    └── pages/
        ├── login.jsx
        ├── login.css
        ├── search.jsx
        ├── search.css
        ├── results.jsx
        ├── results.css
        ├── statistics.jsx
        └── statistics.css
```

## Köra med Docker

Projektet innehåller en Dockerfile som bygger en container baserad på `node:20-alpine`.

Bygg imagen:

```bash
docker build -t copycatcher-frontend .
```

Kör containern:

```bash
docker run -p 5173:5173 copycatcher-frontend
```

Frontend blir då tillgänglig på:

```txt
http://localhost:5173
```

Dockerfilen startar utvecklingsservern med:

```bash
npm run dev -- --host 0.0.0.0 --port 5173
```

## Bygga för produktion

Skapa en produktionsbuild:

```bash
npm run build
```

Builden skapas i:

```txt
dist/
```

Förhandsvisa builden lokalt:

```bash
npm run preview
```

## Kommentarer / förbättringsförslag

Några saker som kan vara bra att se över framöver:

- `LoginBox.jsx` innehåller ingen riktig autentisering ännu.
- `Protected_route.jsx` är tom och kan antingen implementeras eller tas bort.
- `PercentageBar.jsx` importerar `prop-types`, men `prop-types` finns inte listat som direkt dependency i `package.json`.
- `dist/` och `node_modules/` bör normalt inte skickas med i Git-repot.
- Projektnamnet i `package.json` är `test`; det kan ändras till exempelvis `copycatcher-frontend`.

## Författare

Skapad av Ludvig Bengtsson & Jessica Andersson.
