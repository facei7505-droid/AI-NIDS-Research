import csv
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from audit_netflow_v2_schema import inspect_csv, audit


def sample_csv(path, features=None, *, label_values=("0","1")):
    if features is None:
        features=[f"NetFlow_feature_{n}" for n in range(35)]
    headers=["Label","Attack","IPV4_SRC_ADDR",*features]
    with path.open("w",newline="",encoding="utf-8") as handle:
        w=csv.writer(handle)
        w.writerow(headers)
        for i,value in enumerate(label_values):
            w.writerow([value,"Benign" if value=="0" else "DoS","10.0.0.1",*([i+1]*len(features))])


def test_equal_feature_schema_hash_and_leakage_exclusion(tmp_path):
    a,b=tmp_path/"source.csv",tmp_path/"external.csv"
    sample_csv(a)
    sample_csv(b)
    source=inspect_csv(a)
    target=inspect_csv(b)
    result=audit(source,target)
    assert result["schema_compatible"]
    assert len(result["shared_candidate_predictors"])==35
    assert source["sha256"]==hashlib.sha256(a.read_bytes()).hexdigest()
    assert not ({"label","attack","ipv4_src_addr"} & set(source["candidate_predictors"]))
    assert source["sample_labels"]=={"0":1,"1":1}
    assert result["status"]=="STRUCTURAL_SCHEMA_AUDIT_ONLY"


def test_rejects_different_version_without_silent_mapping(tmp_path):
    a,b=tmp_path/"v2-a.csv",tmp_path/"v2-b.csv"
    sample_csv(a)
    cols=[f"NetFlow_feature_{n}" for n in range(35)]
    cols[-1]="different_semantics"
    sample_csv(b,features=cols)
    result=audit(inspect_csv(a,do_hash=False),inspect_csv(b,do_hash=False))
    assert not result["schema_compatible"]
    assert result["missing_in_external"]==["netflow_feature_34"]
    assert result["additional_in_external"]==["different_semantics"]


def test_rejects_duplicate_casefolded_headers(tmp_path):
    p=tmp_path/"bad.csv"
    p.write_text("Label,label,"+",".join(f"f_{x}" for x in range(35))+
                 "\n0,0,"+",".join("1" for _ in range(35))+"\n",encoding="utf-8")
    with pytest.raises(ValueError,match="duplicate"):
        inspect_csv(p)


@pytest.mark.parametrize("label",["benign","attack","","2"])
def test_rejects_unknown_label_mapping(tmp_path,label):
    p=tmp_path/"labels.csv"
    sample_csv(p,label_values=("0",label))
    with pytest.raises(ValueError,match="Label value"):
        inspect_csv(p)


def test_rejects_missing_label(tmp_path):
    p=tmp_path/"nolabel.csv"
    p.write_text(",".join(f"n{i}" for i in range(42))+"\n"+
                 ",".join("0" for _ in range(42))+"\n")
    with pytest.raises(ValueError,match="Missing binary Label"):
        inspect_csv(p)


def test_skip_hash_is_explicit_and_not_published_as_verified(tmp_path):
    p=tmp_path/"input.csv"
    sample_csv(p)
    info=inspect_csv(p,do_hash=False)
    assert info["sha256"] is None
    assert info["sample_is_not_population_statistics"] is True
