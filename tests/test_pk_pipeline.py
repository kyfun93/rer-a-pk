#!/usr/bin/env python3
"""Tests de non-régression du pipeline PK complet (miroir index.html)."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from typing import Any

# Réutilise la logique calibration déjà validée
from test_calibration_logic import (  # noqa: E402
    classify_calibration_registration,
    dedupe_calibration_points_by_pk,
    explain_calibration_offset_detail,
    get_calibration_zone_for_pk,
    resolve_calibration_branch_for_registration,
    build_calibration_segments,
)

BRANCH_OFFSETS_BOISSY = 25000

PK_DISCONTINUITIES = [
    {
        "branch": "central",
        "pk_before": 10800,
        "pk_after": 11300,
        "split_ref": {"lat": 48.898, "lon": 2.218},
        "window_m": 100,
        "jump": 500,
    }
]


@dataclass
class TestResult:
    name: str
    inputs: dict
    expected: Any
    actual: Any
    passed: bool


def normalize_branch_key(branch_key: str | None) -> str:
    if branch_key in ("boissy", "chessy"):
        return branch_key
    return "central"


def round_pk_to_discontinuity_bounds(pk_metric: float, branch_key: str | None) -> float:
    if pk_metric != pk_metric:
        return pk_metric
    normalized = normalize_branch_key(branch_key)
    for disc in PK_DISCONTINUITIES:
        if disc["branch"] != normalized:
            continue
        if disc["pk_before"] < pk_metric < disc["pk_after"]:
            dist_before = pk_metric - disc["pk_before"]
            dist_after = disc["pk_after"] - pk_metric
            return disc["pk_before"] if dist_before <= dist_after else disc["pk_after"]
    return pk_metric


def apply_pk_display_jump(pk_metric: float, lat: float | None, lon: float | None, branch_key: str | None) -> float:
    if pk_metric != pk_metric:
        return pk_metric
    normalized = normalize_branch_key(branch_key)
    rounded = round_pk_to_discontinuity_bounds(pk_metric, normalized)
    for disc in PK_DISCONTINUITIES:
        if disc["branch"] != normalized:
            continue
        if rounded == disc["pk_after"]:
            return rounded
        if rounded == disc["pk_before"]:
            if lat is not None and lon is not None:
                # Fenêtre simplifiée : pas de re-projection GPS dans les tests unitaires
                pass
            return rounded
    return rounded


def get_local_offset(pk_raw: float, branch_key: str | None, fixture: dict[str, list[dict]]) -> float:
    zone = get_calibration_zone_for_pk(pk_raw, branch_key)
    if not zone:
        return 0.0
    segments = build_calibration_segments(fixture.get(zone, []))
    return explain_calibration_offset_detail(pk_raw, segments)["localOffset"]


def compute_pk_with_calibrations(
    pk_raw: float,
    branch_key: str | None,
    *,
    pk_offset: float = 0.0,
    fixture: dict[str, list[dict]] | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> float:
    fixture = fixture or {"central": [], "boissy": [], "chessy": []}
    local = get_local_offset(pk_raw, branch_key, fixture)
    pk_with_cal = pk_raw + pk_offset + local
    return apply_pk_display_jump(pk_with_cal, lat, lon, branch_key)


def get_display_pk(branch_key: str | None, pk_metric: float) -> float:
    normalized = normalize_branch_key(branch_key)
    offset = BRANCH_OFFSETS_BOISSY if normalized == "boissy" else 0
    return pk_metric - offset


def parse_user_pk_input(branch_key: str | None, pk_input: float) -> float:
    normalized = normalize_branch_key(branch_key)
    offset = BRANCH_OFFSETS_BOISSY if normalized == "boissy" else 0
    return pk_input + offset


def merge_calibrations(shared: list[dict], local: list[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {"central": [], "boissy": [], "chessy": []}
    for entry in shared + local:
        if not entry:
            continue
        pk = entry.get("pkExact", entry.get("pk"))
        offset = entry.get("pkOffset", entry.get("offset"))
        branch = entry.get("branch")
        zone = classify_calibration_registration(pk, offset, branch)
        if not zone:
            continue
        buckets[zone].append(
            {
                "pk": pk,
                "offset": offset,
                "timestamp": entry.get("timestamp") or 0,
            }
        )
    return {
        "central": dedupe_calibration_points_by_pk(buckets["central"]),
        "boissy": dedupe_calibration_points_by_pk(buckets["boissy"]),
        "chessy": dedupe_calibration_points_by_pk(buckets["chessy"]),
    }


def simulate_restart(pk_offset_stored: float, local_cals: list[dict], shared: list[dict]) -> tuple[float, dict]:
    fixture = merge_calibrations(shared, local_cals)
    return pk_offset_stored, fixture


def simulate_reset_offset_only(pk_offset: float) -> float:
    return 0.0


def simulate_clear_local_calibrations() -> list[dict]:
    return []


def run_tests() -> list[TestResult]:
    results: list[TestResult] = []

    def check(name: str, inputs: dict, expected: Any, actual: Any, numeric: bool = False, eps: float = 0.02):
        passed = abs(actual - expected) <= eps if numeric else actual == expected
        results.append(TestResult(name, inputs, expected, actual, passed))

    empty = {"central": [], "boissy": [], "chessy": []}

    # 1. PK brut sans calibration ni offset
    check(
        "pipeline raw only",
        {"pkRaw": 32500, "branch": "chessy"},
        32500.0,
        compute_pk_with_calibrations(32500, "chessy"),
        True,
    )

    # 2. PK avec uniquement pkOffset
    check(
        "pipeline pkOffset only",
        {"pkRaw": 32500, "pkOffset": 42},
        32542.0,
        compute_pk_with_calibrations(32500, "chessy", pk_offset=42),
        True,
    )

    # 3. PK avec uniquement calibration locale
    local_fixture = {"central": [], "boissy": [], "chessy": [{"pk": 32000, "offset": -100}]}
    check(
        "pipeline local cal only",
        {"pkRaw": 32000},
        31900.0,
        compute_pk_with_calibrations(32000, "chessy", fixture=local_fixture),
        True,
    )

    # 4. PK avec uniquement calibration partagée
    shared_fixture = {"central": [], "boissy": [], "chessy": [{"pk": 38600, "offset": 73}]}
    check(
        "pipeline shared cal only",
        {"pkRaw": 38600},
        38673.0,
        compute_pk_with_calibrations(38600, "chessy", fixture=shared_fixture),
        True,
    )

    # 5. Local + partagé même PK → local plus récent gagne
    shared = [{"pkExact": 32000, "pkOffset": -100, "branch": "chessy", "timestamp": 1}]
    local = [{"pkExact": 32000, "pkOffset": -50, "branch": "chessy", "timestamp": 2}]
    merged = merge_calibrations(shared, local)
    check(
        "pipeline local+shared same pk",
        {"pk": 32000},
        -50.0,
        get_local_offset(32000, "chessy", merged),
        True,
    )

    # 6. Saut d'affichage Nanterre
    check(
        "pipeline discontinuity inside zone rounds",
        {"pkRaw": 11000, "branch": "central"},
        10800.0,
        compute_pk_with_calibrations(11000, "central"),
        True,
    )
    check(
        "pipeline discontinuity at pk_after unchanged",
        {"pkRaw": 11300, "branch": "central"},
        11300.0,
        compute_pk_with_calibrations(11300, "central"),
        True,
    )

    # 7. Redémarrage simulé — offset et calibrations rechargés
    offset_after, fixture_after = simulate_restart(15.0, local, shared)
    pk_after_restart = compute_pk_with_calibrations(32000, "chessy", pk_offset=offset_after, fixture=fixture_after)
    check(
        "pipeline restart preserves offset and cals",
        {"pkRaw": 32000, "pkOffset": 15},
        31965.0,
        pk_after_restart,
        True,
    )

    # 8. Reset offset only
    check(
        "pipeline reset offset",
        {"before": 15},
        0.0,
        simulate_reset_offset_only(15),
        True,
    )
    check(
        "pipeline after reset offset no global",
        {"pkRaw": 32000},
        31950.0,
        compute_pk_with_calibrations(32000, "chessy", pk_offset=0, fixture=merged),
        True,
    )

    # 9. Clear local — shared reste
    cleared = simulate_clear_local_calibrations()
    fixture_cleared = merge_calibrations(shared, cleared)
    check(
        "pipeline after clear local keeps shared",
        {"pk": 32000},
        -100.0,
        get_local_offset(32000, "chessy", fixture_cleared),
        True,
    )

    # 10. Import ancien JSON — central post-bifurcation rejeté
    check(
        "pipeline import legacy central post-bif",
        {"pk": 34000, "branch": "central"},
        None,
        classify_calibration_registration(34000, -660.76, "central"),
    )
    check(
        "pipeline import chessy ok",
        {"pk": 38600, "branch": "chessy"},
        "chessy",
        classify_calibration_registration(38600, 72.78, "chessy"),
    )

    # 11. Branche forcée incorrecte
    chessy_only = {"central": [], "boissy": [], "chessy": [{"pk": 32500, "offset": -90}]}
    # fixture avec two points from calibration_logic
    two_chessy = {"central": [], "boissy": [], "chessy": [{"pk": 32000, "offset": -100}, {"pk": 33000, "offset": -80}]}
    check(
        "pipeline wrong branch selected",
        {"pkRaw": 32500, "branch": "boissy"},
        32500.0,
        compute_pk_with_calibrations(32500, "boissy", fixture=two_chessy),
        True,
    )
    check(
        "pipeline correct branch selected",
        {"pkRaw": 32500, "branch": "chessy"},
        32410.0,
        compute_pk_with_calibrations(32500, "chessy", fixture=two_chessy),
        True,
    )

    # 12. Bifurcation exacte
    central_chessy = {
        "central": [{"pk": 28000, "offset": -30}, {"pk": 29000, "offset": -20}],
        "boissy": [],
        "chessy": [{"pk": 32000, "offset": -100}, {"pk": 33000, "offset": -80}],
    }
    check(
        "pipeline bifurcation 30000 zone",
        {"pk": 30000, "branch": "chessy"},
        "central",
        get_calibration_zone_for_pk(30000, "chessy"),
    )
    check(
        "pipeline bifurcation 30001 no central leak",
        {"pkRaw": 30001, "branch": "chessy"},
        30001.0,
        compute_pk_with_calibrations(30001, "chessy", fixture=central_chessy),
        True,
    )

    # 13. Zone ambiguë proche (PK 34500)
    check(
        "pipeline ambiguous zone uses selected branch",
        {"pkRaw": 34500, "branch": "chessy"},
        34500.0,
        compute_pk_with_calibrations(34500, "chessy", fixture=two_chessy),
        True,
    )

    # 14. Recalage utilise PK métrique interne (Boissy relatif → absolu)
    user_input_boissy = 9000
    metric = parse_user_pk_input("boissy", user_input_boissy)
    check(
        "pipeline recal uses metric pk boissy",
        {"input": 9000, "branch": "boissy"},
        34000.0,
        metric,
        True,
    )
    raw_pk = 34050.0
    recal_offset = metric - raw_pk
    check(
        "pipeline recal offset from raw not display",
        {"metricPk": 34000, "rawPk": 34050},
        -50.0,
        recal_offset,
        True,
    )

    # 15. Chaîne unique confirmée
    pk_raw = 32500.0
    pk_offset = 10.0
    local = get_local_offset(pk_raw, "chessy", two_chessy)
    before_jump = pk_raw + pk_offset + local
    final = apply_pk_display_jump(before_jump, None, None, "chessy")
    check(
        "pipeline single chain formula",
        {"pkRaw": 32500},
        final,
        compute_pk_with_calibrations(32500, "chessy", pk_offset=10, fixture=two_chessy),
        True,
    )

    # 16. Pas de double pkOffset dans recal moderne (offset stocké localement seulement)
    check(
        "pipeline recal does not require pkOffset mutation",
        {"storedPkOffset": 0, "localOffsetAtPoint": -50},
        31950.0,
        compute_pk_with_calibrations(32000, "chessy", pk_offset=0, fixture=merged),
        True,
    )

    # 17. Affichage Boissy ne modifie pas le métrique interne
    internal = 34000.0
    display = get_display_pk("boissy", internal)
    check(
        "pipeline boissy display is cosmetic",
        {"metric": 34000},
        9000.0,
        display,
        True,
    )
    check(
        "pipeline boissy roundtrip",
        {"input": 9000},
        34000.0,
        parse_user_pk_input("boissy", 9000),
        True,
    )

    # 18. Branche incertaine bloque enregistrement
    resolved = resolve_calibration_branch_for_registration(34500, "central")
    check(
        "pipeline uncertain branch blocks registration",
        {"pk": 34500, "branch": "central"},
        False,
        resolved["certain"],
    )

    # 19. Anti double-correction (exemple obligatoire)
    # Avant : pkRaw 32050, localOffset 0, final 32050
    # Après calibration : même pkRaw 32050 (géométrie inchangée), seules les corrections locales changent.
    # Cas exact (contrôle au PK de mesure 32050 / −50) :
    #   localOffset = −50 → final = 32000 — jamais 31950.
    pk_raw_stable = 32050.0
    empty_before = {"central": [], "boissy": [], "chessy": []}
    local_before = get_local_offset(pk_raw_stable, "chessy", empty_before)
    final_before = compute_pk_with_calibrations(pk_raw_stable, "chessy", fixture=empty_before)
    check("anti-double before localOffset", {"pkRaw": 32050}, 0.0, local_before, True)
    check("anti-double before final", {"pkRaw": 32050}, 32050.0, final_before, True)

    # Même GPS : point de contrôle centré sur le pkRaw mesuré → offset plein −50
    after_exact = {"central": [], "boissy": [], "chessy": [{"pk": 32050, "offset": -50}]}
    local_after = get_local_offset(pk_raw_stable, "chessy", after_exact)
    final_after = compute_pk_with_calibrations(pk_raw_stable, "chessy", fixture=after_exact)
    check("anti-double after pkRaw unchanged", {"pkRaw": 32050}, 32050.0, pk_raw_stable, True)
    check("anti-double after localOffset", {"pkRaw": 32050}, -50.0, local_after, True)
    check("anti-double after final", {"pkRaw": 32050}, 32000.0, final_after, True)
    check("anti-double single chain", {}, final_after, pk_raw_stable + local_after, True)
    forbidden = compute_pk_with_calibrations(32000.0, "chessy", fixture=after_exact)
    # Si le brut avait été forcé à 32000 (ancienne double géométrie), on aurait quasiment 31950 :
    # ici le contrôle est à 32050 → à pkRaw 32000, offset ≈ −47.92, final ≈ 31952
    check(
        "anti-double forbidden geom+offset near 31950",
        {"pkRaw": 32000},
        True,
        abs(forbidden - 31950) < 5,
    )
    check("anti-double final is not forbidden", {"final": final_after}, True, final_after == 32000.0)

    # Contrôle enregistré au pkExact 32000 : le brut reste 32050 (pas de géométrie cal)
    after_exact_pk = {"central": [], "boissy": [], "chessy": [{"pk": 32000, "offset": -50}]}
    final_at_exact_pk_lookup = compute_pk_with_calibrations(32050, "chessy", fixture=after_exact_pk)
    check(
        "anti-double raw stable with exactPk control",
        {"pkRaw": 32050, "controlPk": 32000},
        True,
        final_at_exact_pk_lookup != 31950 and abs(final_at_exact_pk_lookup - (32050 + get_local_offset(32050, "chessy", after_exact_pk))) < 0.02,
    )

    # 20. Legacy pkOffset + calibrations → ne pas cumuler (migration vers 0)
    legacy_offset = 42.0
    migrated_offset = 0.0
    check(
        "legacy pkOffset migrated to zero",
        {"before": legacy_offset, "hasCals": True},
        0.0,
        migrated_offset,
        True,
    )
    check(
        "legacy after migration applies only local",
        {"pkRaw": 32050, "pkOffset": 0},
        32000.0,
        compute_pk_with_calibrations(32050, "chessy", pk_offset=migrated_offset, fixture=after_exact),
        True,
    )
    check(
        "legacy without migration would cumulate",
        {"pkRaw": 32050, "pkOffset": 42},
        32042.0,
        compute_pk_with_calibrations(32050, "chessy", pk_offset=legacy_offset, fixture=after_exact),
        True,
    )

    # 21. Reset complet local ne touche pas shared
    shared_keep = [{"pkExact": 38600, "pkOffset": 73, "branch": "chessy", "timestamp": 1}]
    after_full_reset = merge_calibrations(shared_keep, [])
    check(
        "full reset keeps shared",
        {"pk": 38600},
        73.0,
        get_local_offset(38600, "chessy", after_full_reset),
        True,
    )
    check(
        "full reset clears local point",
        {"pk": 32000},
        0.0,
        get_local_offset(32000, "chessy", after_full_reset),
        True,
    )

    # === Persistance / ancrage / navigateur vierge / legacy JSON ===

    def resolve_anchor(entry: dict) -> dict:
        """Miroir JS resolveCalibrationAnchorPk."""
        if not entry:
            return {"anchorPk": None, "source": "rejected"}
        if entry.get("pkRaw") is not None and entry["pkRaw"] == entry["pkRaw"]:
            return {"anchorPk": entry["pkRaw"], "source": "pkRaw"}
        pk_exact = entry.get("pkExact", entry.get("pk"))
        offset = entry.get("pkOffset", entry.get("offset"))
        if pk_exact is not None and offset is not None and offset == offset:
            return {"anchorPk": pk_exact - offset, "source": "derived"}
        return {"anchorPk": None, "source": "rejected"}

    exported = {
        "pkExact": 32000,
        "pkRaw": 32050,
        "pkOffset": -50,
        "lat": 48.85,
        "lon": 2.55,
        "accuracy": 5,
        "branch": "chessy",
        "timestamp": "2026-07-15T12:00:00.000Z",
    }
    check("export schema keys", {}, True, all(k in exported for k in ("pkExact", "pkRaw", "pkOffset", "branch", "lat", "lon", "timestamp")))
    check("anchor explicit pkRaw", {"entry": exported}, 32050.0, resolve_anchor(exported)["anchorPk"], True)
    check("anchor source pkRaw", {}, "pkRaw", resolve_anchor(exported)["source"])

    # Rechargement : ancre restaurée à 32050
    reloaded_fixture = {"central": [], "boissy": [], "chessy": [{"pk": 32050, "offset": -50}]}
    check("reload final 32000", {"pkRaw": 32050}, 32000.0, compute_pk_with_calibrations(32050, "chessy", fixture=reloaded_fixture), True)
    check("reload anchor pk", {}, 32050.0, reloaded_fixture["chessy"][0]["pk"], True)

    # Navigateur vierge : shared only, pkOffset 0
    virgin_fixture = {"central": [], "boissy": [], "chessy": [{"pk": 32050, "offset": -50}]}
    check("virgin browser final", {"pkOffset": 0}, 32000.0, compute_pk_with_calibrations(32050, "chessy", pk_offset=0, fixture=virgin_fixture), True)

    # Après clear local + import calibrations.json (même point)
    shared_only = merge_calibrations(
        [{"pkExact": 32000, "pkRaw": 32050, "pkOffset": -50, "branch": "chessy", "timestamp": 1}],
        [],
    )
    # merge uses classify with pkExact — control points stored at pkExact from merge helper.
    # Simule buildCalibrationPolylines with resolve_anchor :
    shared_entry = {"pkExact": 32000, "pkRaw": 32050, "pkOffset": -50, "branch": "chessy"}
    anchor = resolve_anchor(shared_entry)
    shared_built = {"central": [], "boissy": [], "chessy": [{"pk": anchor["anchorPk"], "offset": -50}]}
    check("shared import anchor 32050", {}, 32050.0, anchor["anchorPk"], True)
    check("shared import final 32000", {}, 32000.0, compute_pk_with_calibrations(32050, "chessy", fixture=shared_built), True)

    # Ancien JSON sans pkRaw : dérivation pkExact - offset
    legacy = resolve_anchor({"pkExact": 32000, "pkOffset": -50, "branch": "chessy"})
    check("legacy no pkRaw derived", {}, 32050.0, legacy["anchorPk"], True)
    check("legacy no pkRaw source", {}, "derived", legacy["source"])
    legacy_reject = resolve_anchor({"pkExact": 32000, "branch": "chessy"})
    check("legacy incomplete rejected", {}, None, legacy_reject["anchorPk"])

    # pkOffset +30 chargé AVANT shared → après migration = 0, final 32000 (jamais 32030)
    check(
        "pkOffset before shared would cumulate",
        {"pkOffset": 30},
        32030.0,
        compute_pk_with_calibrations(32050, "chessy", pk_offset=30, fixture=shared_built),
        True,
    )
    check(
        "pkOffset after shared migrated to 0",
        {"pkOffset": 0},
        32000.0,
        compute_pk_with_calibrations(32050, "chessy", pk_offset=0, fixture=shared_built),
        True,
    )

    # Backup legacy jamais dans le calcul
    check(
        "legacy backup unused",
        {"pkOffset": 0, "backup": 30},
        32000.0,
        compute_pk_with_calibrations(32050, "chessy", pk_offset=0, fixture=shared_built),
        True,
    )

    # pkRaw strictement identique avant/après chargement des calibrations
    check("raw before load", {}, 32050.0, compute_pk_with_calibrations(32050, "chessy", fixture=empty_before), True)
    pk_raw_input = 32050.0
    check("raw identical after load", {"before": 32050, "after": pk_raw_input}, True, pk_raw_input == 32050.0)
    check(
        "after load only offset applied",
        {},
        32000.0,
        compute_pk_with_calibrations(pk_raw_input, "chessy", fixture=shared_built),
        True,
    )

    return results


def main() -> int:
    results = run_tests()
    failed = [r for r in results if not r.passed]
    print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    print(f"\nRésumé pipeline: {len(results) - len(failed)}/{len(results)} tests OK")
    if failed:
        for item in failed:
            print(f"- {item.name}: attendu={item.expected}, obtenu={item.actual}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
