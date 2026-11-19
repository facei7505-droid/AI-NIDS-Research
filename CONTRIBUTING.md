# Contributing to AI-NIDS Research

This is an **exploratory research codebase**, not a production intrusion-detection tool. Contributions are welcome only when they improve the correctness, reproducibility, interpretability or transparent documentation of experiments.

## Before contributing

1. Read [RESEARCH_DESIGN.md](docs/RESEARCH_DESIGN.md) and [STATUS.md](docs/STATUS.md).
2. Open a focused issue describing the specific research question, error, proposed control or replication concern.
3. Never use already inspected official test labels to tune a new model or choose a favorable hypothesis and then present the outcome as independent confirmation.
4. Do not commit proprietary network traffic, sensitive IP addresses, original datasets, credentials or unlicensed materials. Local research inputs are excluded by `.gitignore`.
5. Disclose substantial AI assistance and describe what was human-verified. Do not manufacture results or citations.

## Local validation

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m compileall -q src tests
```

For research logic changes, add a **small deterministic synthetic-data test** that fails on the old behavior, then demonstrate that it passes after your fix. For results, supply exact dataset provenance, file hashes, software environment, model parameters, seeds, performance metrics, and a stated train/validation/test boundary.

## Evidence policy

- **Measured**: an actual executed run with accessible raw data provenance, code revision, and numerical output.
- **Exploratory**: an outcome-driven follow-up or analysis using already inspected data.
- **Proposed**: design/code exists but the complete study has not executed successfully.
- **Externally confirmed**: a separately sourced and appropriately controlled data collection independently supports a previously defined hypothesis. This status is **not reached** by the current project.

Every research claim must cite the exact stored CSV/JSON result rather than a manually typed unsupported number. Include negative and null outcomes. Do not claim significance from overlapping random seeds or independently replicate results by merely changing random seeds on one dataset.

## Pull-request checklist

- [ ] Change is scoped and reproducible
- [ ] Unit tests added or updated
- [ ] No direct target leakage or training-on-test introduced
- [ ] Dataset provenance and model/data split documented
- [ ] No source data or personal information committed
- [ ] Manuscript, README and STATUS kept consistent if results change
- [ ] All generated evidence comes from executed computation
- [ ] Existing research and AI assistance acknowledged

**License note:** this repository has no explicit software license yet. Contact the rights holder before redistributing or reusing material outside terms permitted by law; public GitHub visibility alone does not make it open-source licensed.
