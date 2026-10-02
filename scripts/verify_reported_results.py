#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "reported"

def rows(name):
    with (D / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# RQ1
r = rows("rq1_soundness.csv")
assert sum(int(x["controlled_queries"]) for x in r) == 440
assert all(float(x["max_error_to_budget"]) <= 1.0 for x in r)
assert sum(int(x["contract_violations"]) for x in r) == 0

# RQ2 analytical envelope
r = rows("rq2_balance.csv")
assert all(float(x["median_E_over_C"]) < float(x["theoretical_limit"]) for x in r)

# RQ4 physical execution ranges used in the abstract
r = rows("rq4_physical.csv")
assert all(x["contracts_satisfied"] == "yes" for x in r)
sql = [x for x in r if x["engine"] == "SQLite"]
assert round(min(float(x["bytes_ratio"]) for x in sql), 2) == 0.51
assert round(max(float(x["bytes_ratio"]) for x in sql), 2) == 0.69
assert min(float(x["server_or_exec_speedup"]) for x in sql) == 1.45
assert max(float(x["server_or_exec_speedup"]) for x in sql) == 1.91
qctrl = [x for x in r if x["engine"] == "QuestDB" and x["workload"] in {"Sensor54", "Taxi-like"}]
assert min(float(x["bytes_ratio"]) for x in qctrl) == 0.54
assert max(float(x["bytes_ratio"]) for x in qctrl) == 0.70
assert min(float(x["server_or_exec_speedup"]) for x in qctrl) == 1.26
assert max(float(x["server_or_exec_speedup"]) for x in qctrl) == 1.69

# Primary Mauna Loa replay
r = rows("rq4_primary_mauna_loa.csv")
assert len(r) == 2 and all(int(x["queries"]) == 12 for x in r)
assert round(min(float(x["bytes_ratio"]) for x in r), 2) == 0.50
assert round(max(float(x["bytes_ratio"]) for x in r), 2) == 0.70
assert min(float(x["median_server_speedup"]) for x in r) == 1.20
assert max(float(x["median_server_speedup"]) for x in r) == 1.41

# RQ5 bounded mutable state
r = rows("rq5_mutable_state.csv")
assert all(int(x["observed_mutable_objects"]) <= int(x["bound"]) for x in r)

# Baseline table: exact and certified methods satisfy contracts; NoSealedRead does not
r = rows("rq4_baselines.csv")
by = {x["method"]: x for x in r}
assert int(by["NoSealedRead"]["satisfaction_percent"]) == 0
for name in ["FullLateRead", "Oracle", "NoBalance", "Balanced-Cert", "FixedRows", "FixedTime"]:
    assert int(by[name]["satisfaction_percent"]) == 100

print("reported-result consistency: PASS")
