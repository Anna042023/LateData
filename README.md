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

For each supported query class, a metadata-only certification overlay is maintained over the shared Sealed microchunks. Finalized segments expose a common certificate charge $\lambda_c$, while the current residual tail keeps its exact certificate.

For a query with error budget $\epsilon_q$, the planner:

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
