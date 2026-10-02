# LateData: Error-Bounded Aggregate Query Processing over Sealed Late State

This repository accompanies the PVLDB manuscript:

**Which Late Data Must Be Read? Error-Bounded Aggregate Query Processing in Time-Series Databases**

This release is synchronized with the **R11.114** manuscript.

## Repository contents

- `paper/paper.pdf` - R11.114 submission PDF.
- `paper/source/` - complete submission source, bibliography, figures, editable figure sources, and build scripts.
- `data/reported/` - machine-readable summaries of the experimental values reported in the final manuscript.
- `code/balanced_cert_reference.py` - compact reference implementation of the uniform-charge single-query certified planner described in Section 4.
- `scripts/verify_reported_results.py` - checks the manuscript-facing numerical invariants encoded in `data/reported/`.
- `VERIFY.sh` - one-command artifact sanity check.
- `MANIFEST.sha256` - SHA-256 integrity manifest for the release.

## Quick verification

From the repository root:

```bash
bash VERIFY.sh
```

A successful run ends with:

```text
ARTIFACT VERIFICATION: PASS
```

The verification uses only the Python standard library.

## Build the paper

The submission source is under `paper/source/`:

```bash
cd paper/source
bash BUILD.sh
```

The canonical submitted PDF is `paper/paper.pdf`.

## Code example

The reference implementation exposes the exact uniform-charge planner used by the certified surrogate:

```bash
python3 code/balanced_cert_reference.py
```

The implementation enumerates the residual-tail read/skip decision and, for each feasible state, reads the required number of cheapest finalized segments.

## Data

The CSV files under `data/reported/` encode the values reported by RQ1-RQ5 and the physical/baseline tables in the paper. They are intended for manuscript-facing verification and plotting/checking of published summary values.

Important scope note: this GitHub bundle does **not** reconstruct unavailable event-level raw run logs or claim to rerun the full QuestDB instrumented experiment from scratch. It packages the currently accessible frozen paper, source, reported-result data, and a reference implementation/checker. If the historical full raw artifact is available separately, it should be merged into this repository before claiming raw-run reproducibility.

## Artifact boundaries

The manuscript distinguishes deterministic proofs from execution measurements. This repository follows the same boundary:

- the reference planner illustrates the proved uniform-charge selection rule;
- the CSVs preserve reported evaluation summaries;
- the verification script checks numerical consistency and directly testable inequalities from those summaries;
- no summary check is presented as a substitute for the deterministic proofs in the paper.

## Public upload

Upload the **contents of this directory** to the repository root rather than uploading this ZIP as one opaque file. At minimum, the public root should visibly contain:

`README.md`, `VERIFY.sh`, `MANIFEST.sha256`, `paper/`, `data/`, `code/`, and `scripts/`.
