# Serbia 2026 parliamentary election — results map

Interactive Leaflet + OpenStreetMap map of RIK polling-station results.

- **World view:** countries (Serbia, Kosovo and Metohija, 38 diaspora countries) shaded by aggregated results.
- **Zoom ≥ 6:** circles per municipality / diaspora city, sized by number of voters.
- **Map shading:** switch between total voters, voters per 100,000 host-country residents, and Serbia-origin migrants per 100,000 host-country residents. Result details retain vote counts and percentages for Студенти (lista_3) / СНС (lista_1).
- **Country demographics:** 2020 mid-year estimates from the UN World Population Prospects 2024 and UN International Migrant Stock 2020. Tooltips show Serbia-origin migrants and a joint Serbia + Croatia + Bosnia and Herzegovina + Montenegro total per 100,000 host-country residents. These are comparable migrant-origin estimates, not ethnicity counts. Values that the UN table does not report separately are shown as unavailable, not zero; the joint total is shown only when all four origins are available.

## Rebuild

```sh
python3 build.py path/to/results.csv   # writes data.js and shapes.js
```

Geocoding uses OSM Nominatim (cached in `geocache.json`). Country shapes: Natural Earth 1:50m.
Some diaspora station locations are inferred from station names and marked "локација приближна".

Country demographic sources:

- [UN World Population Prospects](https://population.un.org/wpp/)
- [UN International Migrant Stock](https://www.un.org/development/desa/pd/content/international-migrant-stock)
