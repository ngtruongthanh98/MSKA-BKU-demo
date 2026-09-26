import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE_DIR = os.path.join(REPO_ROOT, "model", "baseline-MSKA")
sys.path.insert(0, BASELINE_DIR)

import metrics  # noqa: E402  (vendored WER/BLEU/ROUGE, same code the paper's train.py uses)
from phoenix_cleanup import clean_phoenix_2014_trans  # noqa: E402


def load_predictions():
    with open(os.path.join(REPO_ROOT, "data", "results.json"), encoding="utf-8") as f:
        txt = json.load(f)
    with open(os.path.join(REPO_ROOT, "data", "reg_results.json"), encoding="utf-8") as f:
        gls = json.load(f)

    txt_by_name = {r["name"]: r for r in txt}
    gls_by_name = {r["name"]: r for r in gls}
    assert set(txt_by_name) == set(gls_by_name), "name sets differ between results.json and reg_results.json"

    records = []
    for name, t in txt_by_name.items():
        g = gls_by_name[name]
        gls_hyp_str = " ".join(g["gls_hyp"]).upper()
        gls_ref_str = g["gls_ref"].upper()
        records.append({
            "name": name,
            "split": t["prefix"],
            "txt_hyp": t["txt_hyp"],
            "txt_ref": t["txt_ref"],
            "gls_hyp_raw": gls_hyp_str,
            "gls_ref_raw": gls_ref_str,
            "gls_hyp": clean_phoenix_2014_trans(gls_hyp_str),
            "gls_ref": clean_phoenix_2014_trans(gls_ref_str),
        })
    return records


def by_split(records, split):
    return [r for r in records if r["split"] == split]
