#!/usr/bin/env python3
"""Aggregate RIK polling-station CSV into country + town level data for the map.

Usage: python3 build.py /path/to/results.csv
Geocoding uses OSM Nominatim (cached in geocache.json, 1 req/s).
"""
import csv, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SNS, STUDENTS = "lista_1", "lista_3"
LISTS = [f"lista_{i}" for i in range(1, 31)]

# bm_broj of abroad stations -> (town, ISO2, geocode query)
ABROAD = {
    1: ("Мелбурн", "AU", "Melbourne, Australia"), 2: ("Сиднеј", "AU", "Sydney, Australia"),
    3: ("Беч", "AT", "Vienna, Austria"), 4: ("Беч", "AT", "Vienna, Austria"),
    5: ("Беч", "AT", "Vienna, Austria"), 6: ("Беч", "AT", "Vienna, Austria"),
    7: ("Салцбург", "AT", "Salzburg, Austria"), 8: ("Линц", "AT", "Linz, Austria"),
    9: ("Брисел", "BE", "Brussels, Belgium"),
    10: ("Сарајево", "BA", "Sarajevo"), 11: ("Бања Лука", "BA", "Banja Luka"),
    12: ("Бања Лука", "BA", "Banja Luka"), 13: ("Бања Лука", "BA", "Banja Luka"),
    14: ("Мостар", "BA", "Mostar"), 15: ("Дрвар", "BA", "Drvar"), 16: ("Требиње", "BA", "Trebinje"),
    17: ("Зворник", "BA", "Zvornik"), 18: ("Зворник", "BA", "Zvornik"), 19: ("Зворник", "BA", "Zvornik"),
    20: ("Братунац", "BA", "Bratunac"), 21: ("Вишеград", "BA", "Višegrad"),
    22: ("Источно Сарајево", "BA", "Istočno Sarajevo"), 23: ("Бијељина", "BA", "Bijeljina"),
    24: ("Бијељина", "BA", "Bijeljina"), 25: ("Фоча", "BA", "Foča"), 26: ("Рудо", "BA", "Rudo, Bosnia"),
    27: ("Мркоњић Град", "BA", "Mrkonjić Grad"), 28: ("Пале", "BA", "Pale, Bosnia"),
    29: ("Добој", "BA", "Doboj"), 30: ("Соколац", "BA", "Sokolac"), 31: ("Приједор", "BA", "Prijedor"),
    32: ("Билећа", "BA", "Bileća"), 33: ("Невесиње", "BA", "Nevesinje"), 34: ("Хан Пијесак", "BA", "Han Pijesak"),
    35: ("Угљевик", "BA", "Ugljevik"), 36: ("Гацко", "BA", "Gacko"), 37: ("Ново Горажде", "BA", "Novo Goražde"),
    38: ("Бразилија", "BR", "Brasília"), 39: ("Атина", "GR", "Athens"), 40: ("Копенхаген", "DK", "Copenhagen"),
    41: ("Џакарта", "ID", "Jakarta"), 42: ("Даблин", "IE", "Blanchardstown, Dublin"),
    43: ("Рим", "IT", "Rome"), 44: ("Милано", "IT", "Milan"), 45: ("Трст", "IT", "Trieste"),
    46: ("Токио", "JP", "Tokyo"), 47: ("Преторија", "ZA", "Pretoria"), 48: ("Отава", "CA", "Ottawa"),
    49: ("Торонто", "CA", "Toronto"), 50: ("Пекинг", "CN", "Beijing"), 51: ("Никозија", "CY", "Nicosia"),
    52: ("Луксембург", "LU", "Luxembourg City"), 53: ("Малта", "MT", "St. Julian's, Malta"),
    54: ("Будимпешта", "HU", "Budapest"), 55: ("Берлин", "DE", "Berlin"), 56: ("Диселдорф", "DE", "Düsseldorf"),
    57: ("Минхен", "DE", "Munich"), 58: ("Минхен", "DE", "Munich"), 59: ("Штутгарт", "DE", "Stuttgart"),
    60: ("Франкфурт", "DE", "Frankfurt am Main"), 61: ("Франкфурт", "DE", "Frankfurt am Main"),
    62: ("Хамбург", "DE", "Hamburg"), 63: ("Окланд", "NZ", "Auckland"), 64: ("Осло", "NO", "Oslo"),
    65: ("Варшава", "PL", "Warsaw"), 66: ("Лисабон", "PT", "Lisbon"), 67: ("Москва", "RU", "Moscow"),
    68: ("Темишвар", "RO", "Timișoara"), 69: ("Скопље", "MK", "Skopje"), 70: ("Куманово", "MK", "Kumanovo"),
    71: ("Вашингтон", "US", "Washington, D.C."), 72: ("Чикаго", "US", "Chicago"),
    73: ("Њујорк", "US", "New York City"), 74: ("Лос Анђелес", "US", "Santa Monica, California"),
    75: ("Љубљана", "SI", "Ljubljana"), 76: ("Љубљана", "SI", "Ljubljana"), 77: ("Лондон", "GB", "London"),
    78: ("Хелсинки", "FI", "Helsinki"), 79: ("Париз", "FR", "Paris"), 80: ("Стразбур", "FR", "Strasbourg"),
    81: ("Хаг", "NL", "The Hague"), 82: ("Загреб", "HR", "Zagreb"), 83: ("Вуковар", "HR", "Vukovar"),
    84: ("Подгорица", "ME", "Podgorica"), 85: ("Подгорица", "ME", "Podgorica"), 86: ("Подгорица", "ME", "Podgorica"),
    87: ("Праг", "CZ", "Prague"), 88: ("Берн", "CH", "Bern"), 89: ("Цирих", "CH", "Zürich"),
    90: ("Стокхолм", "SE", "Stockholm"), 91: ("Малме", "SE", "Malmö"),
    92: ("Мадрид", "ES", "Madrid"), 93: ("Мадрид", "ES", "Madrid"),
}
COUNTRY_SR = {
    "RS": "Србија", "XK": "Косово и Метохија", "BA": "Босна и Херцеговина", "DE": "Немачка", "AT": "Аустрија",
    "US": "САД", "IT": "Италија", "CH": "Швајцарска", "SI": "Словенија", "FR": "Француска", "SE": "Шведска",
    "GB": "Уједињено Краљевство", "CA": "Канада", "NL": "Холандија", "NO": "Норвешка", "ES": "Шпанија",
    "MT": "Малта", "MK": "Северна Македонија", "CZ": "Чешка", "ME": "Црна Гора", "HR": "Хрватска",
    "BE": "Белгија", "AU": "Аустралија", "DK": "Данска", "GR": "Грчка", "CY": "Кипар", "RU": "Русија",
    "PT": "Португалија", "HU": "Мађарска", "CN": "Кина", "LU": "Луксембург", "IE": "Ирска",
    "NZ": "Нови Зеланд", "PL": "Пољска", "FI": "Финска", "JP": "Јапан", "ZA": "Јужноафричка Република",
    "ID": "Индонезија", "RO": "Румунија", "BR": "Бразил",
}
# Stations in BiH whose exact town is inferred from school names, not stated in the data.
APPROX_BM = set(range(17, 37)) | {52, 53, 68, 74, 85, 86}

# Nominatim picks same-named villages for these; pin municipality centres manually.
OVERRIDES = {
    "RS|Сопот": [44.5194, 20.5753], "RS|Рача": [44.2272, 20.9836], "RS|Жабари": [44.3556, 21.2147],
    "RS|Црвени крст": [43.3350, 21.8800], "RS|Трговиште": [42.3514, 22.0814],
    "XK|Обилић": [42.6869, 21.0775], "XK|Гора": [42.0626, 20.6533],
}


def num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def empty():
    return {"registered": 0, "voted": 0, "valid": 0, "invalid": 0, "stations": 0, "reported": 0,
            "lists": [0] * 30}


def add(agg, row):
    agg["registered"] += num(row["upisani_biraci"])
    agg["voted"] += num(row["glasali_biraci"])
    agg["valid"] += num(row["vazeci_glasovi"])
    agg["invalid"] += num(row["nevazeci_listici"])
    agg["stations"] += 1
    if row["vreme_unosa_rezultata"] not in ("", "-"):
        agg["reported"] += 1
    for i, k in enumerate(LISTS):
        agg["lists"][i] += num(row.get(k))


def clean_muni(name):
    return re.sub(r"^(Градска општина|Општина|Град)\s+", "", name).strip()


cache_path = HERE / "geocache.json"
cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}


def geocode(query, cc=None):
    key = f"{query}|{cc or ''}"
    if key in cache:
        return cache[key]
    params = {"q": query, "format": "json", "limit": 1}
    if cc:
        params["countrycodes"] = cc
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "election-map-demo/1.0 (local build script)"})
    time.sleep(1.1)
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    cache[key] = [float(res[0]["lat"]), float(res[0]["lon"])] if res else None
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=0))
    print(("ok  " if res else "MISS"), query, cc, flush=True)
    return cache[key]


def main(csv_path):
    rows = [r for r in csv.DictReader(open(csv_path, encoding="utf-8-sig")) if r.get("bm_uid", "").isdigit()]
    countries, towns = {}, {}
    total = empty()
    for r in rows:
        region = r["okrug_region"]
        add(total, r)
        if r["opstina"] == "Иностранство":
            town, cc, q = ABROAD[num(r["bm_broj"])]
            approx = num(r["bm_broj"]) in APPROX_BM
        elif region.startswith("Заводи"):
            # Prisons have no municipality; count them for Serbia only.
            cc, town, q, approx = "RS", None, None, False
        else:
            cc = "XK" if region.startswith("Регион Косово") else "RS"
            town = clean_muni(r["opstina"])
            q, approx = town, False
        countries.setdefault(cc, empty())
        add(countries[cc], r)
        if town is None:
            continue
        key = f"{cc}|{town}"
        if key not in towns:
            towns[key] = {"name": town, "cc": cc, "query": q, "approx": approx,
                          "region": region.split("/")[-1], **empty()}
        add(towns[key], r)
        towns[key]["approx"] = towns[key]["approx"] or approx

    missing = []
    for key, t in towns.items():
        if key in OVERRIDES:
            ll = OVERRIDES[key]
        elif t["cc"] in ("RS", "XK"):
            ll = geocode(t["query"], "rs,xk") or geocode(t["query"] + ", Србија")
        else:
            ll = geocode(t["query"], t["cc"].lower())
        if not ll:
            missing.append(t["name"])
        t["ll"] = ll
        del t["query"]

    for cc, a in countries.items():
        a["name"] = COUNTRY_SR.get(cc, cc)
    ne = json.loads((HERE / "ne_50m_admin_0_countries.geojson").read_text())
    feats = []
    for f in ne["features"]:
        p = f["properties"]
        cc = p["ISO_A2_EH"] if p["ISO_A2_EH"] != "-99" else p["ISO_A2"]
        if cc in countries:
            feats.append({"type": "Feature", "properties": {"cc": cc}, "geometry": f["geometry"]})
    (HERE / "shapes.js").write_text("window.COUNTRY_SHAPES = " + json.dumps(
        {"type": "FeatureCollection", "features": feats}, separators=(",", ":")) + ";\n")

    out = {"sns": SNS, "students": STUDENTS, "total": total, "countries": countries,
           "towns": [t for t in towns.values() if t["ll"]],
           "listNames": {SNS: "СНС (листа 1)", STUDENTS: "Студенти (листа 3)"}}
    (HERE / "data.js").write_text("window.ELECTION_DATA = " + json.dumps(out, ensure_ascii=False) + ";\n")
    print(f"stations={len(rows)} countries={len(countries)} towns={len(out['towns'])} missing={missing}")


if __name__ == "__main__":
    main(sys.argv[1])
