import collections
import random

from common import load_predictions, by_split
from align import sentence_wer
from nu import (nu_text, gtnc_flag, contains_number_text,
                number_tokens_text, GLOSS_UNITS, GLOSS_TEENS, GLOSS_TENS)

GLOSS_NUMBER_WORDS = set(GLOSS_UNITS) | set(GLOSS_TEENS) | set(GLOSS_TENS)
GLOSS_NUMBER_WORDS.discard("NULL")  # NULL(=0) never appears as a real weather-forecast numeral gloss


def numeral_gloss_alignment_accuracy(records, split):
    recs = by_split(records, split)
    num_correct = num_total = other_correct = other_total = 0
    for r in recs:
        s = sentence_wer(r["gls_ref"], r["gls_hyp"])
        for op, ref_tok, hyp_tok in s["ops"]:
            if ref_tok is None:
                continue  # insertion, no reference token
            is_num = ref_tok in GLOSS_NUMBER_WORDS
            correct = (op == "C")
            if is_num:
                num_total += 1
                num_correct += correct
            else:
                other_total += 1
                other_correct += correct
    print(f"[{split}] numeral gloss alignment acc={100*num_correct/num_total:.1f}% ({num_correct}/{num_total})"
          f"  other gloss acc={100*other_correct/other_total:.1f}% ({other_correct}/{other_total})")


def unigram_precision_recall(records, split, restrict_numbers):
    recs = by_split(records, split)
    matched = hyp_total = ref_total = 0
    for r in recs:
        if restrict_numbers:
            hyp_toks = number_tokens_text(r["txt_hyp"])
            ref_toks = number_tokens_text(r["txt_ref"])
        else:
            hyp_toks = r["txt_hyp"].split()
            ref_toks = r["txt_ref"].split()
        hc, rc = collections.Counter(hyp_toks), collections.Counter(ref_toks)
        matched += sum(min(c, rc[w]) for w, c in hc.items())
        hyp_total += len(hyp_toks)
        ref_total += len(ref_toks)
    p = 100 * matched / hyp_total if hyp_total else float("nan")
    r_ = 100 * matched / ref_total if ref_total else float("nan")
    kind = "number" if restrict_numbers else "overall"
    print(f"[{split}] {kind} unigram precision={p:.1f}% recall={r_:.1f}%")


def numeral_exact_match_rate(records, split):
    recs = [r for r in by_split(records, split) if contains_number_text(r["txt_ref"])]
    exact = sum(1 for r in recs if nu_text(r["txt_hyp"]) == nu_text(r["txt_ref"]))
    print(f"[{split}] numeral exact-match: {100*exact/len(recs):.1f}% of {len(recs)}"
          f"  (error rate {100*(1-exact/len(recs)):.1f}%)")
    return recs


def bootstrap_ci(values_fn, n, n_resamples=2000, seed=0):
    rng = random.Random(seed)
    stats = []
    for _ in range(n_resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        stats.append(values_fn(idx))
    stats.sort()
    lo = stats[int(0.025 * n_resamples)]
    hi = stats[int(0.975 * n_resamples) - 1]
    return lo, hi


def gtnc_table(records, split, variant="full"):
    recs = [r for r in by_split(records, split) if contains_number_text(r["txt_hyp"]) or contains_number_text(r["txt_ref"])]
    n = len(recs)

    labels = []  # ground-truth: True = numeral error
    flags = []   # GTNC prediction: True = flagged
    for r in recs:
        is_error = nu_text(r["txt_hyp"]) != nu_text(r["txt_ref"])
        labels.append(is_error)
        if variant == "no_signs":
            flags.append(gtnc_flag(r["gls_hyp"], r["txt_hyp"], use_signs=False))
        elif variant == "oracle_glosses":
            # same check as "full" (signed values + degenerate-range rule), just with
            # the reference gloss substituted for the recognizer's hypothesis gloss
            flags.append(gtnc_flag(r["gls_ref"], r["txt_hyp"]))
        else:
            flags.append(gtnc_flag(r["gls_hyp"], r["txt_hyp"]))

    def prf(idx):
        tp = sum(1 for i in idx if flags[i] and labels[i])
        fp = sum(1 for i in idx if flags[i] and not labels[i])
        fn = sum(1 for i in idx if not flags[i] and labels[i])
        tn = sum(1 for i in idx if not flags[i] and not labels[i])
        p = tp / (tp + fp) if (tp + fp) else float("nan")
        r = tp / (tp + fn) if (tp + fn) else float("nan")
        acc_err = fn / (fn + tn) if (fn + tn) else float("nan")
        return tp, fp, fn, tn, p, r, acc_err

    tp, fp, fn, tn, p, r, acc_err = prf(range(n))
    f1 = 2 * p * r / (p + r) if (p + r) else float("nan")
    n_flag = tp + fp

    p_lo, p_hi = bootstrap_ci(lambda idx: prf(idx)[4] * 100, n)
    r_lo, r_hi = bootstrap_ci(lambda idx: prf(idx)[5] * 100, n)
    acc_lo, acc_hi = bootstrap_ci(lambda idx: prf(idx)[6] * 100, n)

    base_err = sum(labels) / n * 100
    print(f"[{split}] variant={variant} n={n} flagged={n_flag} "
          f"P={100*p:.1f} (CI {p_lo:.1f}-{p_hi:.1f})  R={100*r:.1f} (CI {r_lo:.1f}-{r_hi:.1f})  F1={100*f1:.1f}  "
          f"AccErr={100*acc_err:.1f} (CI {acc_lo:.1f}-{acc_hi:.1f})  [unchecked err={base_err:.1f}]")


if __name__ == "__main__":
    records = load_predictions()
    for split in ("dev", "test"):
        n_hyp_or_ref = sum(1 for r in by_split(records, split)
                            if contains_number_text(r["txt_hyp"]) or contains_number_text(r["txt_ref"]))
        n_ref = sum(1 for r in by_split(records, split) if contains_number_text(r["txt_ref"]))
        print(f"[{split}] sentences with number in hyp-or-ref={n_hyp_or_ref}  in ref={n_ref}")
        numeral_gloss_alignment_accuracy(records, split)
        unigram_precision_recall(records, split, restrict_numbers=True)
        unigram_precision_recall(records, split, restrict_numbers=False)
        numeral_exact_match_rate(records, split)
        for variant in ("full", "no_signs", "oracle_glosses"):
            gtnc_table(records, split, variant)
        print()
