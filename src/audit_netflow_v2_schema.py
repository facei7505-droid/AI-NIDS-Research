"""Strict read-only schema/provenance gate for UQ's common NetFlow-v2 datasets.

This script does NOT fit, train, or evaluate a detector. It does not
download data. It does not map or silently impute inconsistent columns.
Data must come from a documented, authorized official UQ distribution.

Dataset pairs intended for scientific comparison:
  NF-UNSW-NB15-v2.csv
  NF-CSE-CIC-IDS2018-v2.csv

The reported external-validation experiment is NOT executed by this audit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


# Label and provenance attributes are NEVER predictors.
TARGET_COLUMNS = frozenset({"label"})
EXCLUDE_PREDICTORS = frozenset({
    "label", "attack", "attack_cat", "category", "dataset",
    "ipv4_src_addr", "ipv4_dst_addr", "ipv6_src_addr", "ipv6_dst_addr",
    "src_ip", "dst_ip", "srcip", "dstip",
})


def canonical(header):
    """Whitespace normalization only: never quietly rename semantics."""
    value = header.strip().lower()
    if not value:
        raise ValueError("Empty header name")
    return value


def inspect_csv(path: Path, *, sample_rows: int = 5000, do_hash: bool = True):
    if sample_rows < 1:
        raise ValueError("sample_rows must be positive")
    path=Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("r",encoding="utf-8-sig",newline="") as handle:
        reader=csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"No header: {path}")
        names=[canonical(c) for c in reader.fieldnames]
        if len(set(names)) != len(names):
            raise ValueError(f"Ambiguous duplicate normalized header: {path}")
        if "label" not in names:
            raise ValueError(f"Missing binary Label column: {path}")
        columns=dict(zip(reader.fieldnames,names))
        labels={"0":0,"1":0}
        sampled=0
        for item in reader:
            if sampled >= sample_rows:
                break
            if None in item:
                raise ValueError("Malformed CSV row with more values than the header")
            label_raw=next((value for k,value in item.items() if columns[k]=="label"),None)
            if label_raw is None or label_raw.strip() not in labels:
                raise ValueError(f"Unrecognized binary Label value in {path}: {label_raw!r}")
            labels[label_raw.strip()]+=1
            sampled+=1
    if sampled == 0:
        raise ValueError("CSV has no data rows")
    candidate=sorted(set(names)-EXCLUDE_PREDICTORS)
    if len(candidate) < 30:
        raise ValueError(f"Only {len(candidate)} eligible predictors; check wrong dataset/version")
    digest=None
    if do_hash:
        h=hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda:handle.read(8*1024*1024),b""):
                h.update(block)
        digest=h.hexdigest()
    return {
        "filename":path.name,
        "sha256":digest,
        "header_columns":names,
        "excluded_columns":sorted(set(names)&EXCLUDE_PREDICTORS),
        "candidate_predictors":candidate,
        "sample_rows_checked":sampled,
        "sample_labels":labels,
        "sample_is_not_population_statistics":True,
    }


def audit(source: dict, external: dict):
    original=set(source["candidate_predictors"])
    target=set(external["candidate_predictors"])
    missing=sorted(original-target)
    extra=sorted(target-original)
    result={
        "status":"STRUCTURAL_SCHEMA_AUDIT_ONLY",
        "dataset_family":"UQ NetFlow v2",
        "source":source,"external":external,
        "shared_candidate_predictors":sorted(original & target),
        "missing_in_external":missing,
        "additional_in_external":extra,
        "schema_compatible":not missing and not extra,
        "limitations":[
            "Header compatibility does not prove equivalent units, numerical distributions, network-session grouping, or label validity.",
            "Only a small prefix of rows was inspected for labels; complete per-file row counts and class shares are not measured.",
            "Endpoint addresses and label/provenance attributes are excluded from the predictor candidate set.",
            "This file reports zero model evaluations and zero independent validation results.",
            "The v2 data are derived from historical PCAP collections; they are not independent live-network deployments.",
            "The shared feature definitions must be checked against the official UQ feature specification before benchmarking.",
        ],
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--external",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path("results/netflow_v2_schema_audit.json"))
    parser.add_argument("--sample-rows",type=int,default=5000)
    parser.add_argument("--skip-hash",action="store_true",
                        help="Inspect header/labels only; cannot claim hash-verified input")
    args=parser.parse_args()
    if args.source.resolve()==args.external.resolve():
        parser.error("Independent dataset files required; source and target cannot be the same file")
    source=inspect_csv(args.source,sample_rows=args.sample_rows,do_hash=not args.skip_hash)
    external=inspect_csv(args.external,sample_rows=args.sample_rows,do_hash=not args.skip_hash)
    result=audit(source,external)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(f"Shared eligible features: {len(result['shared_candidate_predictors'])}")
    print(f"Schema compatible: {result['schema_compatible']}")
    if not result["schema_compatible"]:
        raise SystemExit("Feature schema mismatch — do not claim cross-domain evaluation")


if __name__=="__main__":
    main()
