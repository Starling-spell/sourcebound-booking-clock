import hashlib
import ast
import json
import sys
from pathlib import Path
import pytest

SOURCE = "https://raw.githubusercontent.com/example/timetable/" + "a" * 40 + "/hours.txt"
BODY = "Demo Observatory: UTC recurring weekly hours, Monday 09:00-12:00; all other days closed."
HASH = hashlib.sha256(BODY.encode()).hexdigest()
WEEK = 1791763200  # Monday 2026-10-12 UTC


@pytest.fixture
def clock(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.warp("2026-10-05T00:00:00Z")
    direct_vm.mock_web(r".*hours.txt", {"status": 200, "body": BODY})
    direct_vm.mock_llm(r"(?s).*Compile the COMPLETE opening-hours document.*",
                       json.dumps({"status": "EXPLICIT", "days": [[[18, 24]], [], [], [], [], [], []]}))
    contract = direct_deploy("contracts/SourceBoundBookingClock.py")
    contract.create_calendar("room", "Demo Observatory", SOURCE, HASH, WEEK)
    return contract


def test_evidence_mask_and_reservation(clock):
    report = clock.get_calendar("room")
    assert report["state"] == "READY"
    assert report["text"] == BODY
    assert report["mask"].count("1") == 6
    clock.reserve("room", "b1", 18, 2)
    assert clock.get_occupancy("room").count("1") == 2
    assert clock.get_reservation("room", "b1")["evidence_root"] == report["root"]


def test_overlap(clock, direct_vm):
    clock.reserve("room", "b1", 18, 2)
    with direct_vm.expect_revert("overlapping reservation"):
        clock.reserve("room", "b2", 19, 1)
    assert clock.get_occupancy("room").count("1") == 2


def test_closed_hours(clock, direct_vm):
    with direct_vm.expect_revert("outside observed opening hours"):
        clock.reserve("room", "b1", 24, 1)
    assert clock.get_occupancy("room").count("1") == 0


def test_cancel_releases_but_no_replay(clock, direct_vm):
    clock.reserve("room", "b1", 18, 2)
    clock.cancel("room", "b1")
    assert clock.get_occupancy("room").count("1") == 0
    with direct_vm.expect_revert("spent booking ID"):
        clock.reserve("room", "b1", 18, 2)
    with direct_vm.expect_revert("not cancellable"):
        clock.cancel("room", "b1")
    clock.reserve("room", "b2", 18, 2)
    assert clock.get_reservation("room", "b1")["state"] == "CANCELLED"


def test_bound_principal(clock, direct_vm, direct_bob):
    clock.reserve("room", "b1", 18, 2)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("bound booking principal"):
        clock.cancel("room", "b1")
    assert clock.get_occupancy("room").count("1") == 2


def test_cross_calendar(clock, direct_vm):
    clock.create_calendar("other", "Demo Observatory", SOURCE, HASH, WEEK)
    clock.reserve("room", "b1", 18, 2)
    with direct_vm.expect_revert("unknown reservation in calendar"):
        clock.cancel("other", "b1")
    assert clock.get_occupancy("room").count("1") == 2
    assert clock.get_occupancy("other").count("1") == 0


def test_wrong_hash(clock, direct_vm):
    clock.create_calendar("bad", "Demo Observatory", SOURCE, "0" * 64, WEEK)
    assert clock.get_calendar("bad")["state"] == "UNAVAILABLE"
    with direct_vm.expect_revert("calendar not ready"):
        clock.reserve("bad", "b1", 18, 1)


def test_unknown(clock, direct_vm):
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*hours.txt", {"status": 200, "body": BODY})
    direct_vm.mock_llm(r"(?s).*Compile the COMPLETE opening-hours document.*",
                       json.dumps({"status": "UNKNOWN", "days": []}))
    clock.create_calendar("uncertain", "Demo Observatory", SOURCE, HASH, WEEK)
    assert clock.get_calendar("uncertain")["state"] == "AMBIGUOUS"
    with direct_vm.expect_revert("calendar not ready"):
        clock.reserve("uncertain", "b1", 18, 1)


def warp_message(contract, vm, timestamp):
    vm.warp(timestamp)
    # SDK 0.29.2 refreshes sender/origin but omits message_raw.datetime.
    module = sys.modules[object.__getattribute__(contract, "_instance").__class__.__module__]
    module.gl.message_raw["datetime"] = timestamp


def test_expired_booking(clock, direct_vm):
    warp_message(clock, direct_vm, "2026-10-12T09:00:00Z")
    with direct_vm.expect_revert("booking already started"):
        clock.reserve("room", "b1", 18, 1)


def test_started_cannot_cancel(clock, direct_vm):
    clock.reserve("room", "b1", 18, 1)
    warp_message(clock, direct_vm, "2026-10-12T09:00:00Z")
    with direct_vm.expect_revert("not cancellable"):
        clock.cancel("room", "b1")


def test_invalid_horizon_and_repeated_calendar(clock, direct_vm):
    with direct_vm.expect_revert("spent calendar ID"):
        clock.create_calendar("room", "Demo Observatory", SOURCE, HASH, WEEK)
    with direct_vm.expect_revert("future UTC Monday"):
        clock.create_calendar("wrongdate", "Demo Observatory", SOURCE, HASH, WEEK + 1800)
    with direct_vm.expect_revert("commit-pinned"):
        clock.create_calendar("wrongurl", "Demo Observatory", "https://example.com/", HASH, WEEK)


def test_bounds(clock, direct_vm):
    for first, count in [(335, 2), (-1, 1), (18, 9), (18, 0)]:
        with direct_vm.expect_revert("invalid slot range"):
            clock.reserve("room", "bounds", first, count)


def load_helpers():
    tree = ast.parse(Path("contracts/SourceBoundBookingClock.py").read_text())
    helpers = [node for node in tree.body if isinstance(node, ast.FunctionDef)
               and node.name in ("canonical", "compile_mask", "reports_match")]
    scope = {"json": json}
    exec(compile(ast.Module(body=helpers, type_ignores=[]), "helpers", "exec"), scope)
    return scope


def test_malformed_intervals():
    compile_mask = load_helpers()["compile_mask"]
    for intervals in [[[18, 25], [24, 26]], [[True, 24]], [[18, 49]], [[24, 18]]]:
        assert compile_mask({"status": "EXPLICIT", "days": [intervals, [], [], [], [], [], []]}) is None
    assert compile_mask({"status": "UNKNOWN", "days": [[[18, 24]]]}) is None


def test_exact_equivalence_disagreement():
    match = load_helpers()["reports_match"]
    report = {"state": "READY", "mask": "01", "hash": HASH}
    assert match(report, dict(report))
    assert not match(report, {**report, "mask": "00"})
    assert not match(report, {**report, "state": "AMBIGUOUS"})


def test_history_chain(clock):
    clock.reserve("room", "b1", 18, 1)
    clock.cancel("room", "b1")
    events = clock.history(0, 20)
    assert len(events) == 3
    assert events[1]["previous"] == events[0]["root"]
    assert events[2]["previous"] == events[1]["root"]
    assert events[1]["reservation"]["state"] == "RESERVED"
    assert events[2]["reservation"]["state"] == "CANCELLED"
