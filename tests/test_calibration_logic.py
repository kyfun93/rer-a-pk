#!/usr/bin/env python3
"""Vérification complète de la logique calibration PK (miroir index.html)."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from typing import Any

CALIBRATION_SINGLE_RADIUS = 1200
BRANCH_COMMON_MAX = 30000
BRANCH_CHESSY_MIN = 31795
BRANCH_BOISSY_MIN = 32750
BRANCH_BOISSY_MAX = 47200
BRANCH_CHESSY_MAX = 59700


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


def detect_branch_for_pk(pk: float) -> str:
    if pk <= BRANCH_COMMON_MAX:
        return "central"
    if BRANCH_CHESSY_MIN <= pk < BRANCH_BOISSY_MIN:
        return "chessy"
    if BRANCH_BOISSY_MIN <= pk <= BRANCH_BOISSY_MAX:
        boissy_stations = [34000, 35600, 37500, 38500, 40300, 41800, 44500, 47200]
        chessy_stations = [34525, 36750, 37950, 39850, 42150, 44850]
        min_boissy = min(abs(pk - s) for s in boissy_stations)
        min_chessy = min(abs(pk - s) for s in chessy_stations)
        return "boissy" if min_boissy < min_chessy else "chessy"
    if BRANCH_BOISSY_MAX < pk <= BRANCH_CHESSY_MAX:
        return "chessy"
    return "central"


def resolve_calibration_branch_for_registration(pk: float, branch_hint: str | None) -> dict:
    if pk != pk:
        return {"branch": None, "certain": False}
    if pk <= BRANCH_COMMON_MAX:
        return {"branch": "central", "certain": True}
    if branch_hint in ("chessy", "boissy"):
        return {"branch": branch_hint, "certain": True}
    return {"branch": None, "certain": False}


def classify_calibration_registration(pk: float, offset: float, branch_hint: str | None) -> str | None:
    if pk != pk or offset != offset:
        return None
    resolved = resolve_calibration_branch_for_registration(pk, branch_hint)
    if not resolved["certain"] or not resolved["branch"]:
        return None
    if resolved["branch"] == "central":
        return "central" if pk <= BRANCH_COMMON_MAX else None
    if pk <= BRANCH_COMMON_MAX:
        return None
    return resolved["branch"]


def get_calibration_zone_for_pk(pk: float, branch_key: str | None) -> str | None:
    if pk != pk:
        return None
    if pk <= BRANCH_COMMON_MAX:
        return "central"
    normalized = normalize_branch_key(branch_key)
    if normalized in ("boissy", "chessy"):
        return normalized
    return detect_branch_for_pk(pk)


def dedupe_calibration_points_by_pk(points: list[dict]) -> list[dict]:
    by_pk: dict[float, dict] = {}
    for point in points:
        if point is None or point.get("pk") is None or point.get("offset") is None:
            continue
        pk = point["pk"]
        existing = by_pk.get(pk)
        if not existing or (point.get("timestamp") or 0) >= (existing.get("timestamp") or 0):
            by_pk[pk] = point
    return sorted(by_pk.values(), key=lambda p: p["pk"])


def build_calibration_segments(points: list[dict]) -> list[dict]:
    sorted_points = dedupe_calibration_points_by_pk(points)
    if not sorted_points:
        return []
    if len(sorted_points) == 1:
        center = sorted_points[0]
        return [{
            "type": "single",
            "center": center,
            "start": center["pk"] - CALIBRATION_SINGLE_RADIUS,
            "end": center["pk"] + CALIBRATION_SINGLE_RADIUS,
            "radius": CALIBRATION_SINGLE_RADIUS,
        }]
    segments = []
    first = sorted_points[0]
    last = sorted_points[-1]
    segments.append({
        "type": "ramp",
        "start": first["pk"] - CALIBRATION_SINGLE_RADIUS,
        "end": first["pk"],
        "offsetStart": 0,
        "offsetEnd": first["offset"],
    })
    for left, right in zip(sorted_points, sorted_points[1:]):
        if right["pk"] <= left["pk"]:
            continue
        segments.append({"type": "pair", "left": left, "right": right})
    segments.append({
        "type": "ramp",
        "start": last["pk"],
        "end": last["pk"] + CALIBRATION_SINGLE_RADIUS,
        "offsetStart": last["offset"],
        "offsetEnd": 0,
    })
    return segments


def explain_calibration_offset_detail(pk: float, segments: list[dict]) -> dict:
    for segment in segments:
        if segment["type"] == "pair":
            left = segment["left"]
            right = segment["right"]
            if pk < left["pk"] or pk > right["pk"]:
                continue
            span = right["pk"] - left["pk"]
            t = (pk - left["pk"]) / span
            return {
                "segmentType": "pair",
                "interpolationFactor": t,
                "localOffset": left["offset"] + (right["offset"] - left["offset"]) * t,
                "controlPoints": [
                    {"pk": left["pk"], "offset": left["offset"]},
                    {"pk": right["pk"], "offset": right["offset"]},
                ],
            }
        if segment["type"] == "ramp":
            if pk < segment["start"] or pk > segment["end"]:
                continue
            span = segment["end"] - segment["start"]
            t = (pk - segment["start"]) / span
            is_head = segment["offsetStart"] == 0
            is_tail = segment["offsetEnd"] == 0
            segment_type = "ramp-head" if is_head else ("ramp-tail" if is_tail else "ramp")
            return {
                "segmentType": segment_type,
                "interpolationFactor": t,
                "localOffset": segment["offsetStart"] + (segment["offsetEnd"] - segment["offsetStart"]) * t,
                "controlPoints": [
                    {"pk": segment["start"], "offset": segment["offsetStart"]},
                    {"pk": segment["end"], "offset": segment["offsetEnd"]},
                ],
            }
        if segment["type"] == "single":
            if pk < segment["start"] or pk > segment["end"]:
                continue
            dist = abs(pk - segment["center"]["pk"])
            factor = max(0.0, 1 - dist / segment["radius"])
            return {
                "segmentType": "single",
                "interpolationFactor": factor,
                "localOffset": segment["center"]["offset"] * factor,
                "controlPoints": [{"pk": segment["center"]["pk"], "offset": segment["center"]["offset"]}],
            }
    return {"segmentType": "none", "interpolationFactor": None, "localOffset": 0.0, "controlPoints": []}


def diagnose(pk_raw: float, branch_key: str | None, fixture: dict[str, list[dict]], global_offset: float = 0.0) -> dict:
    zone = get_calibration_zone_for_pk(pk_raw, branch_key)
    segments = build_calibration_segments(fixture.get(zone or "", []))
    detail = explain_calibration_offset_detail(pk_raw, segments)
    return {
        "pkRaw": pk_raw,
        "branchKey": branch_key,
        "zone": zone,
        "segmentType": detail["segmentType"],
        "controlPoints": detail["controlPoints"],
        "interpolationFactor": detail["interpolationFactor"],
        "localOffset": detail["localOffset"],
        "globalOffset": global_offset,
        "pkFinal": pk_raw + global_offset + detail["localOffset"],
    }


def offset(pk: float, branch: str, fixture: dict[str, list[dict]]) -> float:
    return diagnose(pk, branch, fixture)["localOffset"]


def approx(actual: float, expected: float, epsilon: float = 0.02) -> bool:
    return abs(actual - expected) <= epsilon


def run_tests() -> list[TestResult]:
    results: list[TestResult] = []

    def check(name: str, inputs: dict, expected: Any, actual: Any, numeric: bool = False, epsilon: float = 0.02):
        passed = approx(actual, expected, epsilon) if numeric else actual == expected
        results.append(TestResult(name, inputs, expected, actual, passed))

    zones = ["central", "chessy", "boissy"]
    single = {
        "central": {"pk": 28000, "offset": -30},
        "chessy": {"pk": 32000, "offset": -100},
        "boissy": {"pk": 34000, "offset": 40},
    }
    two_point = {
        "central": [{"pk": 28000, "offset": -30}, {"pk": 29000, "offset": -20}],
        "chessy": [{"pk": 32000, "offset": -100}, {"pk": 33000, "offset": -80}],
        "boissy": [{"pk": 34000, "offset": 40}, {"pk": 35000, "offset": 20}],
    }

    for zone in zones:
        empty_fixture = {"central": [], "boissy": [], "chessy": []}
        sample_pk = 25000 if zone == "central" else (32500 if zone == "chessy" else 34500)
        branch = zone if zone != "central" else "central"
        check(f"zero {zone}", {"pk": sample_pk, "branch": branch}, 0.0, offset(sample_pk, branch, empty_fixture), True)

    for zone, point in single.items():
        fixture = {"central": [], "boissy": [], "chessy": []}
        fixture[zone] = [point]
        branch = zone if zone != "central" else "central"
        check(f"single {zone} @point", {"pk": point["pk"], "branch": branch}, point["offset"], offset(point["pk"], branch, fixture), True)
        check(f"single {zone} -1200", {"pk": point["pk"] - 1200}, 0.0, offset(point["pk"] - 1200, branch, fixture), True)
        check(f"single {zone} +1200", {"pk": point["pk"] + 1200}, 0.0, offset(point["pk"] + 1200, branch, fixture), True)
        check(f"single {zone} +300", {"pk": point["pk"] + 300}, point["offset"] * 0.75, offset(point["pk"] + 300, branch, fixture), True)

    for zone, points in two_point.items():
        fixture = {"central": [], "boissy": [], "chessy": []}
        fixture[zone] = points
        branch = zone if zone != "central" else "central"
        p0, p1 = points
        check(f"double {zone} head", {"pk": p0["pk"] - 1200}, 0.0, offset(p0["pk"] - 1200, branch, fixture), True)
        check(f"double {zone} tail", {"pk": p1["pk"] + 1200}, 0.0, offset(p1["pk"] + 1200, branch, fixture), True)
        check(f"double {zone} junction first", {"pk": p0["pk"]}, p0["offset"], offset(p0["pk"], branch, fixture), True)
        check(f"double {zone} junction last", {"pk": p1["pk"]}, p1["offset"], offset(p1["pk"], branch, fixture), True)
        mid = (p0["pk"] + p1["pk"]) / 2
        expected_mid = p0["offset"] + (p1["offset"] - p0["offset"]) * 0.5
        check(f"double {zone} mid", {"pk": mid}, expected_mid, offset(mid, branch, fixture), True)

    for zone, points in two_point.items():
        fixture = {"central": [], "boissy": [], "chessy": []}
        third = {"pk": points[1]["pk"] + 1000, "offset": points[1]["offset"] / 2}
        fixture[zone] = points + [third]
        branch = zone if zone != "central" else "central"
        between = points[1]["pk"] + 500
        expected = points[1]["offset"] + (third["offset"] - points[1]["offset"]) * 0.5
        check(f"triple {zone}", {"pk": between}, expected, offset(between, branch, fixture), True)

    fixture = {"central": two_point["central"], "boissy": [], "chessy": two_point["chessy"]}
    check("bifurcation 30000 zone", {"pk": 30000, "branch": "chessy"}, "central", diagnose(30000, "chessy", fixture)["zone"])
    check("bifurcation 30000 offset", {"pk": 30000}, -20 + 20 * (1000 / 1200), offset(30000, "chessy", fixture), True)
    check("bifurcation 30001 zone", {"pk": 30001, "branch": "chessy"}, "chessy", diagnose(30001, "chessy", fixture)["zone"])
    check("bifurcation 30001 offset", {"pk": 30001}, 0.0, offset(30001, "chessy", fixture), True)

    fixture = {"central": [], "boissy": [], "chessy": [{"pk": 32000, "offset": -100}]}
    check("isolation chessy->central", {"pk": 29000}, 0.0, offset(29000, "central", fixture), True)
    check("isolation chessy->boissy", {"pk": 34500, "branch": "boissy"}, 0.0, offset(34500, "boissy", fixture), True)

    fixture = {"central": [{"pk": 29000, "offset": -20}], "boissy": [], "chessy": []}
    check("isolation central->chessy", {"pk": 32500, "branch": "chessy"}, 0.0, offset(32500, "chessy", fixture), True)

    registration_cases = [
        (29000, -20, "chessy", "central"),
        (32000, -100, "chessy", "chessy"),
        (32000, -100, "central", None),
        (32000, -100, "auto", None),
        (34000, 40, "boissy", "boissy"),
        (29950, -5, "chessy", "central"),
        (30100, -10, "chessy", "chessy"),
        (30100, -10, "central", None),
    ]
    for pk, off, branch, expected in registration_cases:
        check(f"register {pk}/{branch}", {"pk": pk, "branch": branch}, expected, classify_calibration_registration(pk, off, branch))

    resolved = resolve_calibration_branch_for_registration(34500, "central")
    check("security uncertain", {"pk": 34500, "branch": "central"}, False, resolved["certain"])

    fixture = {"central": [], "boissy": [], "chessy": two_point["chessy"]}
    d = diagnose(31400, "chessy", fixture)
    check("segment ramp-head", {"pk": 31400}, "ramp-head", d["segmentType"])
    d = diagnose(33600, "chessy", fixture)
    check("segment ramp-tail", {"pk": 33600}, "ramp-tail", d["segmentType"])
    d = diagnose(32500, "chessy", fixture)
    check("segment pair", {"pk": 32500}, "pair", d["segmentType"])
    check("limit +1200 tail", {"pk": 34200}, 0.0, offset(34200, "chessy", fixture), True)
    check("limit +1201 tail", {"pk": 34201}, 0.0, offset(34201, "chessy", fixture), True)
    check("limit -1200 head", {"pk": 30800}, 0.0, offset(30800, "chessy", fixture), True)
    check("limit -1201 head", {"pk": 30799}, 0.0, offset(30799, "chessy", fixture), True)

    fixture = {"central": [], "boissy": [], "chessy": [
        {"pk": 32000, "offset": -100},
        {"pk": 33000, "offset": 80},
        {"pk": 34500, "offset": -150},
    ]}
    check("triple continuity 2-3", {"pk": 33750}, -35.0, offset(33750, "chessy", fixture), True)
    check("triple junction 33000", {"pk": 33000}, 80.0, offset(33000, "chessy", fixture), True)

    fixture = {"central": [], "boissy": [], "chessy": [
        {"pk": 32000, "offset": -100, "timestamp": 1},
        {"pk": 32000, "offset": -50, "timestamp": 2},
    ]}
    check("duplicate pk latest", {"pk": 32000}, -50.0, offset(32000, "chessy", fixture), True)

    fixture = {
        "central": [{"pk": 28000, "offset": -30}],
        "boissy": [],
        "chessy": [{"pk": 38600, "offset": 73}],
    }
    check("shared+local central", {"pk": 28000}, -30.0, offset(28000, "central", fixture), True)
    check("shared+local chessy", {"pk": 38600}, 73.0, offset(38600, "chessy", fixture), True)

    fixture = {"central": [], "boissy": [], "chessy": two_point["chessy"]}
    for pk, expected in [(30800, 0), (31400, -50), (32500, -90), (33600, -40), (34200, 0)]:
        check(f"doc chessy {pk}", {"pk": pk}, expected, offset(pk, "chessy", fixture), True)

    d = diagnose(34500, "both", fixture)
    check("branch both detect", {"pk": 34500, "branch": "both"}, True, d["zone"] in ("boissy", "chessy"))
    d = diagnose(34500, "chessy", fixture)
    check("branch forced chessy", {"pk": 34500, "branch": "chessy"}, "chessy", d["zone"])

    fixture_chessy_only = {"central": [], "boissy": [], "chessy": two_point["chessy"]}
    check(
        "branch mismatch chessy cal / boissy selected",
        {"pk": 32500, "branch": "boissy"},
        0.0,
        offset(32500, "boissy", fixture_chessy_only),
        True,
    )
    check(
        "branch mismatch chessy cal / chessy selected",
        {"pk": 32500, "branch": "chessy"},
        -90.0,
        offset(32500, "chessy", fixture_chessy_only),
        True,
    )

    buckets = {"central": [], "boissy": [], "chessy": []}
    for pk, off, branch, expected_zone in [
        (29950, -5, "chessy", "central"),
        (30100, -10, "chessy", "chessy"),
    ]:
        zone = classify_calibration_registration(pk, off, branch)
        if expected_zone == "central":
            buckets["central"].append({"pk": pk, "offset": off})
        elif expected_zone == "chessy":
            buckets["chessy"].append({"pk": pk, "offset": off})
    check("near bifurcation buckets", {}, True, len(buckets["central"]) == 1 and len(buckets["chessy"]) == 1)

    check("import calibrations.json central rejected", {"pk": 34000, "branch": "central"}, None, classify_calibration_registration(34000, -660.76, "central"))
    check("import calibrations.json chessy ok", {"pk": 38600, "branch": "chessy"}, "chessy", classify_calibration_registration(38600, 72.78, "chessy"))

    return results


def main() -> int:
    results = run_tests()
    failed = [r for r in results if not r.passed]
    print(json.dumps([asdict(r) for r in results], ensure_ascii=False, indent=2))
    print(f"\nRésumé: {len(results) - len(failed)}/{len(results)} tests OK")
    if failed:
        print("Échecs:")
        for item in failed:
            print(f"- {item.name}: attendu={item.expected}, obtenu={item.actual}, entrées={item.inputs}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
