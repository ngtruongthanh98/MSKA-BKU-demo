"""Build a small, curated set of REAL MSKA-SLR/SLT outputs for the local replay
demo. backend/controllers/demoController.js reads the resulting JSON directly
at request time -- no model, GPU, or network call involved.

Picks from the test split (matching the paper's reported test-split numbers)
across three categories so the demo tells a complete story: the system
catching its own numeral error (gtnc_warning), a clean best case
(perfect_recognition), and a typical middling case (typical_errors).
"""
import json
import os

from common import load_predictions, by_split
from nu import gtnc_flag
from align import sentence_wer

OUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "demo_manifest.json")
N_PER_CATEGORY = 5


def sentence_is_perfect(r):
    return r["gls_hyp"] == r["gls_ref"] and r["txt_hyp"].strip() == r["txt_ref"].strip()


def build():
    records = by_split(load_predictions(), "test")

    flagged, perfect, typical = [], [], []
    for r in records:
        wer = sentence_wer(r["gls_ref"], r["gls_hyp"])
        entry = {
            "name": r["name"],
            "split": r["split"],
            "glossHyp": r["gls_hyp"],
            "glossRef": r["gls_ref"],
            "textHyp": r["txt_hyp"],
            "textRef": r["txt_ref"],
            "gtncFlag": gtnc_flag(r["gls_hyp"], r["txt_hyp"]),
            "numErr": wer["num_err"],
            "category": None,
        }
        ref_len = wer["num_ref"]
        # a 4-8 gloss reference reads well on a slide and matches the length
        # bucket the paper itself finds most representative (lowest WER)
        in_sweet_spot = 4 <= ref_len <= 8
        if entry["gtncFlag"]:
            flagged.append(entry)
        elif sentence_is_perfect(r) and in_sweet_spot:
            perfect.append(entry)
        # "typical": a believable partial success, not a near-total recognition
        # failure -- non-empty gloss hypothesis with 1-3 word-level errors
        elif r["gls_hyp"] and 1 <= wer["num_err"] <= 3 and in_sweet_spot:
            typical.append(entry)

    # shortest-first within the sweet spot reads best on a projector
    for pool in (flagged, perfect, typical):
        pool.sort(key=lambda e: len(e["glossHyp"].split()))

    manifest = []
    for category, pool in (("gtnc_warning", flagged),
                           ("perfect_recognition", perfect),
                           ("typical_errors", typical)):
        for entry in pool[:N_PER_CATEGORY]:
            entry["category"] = category
            manifest.append(entry)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"wrote {len(manifest)} entries -> {OUT_PATH}")
    print(f"  gtnc_warning={min(len(flagged), N_PER_CATEGORY)} "
          f"perfect_recognition={min(len(perfect), N_PER_CATEGORY)} "
          f"typical_errors={min(len(typical), N_PER_CATEGORY)}")


if __name__ == "__main__":
    build()
