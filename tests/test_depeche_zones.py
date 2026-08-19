#!/usr/bin/env python3
"""Tests de la recherche Dépêche (normalisation, JSON, intervalle d'accès)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONES_PATH = ROOT / "data" / "zones-depeche.json"
INDEX_PATH = ROOT / "index.html"
BOISSY_OFFSET = 25000


def normalize_zone_id(value: str) -> str:
    s = str(value or "").strip().upper()
    s = re.sub(r"\s+", "", s)
    if s[:1] == "Z" and (len(s) == 1 or s[1].isdigit() or s[1] == "("):
        s = s[1:]
    return s


def format_depeche_pk(pk_metric: float, branch: str) -> str:
    offset = BOISSY_OFFSET if branch == "boissy" else 0
    display = int(round(pk_metric - offset))
    sign = "-" if display < 0 else ""
    abs_v = abs(display)
    return f"{sign}{abs_v // 1000}.{abs_v % 1000:03d}"


def distance_pk_to_interval(pk: float, pk_start: float, pk_end: float) -> float:
    a, b = min(pk_start, pk_end), max(pk_start, pk_end)
    if a <= pk <= b:
        return 0.0
    return a - pk if pk < a else pk - b


def search_zones(query: str, data: list[dict]) -> dict:
    query_norm = normalize_zone_id(query)
    exact = []
    similar = []
    for entry in data:
        key = entry.get("zoneKey") or normalize_zone_id(entry.get("zone", ""))
        if key == query_norm:
            exact.append(entry)
        elif key.startswith(query_norm):
            similar.append(entry)
    return {"exact": exact, "similar": similar}


def access_search_branch_for_zone(pk_start: float, pk_end: float, branch_hint: str | None) -> str:
    """Miroir de findNearestAccessForZone : tronc jusqu'à la fourche de Fontenay (31500)."""
    fontenay_fork_pk = 31500
    a, b = min(pk_start, pk_end), max(pk_start, pk_end)
    if b <= fontenay_fork_pk:
        return "central"
    if branch_hint in ("boissy", "chessy"):
        return branch_hint
    if a >= 31795:
        return "chessy"
    if a >= 32750:
        return "boissy"
    return "central"


def main() -> int:
    failed: list[str] = []

    def check(name: str, expected, actual) -> None:
        ok = expected == actual
        print(("OK  " if ok else "FAIL") + f" {name}: attendu={expected!r} obtenu={actual!r}")
        if not ok:
            failed.append(name)

    for raw, expected in [
        ("1323A", "1323A"),
        ("Z1323A", "1323A"),
        ("Z 1323A", "1323A"),
        ("z 1323a", "1323A"),
        ("3312(2)", "3312(2)"),
        ("Z3312(2)", "3312(2)"),
        ("Z 3312(2)", "3312(2)"),
        ("z3312(2)", "3312(2)"),
    ]:
        check("normalize " + raw, expected, normalize_zone_id(raw))

    data = json.loads(ZONES_PATH.read_text(encoding="utf-8"))
    check("zones count", 238, len(data))
    js_text = (ROOT / "data" / "zones-depeche.js").read_text(encoding="utf-8")
    embedded = json.loads(js_text.split("=", 1)[1].strip().rstrip(";"))
    check("embedded js matches json", True, embedded == data)

    html = INDEX_PATH.read_text(encoding="utf-8")
    check("zones js included", True, 'src="data/zones-depeche.js"' in html)
    check("boissy offset global 25000", True, "[BRANCH_IDS.BOISSY]: 25000" in html)
    check("fontenay fork 31500 used for depeche access", True, "const fontenayForkPk = BOISSY_BRANCH_OFFSET;" in html)

    chessy_29 = [
        z for z in data
        if z["branche"] == "chessy" and 29000 <= z["pkStart"] < 30000
    ]
    check("chessy 29.xxx count", True, len(chessy_29) >= 1)
    for z in chessy_29:
        branch = access_search_branch_for_zone(z["pkStart"], z["pkEnd"], z["branche"])
        check(
            f"chessy {z['zone']} ({z['pkStart']}-{z['pkEnd']}) uses trunk before Fontenay",
            "central",
            branch,
        )

    check(
        "chessy after Fontenay fork stays chessy",
        "chessy",
        access_search_branch_for_zone(34525, 34650, "chessy"),
    )
    check(
        "boissy zone stays boissy",
        "boissy",
        access_search_branch_for_zone(32170, 32250, "boissy"),
    )

    for query in ["1323A", "Z1323A", "Z 1323A", "z 1323a"]:
        hits = search_zones(query, data)["exact"]
        check("exact " + query + " count", 1, len(hits))
        if hits:
            z = hits[0]
            check("exact " + query + " zone", "Z 1323A", z["zone"])
            check("exact " + query + " voie", "1", z["voie"])
            check("exact " + query + " pkStart", 32170, z["pkStart"])
            check("exact " + query + " pkEnd", 32250, z["pkEnd"])
            check("exact " + query + " display start", "7.170", format_depeche_pk(z["pkStart"], z["branche"]))
            check("exact " + query + " display end", "7.250", format_depeche_pk(z["pkEnd"], z["branche"]))

    for query in ["3312(2)", "Z3312(2)", "Z 3312(2)"]:
        hits = search_zones(query, data)["exact"]
        check("exact " + query + " count", 1, len(hits))
        if hits:
            z = hits[0]
            check("exact " + query + " zone", "Z 3312(2)", z["zone"])
            check("exact " + query + " voie", "2", z["voie"])
            check("exact " + query + " pkStart", 54650, z["pkStart"])
            check("exact " + query + " pkEnd", 55050, z["pkEnd"])
            check("exact " + query + " display start", "54.650", format_depeche_pk(z["pkStart"], z["branche"]))
            check("exact " + query + " display end", "55.050", format_depeche_pk(z["pkEnd"], z["branche"]))

    prefix = search_zones("3312", data)
    check("prefix 3312 exact empty", 0, len(prefix["exact"]))
    check("prefix 3312 similar names", ["Z 3312(2)", "Z 3312(1)"], [z["zone"] for z in prefix["similar"]])

    miss = []
    for zone in data:
        key = zone["zoneKey"]
        variants = [
            zone["zone"],
            zone["zone"].lower(),
            zone["zone"].replace(" ", ""),
            zone["zone"].replace(" ", "").lower(),
            key,
            key.lower(),
            "z " + key,
            "Z" + key,
            "z" + key.lower(),
            "Z " + key.lower(),
        ]
        for raw in variants:
            hits = search_zones(raw, data)["exact"]
            if len(hits) != 1 or hits[0]["zoneKey"] != key:
                miss.append((raw, key))
    check("all 238 zones found in every input variant", 0, len(miss))

    missing = search_zones("9999Z", data)
    check("unknown exact", 0, len(missing["exact"]))
    check("unknown similar", 0, len(missing["similar"]))

    check("interval inside", 0.0, distance_pk_to_interval(10300, 10000, 10500))
    check("interval before", 100.0, distance_pk_to_interval(9900, 10000, 10500))
    check("interval after", 200.0, distance_pk_to_interval(10700, 10000, 10500))

    check("ui has depeche button", True, 'id="btnSearchModeDepeche"' in html)
    check("ui keeps pk button", True, 'id="btnSearchModePk"' in html)
    check("ui keeps poteau button", True, 'id="btnSearchModePoteau"' in html)
    check("pk lookup still dispatched", True, "handlePkLookup()" in html)
    check("poteau lookup still dispatched", True, "handlePoteauLookup()" in html)
    check("depeche lookup dispatched", True, "handleDepecheLookup()" in html)

    if failed:
        print(f"\n{len(failed)} échec(s)")
        return 1
    print("\nTous les tests Dépêche sont OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
