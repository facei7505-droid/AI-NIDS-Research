# External validation with the University of Queensland NetFlow v2 family

**Protocol checkpoint: 19 November 2026. No NetFlow v2 external model run has been performed.**

## Why the v2 pair is a better external test

The University of Queensland (UQ) published datasets converted into a common NetFlow-v2 feature format. Unlike the raw UNSW and CICFlowMeter CSV formats, the common standardized feature definitions make it possible *in principle* to test whether the same model-reliability observation transfers between different underlying networks.

- **Source corpus:** NF-UNSW-NB15-v2, 2,390,275 flows according to UQ, of which 95,053 are attack-labeled (3.98%). This is NOT the same 175,341-row UNSW train CSV used in the earlier project.
- **Independent-origin target corpus:** NF-CSE-CIC-IDS2018-v2, 18,893,708 flows, of which 2,258,141 are attack-labeled (11.95%). It is sourced from a different benchmark traffic collection.
- **Feature format:** 43 shared extended NetFlow features according to UQ; full header, type, units, columns and label conventions must still be verified on acquired files.
- **Official dataset site:** https://staff.itee.uq.edu.au/marius/NIDS_datasets/
- **UQ project description and use terms:** https://www.cyber.uq.edu.au/project/machine-learning-based-nids-datasets
- **Citable methods paper:** Sarhan, M., Layeghy, S., & Portmann, M. (2022). *Towards a Standard Feature Set for Network Intrusion Detection System Datasets*. https://doi.org/10.1007/s11036-021-01843-0

The authors permit academic research use with proper attribution; consult the official site for the up-to-date dataset terms. Never redistribute full source CSV files through the project without checking their rights.

## Critical differences and risks

1. The NetFlow v2 source corpus is **derived from UNSW-NB15 traffic** and cannot be treated as a second independently gathered network from the older UNSW official-designated train/test split. It can be used as a standardized *source domain* for an external-origin evaluation on CIC.
2. Other published research has already investigated transfer between these standardized datasets. Our novelty cannot be the mere selection of the v2 pair.
3. Flow records can be correlated or near duplicates. The external data's structure must be audited and any split/temporal boundaries respected.
4. NetFlow features can include network addresses or fields closely correlated with acquisition/testbed setup. Explicitly prohibit endpoint IDs, label/attack categories and dataset-provenance fields as predictors.
5. The rare attack prevalence may make naive, unstratified small samples unsuitable for measuring recall; document sampling or evaluate on the full corpus.
6. Standardized feature names do not guarantee identical label distributions, realistic network-time transfer, semantic equality or live security effectiveness.

## Required protocol gates BEFORE independent test labels are examined

- Obtain the two exact UQ NetFlow-v2 CSV files from documented official distribution, record retrieval UTC time, file sizes and SHA-256.
- Run `src/audit_netflow_v2_schema.py` on the two files. It checks headers, eligibility and obvious label inconsistencies without fitting or scoring any model. It reads a small row prefix, so its sample counts are **not** population statistics.
- **STOP** on header or predictor disagreement. Never silently substitute columns, zero-fill missing features or rename semantically different variables.
- Manually verify units and scientific definitions against UQ's v2 feature definitions. Choose two **nonoverlapping** feature blocks with shared semantics, and register their exact column names **before evaluating the target**. The original UNSW Protocol/Context groups cannot simply be reused by name.
- Establish an accepted source train/validation split that respects available flow/session/time structure. Freeze all model configurations and donor-policy choices using only source data.
- The primary comparison is **global versus train-fitted observable-stratified** donor selection, with equal perturbation fraction and measured effective exchange frequency. The class-label oracle is only a retrospective mechanism control and is excluded from the main claim.
- Register primary metric: paired difference in *excess FPR interaction* under shared feature groups, measured on the target without selecting a new threshold or strategy on target labels.
- Register secondary metrics: clean FPR, recall, confusion counts, per-group exchange rate, feature validity checks, and uncertainty clustered by source capture/session where feasible.
- Publish all negative and zero findings as well as positive ones. A differing attack taxonomy may invalidate direct score comparisons and must be documented.

## How to run only the available audit

After obtaining the real CSVs under `data/external/` (not committed to Git):

```bash
python src/audit_netflow_v2_schema.py \
  --source data/external/NF-UNSW-NB15-v2.csv \
  --external data/external/NF-CSE-CIC-IDS2018-v2.csv \
  --output results/netflow_v2_schema_audit.json
```

This is a **schema/provenance diagnostic only**, not an independent model evaluation. The audit computes SHA-256 of both full files by default; for a quick non-verified header check only, use `--skip-hash` and explicitly label the report unverified.

**Current factual status:** source and target external v2 files have not been acquired and their actual schemas have not been checked by this project. No cross-domain metric has been observed, no new-world-first contribution proved, and 9/10 novelty remains unsubstantiated.
