# LateData

Code and data release for:

**Which Late Data Must Be Read? Error-Bounded Aggregate Query Processing in Time-Series Databases**

LateData studies **selective access to durable but uncompacted late data** in time-series databases. Instead of reading the entire Sealed backlog, the system determines which late-data regions must be read so that a temporal aggregate query satisfies a deterministic error budget while minimizing physical read bytes.

## Main Contributions

1. **Minimum-byte late-state read formulation.**  
   We formulate selective access to Sealed, uncompacted state under pinned snapshot ownership and deterministic aggregate-error contracts. Direct query-specific planning is weakly NP-hard, motivating a reusable metadata-based representation rather than a per-query knapsack solve.

2. **Class-specific balanced certification overlays.**  
   Late-data microchunks remain physically shared, while lightweight per-class overlays maintain event-time boundaries, byte counters, references, and contribution certificates. Mass-adaptive packing separates workload-dependent semantic slack from bounded uniformization slack, and the unfinished residual tail retains an exact certificate.

3. **Exact structured planning over the certified surrogate.**  
   Uniform finalized-segment charges are characterized as the condition that enables an exact cost-only `k`-cheapest rule for every error budget and byte-cost vector. The same ordered representation also supports an integral interval formulation for groups of same-class temporal queries.

4. **Watermark-local online maintenance.**  
   Under bounded lateness and a fixed catalog, arrival-driven mutable certification state depends on the lateness horizon and catalog size rather than total archive length. Sealing, selection, and compaction ownership are kept separate so that query-time selective reads do not modify storage ownership.

## Method Overview

LateData separates query-visible state into three parts:

- **Base** — compacted historical state, read exactly;
- **Open** — recent mutable state, read exactly;
- **Sealed** — durable but uncompacted late-data state, selectively read.

For each supported query class, a metadata-only certification overlay is maintained over the shared Sealed microchunks. Finalized segments expose a common certificate charge `lambda_c`, while the current residual tail keeps its exact certificate.

For a query with error budget `epsilon_q`, the planner:

1. pins a consistent ownership snapshot;
2. resolves the query to a certification class;
3. identifies the intersected finalized segments and residual tail;
4. evaluates the residual-tail read/skip alternatives;
5. determines how many finalized segments must be read;
6. selects the required number of lowest-byte-cost segments;
7. reads the selected Sealed microchunks together with the exact Base and Open state.

The result satisfies the deterministic omission-error certificate of the selected plan.

## Repository Structure

This public repository intentionally keeps only the code, scripts, and reported-result data required for inspecting the released artifact.

```text
LateData/
├── code/
│   └── balanced_cert_reference.py
├── scripts/
│   └── verify_reported_results.py
└── data/
    └── reported/
        ├── rq1_soundness.csv
        ├── rq2_balance.csv
        ├── rq4_physical.csv
        ├── rq4_primary_mauna_loa.csv
        ├── rq4_baselines.csv
        ├── rq5_mutable_state.csv
        └── ...
```

### `code/`

`balanced_cert_reference.py` is a compact reference implementation of the **uniform-charge single-query certified planner**. It explicitly considers both residual-tail states and returns the minimum-byte feasible plan.

### `scripts/`

`verify_reported_results.py` checks the numerical invariants represented by the released CSV summaries, including contract satisfaction, the balance envelope, physical byte ratios, execution speedup ranges, baseline correctness, and the mutable-state bound.

### `data/`

`data/reported/` contains machine-readable summaries of the experimental results reported in the paper. These files are intended for result inspection and consistency checking.

## Requirements

The included reference planner and result checker use only the Python standard library.

- Python **3.10+** recommended
- No GPU required
- No third-party Python packages are required for the two released scripts

The full experimental study described in the paper additionally used SQLite and QuestDB execution paths; those systems are not required to run the compact planner or the released result checker.

## Quick Start

Clone the repository and move to its root directory:

```bash
git clone https://github.com/Anna042023/LateData.git
cd LateData
```

Run the reference planner:

```bash
python3 code/balanced_cert_reference.py
```

A successful self-test prints:

```text
balanced_cert_reference: PASS
```

Check the released result tables:

```bash
python3 scripts/verify_reported_results.py
```

A successful check prints:

```text
reported-result consistency: PASS
```

## Reference Planner

The main entry point is:

```python
plan_uniform_charge(
    byte_costs,
    lambda_charge,
    epsilon,
    tail_certificate=0.0,
    tail_cost=0.0,
)
```

Example:

```python
from code.balanced_cert_reference import plan_uniform_charge

plan = plan_uniform_charge(
    byte_costs=[9, 2, 5, 1],
    lambda_charge=3,
    epsilon=6,
)

print(plan.read_indices)
print(plan.cost)
print(plan.certified_omitted_charge)
```

The planner first conditions on whether the residual tail is read. For each feasible tail state, the error budget determines the maximum number of uniform-charge finalized segments that may remain unread. The planner then reads the required number of cheapest segments and returns the lower-cost feasible alternative.

## Experimental Coverage

The paper evaluates five complementary questions:

| RQ | Focus |
|---|---|
| **RQ1** | Snapshot-safe deterministic certification |
| **RQ2** | Balance-induced certificate inflation |
| **RQ3** | Certification-catalog adequacy |
| **RQ4** | Planning structure and physical execution |
| **RQ5** | Watermark-local maintenance |

The controlled evaluation uses Sensor54-like and Taxi-like workloads, while public time-series traces are used to test heterogeneous real-valued contributions and execution transfer. Physical execution is evaluated with SQLite and QuestDB.

### Reported Results

The released tables capture the main reported measurements:

- **440/440** controlled soundness queries satisfy their requested error contracts.
- **5,400** balance instances remain inside the analytical envelope.
- On **SQLite**, refined catalogs reduce selected late-data bytes to **0.51–0.69×** FullLateRead and achieve median execution speedups of **1.45–1.91×**.
- On controlled **QuestDB 10.0.1** replay, selected bytes are **0.54–0.70×** FullLateRead with median server speedups of **1.26–1.69×**.
- On the public **Mauna Loa CO2** replay, all 12 queries satisfy their contracts, with selected-byte ratios of **0.50–0.70×** and median server speedups of **1.20–1.41×**.

These execution results characterize the tested settings; they should not be interpreted as universal production-latency guarantees.

## Baselines

The evaluation compares the balanced certification design with component-matched alternatives:

- **FullLateRead** — reads the complete Sealed backlog exactly;
- **NoSealedRead** — skips all Sealed state;
- **Oracle** — uses exact per-query contributions;
- **NoBalance** — retains heterogeneous certificate charges;
- **FixedRows** — static row-based segmentation with a common maximum charge;
- **FixedTime** — static time-based segmentation with a common maximum charge;
- **Balanced-Cert** — the proposed balanced certification representation.

The reported-result checker verifies that the exact/certified methods satisfy their contracts in the released baseline table, while `NoSealedRead` does not.

## Artifact Scope

This repository is a **compact code-and-data release**, not a complete reconstruction of every historical experimental driver or raw event-level execution log.

Specifically:

- `code/balanced_cert_reference.py` demonstrates the proved uniform-charge planning rule;
- `data/reported/` preserves manuscript-facing experimental summaries;
- `scripts/verify_reported_results.py` checks directly testable numerical invariants from those summaries.

The result checker is therefore a consistency check over the released data, not a substitute for the paper's formal proofs or a claim that every database experiment can be rerun from raw logs using this compact repository alone.

## Citation

If you use this work, please cite:

```bibtex
@article{wang2027latedata,
  title   = {Which Late Data Must Be Read? Error-Bounded Aggregate Query Processing in Time-Series Databases},
  author  = {Wang, Anna and Zhang, Chao and Li, Ling and Li, Wentao and Li, Deyu},
  journal = {Proceedings of the VLDB Endowment},
  volume  = {20},
  number  = {1},
  year    = {2027}
}
```
