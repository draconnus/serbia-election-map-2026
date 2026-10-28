# Serbia 2026 parliamentary election — results map

Interactive Leaflet + OpenStreetMap map of RIK polling-station results.

- **World view:** countries (Serbia, Kosovo and Metohija, 38 diaspora countries) shaded by aggregated results.
- **Zoom ≥ 6:** circles per municipality / diaspora city, sized by number of voters.
- **Modes:** total voters, or % for Студенти (lista_3) / СНС (lista_1) of valid votes.

## Rebuild

```sh
python3 build.py path/to/results.csv   # writes data.js and shapes.js
```

Geocoding uses OSM Nominatim (cached in `geocache.json`). Country shapes: Natural Earth 1:50m.
Some diaspora station locations are inferred from station names and marked "локација приближна".
