"""Reproduce Section IV (error analysis): error types, sentence-level stats,
confusion table, length-grouped WER, and the WER/BLEU coupling with Spearman rho."""
import collections
import math

from common import load_predictions, by_split
from align import sentence_wer


def add1_smoothed_sentence_bleu4(ref, hyp, max_n=4):
    ref_toks, hyp_toks = ref.split(), hyp.split()
    if len(hyp_toks) == 0:
        return 0.0
    log_precisions = []
    for n in range(1, max_n + 1):
        ref_ngrams = collections.Counter(tuple(ref_toks[i:i + n]) for i in range(len(ref_toks) - n + 1))
        hyp_ngrams = collections.Counter(tuple(hyp_toks[i:i + n]) for i in range(len(hyp_toks) - n + 1))
        total = sum(hyp_ngrams.values())
        matched = sum(min(c, ref_ngrams[g]) for g, c in hyp_ngrams.items())
        p_n = (matched + 1) / (total + 1)
        log_precisions.append(math.log(p_n))
    bp = 1.0 if len(hyp_toks) > len(ref_toks) else math.exp(1 - len(ref_toks) / len(hyp_toks))
    return bp * math.exp(sum(log_precisions) / max_n) * 100


def corpus_bleu4(pairs):
    """Plain (unsmoothed) corpus BLEU-4 over a list of (ref, hyp) strings, for the
    length-grouped bars in Fig. 3b (reuses the project's own sacrebleu wrapper)."""
    from common import metrics
    refs = [p[0] for p in pairs]
    hyps = [p[1] for p in pairs]
    return metrics.bleu(references=refs, hypotheses=hyps, level="word")["bleu4"]


def error_types(records, split):
    recs = by_split(records, split)
    tot_ref = tot_sub = tot_del = tot_ins = 0
    zero_err_sentences = 0
    for r in recs:
        s = sentence_wer(r["gls_ref"], r["gls_hyp"])
        tot_ref += s["num_ref"]
        tot_sub += s["num_sub"]
        tot_del += s["num_del"]
        tot_ins += s["num_ins"]
        if s["num_err"] == 0:
            zero_err_sentences += 1
    print(f"[{split}] sub={100*tot_sub/tot_ref:.2f} del={100*tot_del/tot_ref:.2f} ins={100*tot_ins/tot_ref:.2f}"
          f"  recognized-without-error={100*zero_err_sentences/len(recs):.1f}% ({zero_err_sentences}/{len(recs)})")


def translation_exact_match_and_length_ratio(records, split):
    recs = by_split(records, split)
    exact = sum(1 for r in recs if r["txt_hyp"].strip() == r["txt_ref"].strip())
    hyp_len = sum(len(r["txt_hyp"].split()) for r in recs)
    ref_len = sum(len(r["txt_ref"].split()) for r in recs)
    print(f"[{split}] translation exact-match={100*exact/len(recs):.1f}% ({exact}/{len(recs)})"
          f"  hyp/ref length ratio={hyp_len/ref_len:.2f}")


def confusion_table(records, split, top_k=6):
    recs = by_split(records, split)
    subs = collections.Counter()
    dels = collections.Counter()
    for r in recs:
        s = sentence_wer(r["gls_ref"], r["gls_hyp"])
        for op, ref_tok, hyp_tok in s["ops"]:
            if op == "S":
                subs[(ref_tok, hyp_tok)] += 1
            elif op == "D":
                dels[ref_tok] += 1
    print(f"[{split}] top substitutions (ref -> hyp):")
    for (rt, ht), c in subs.most_common(top_k):
        print(f"    {rt} -> {ht}: {c}")
    print(f"[{split}] top deletions (ref):")
    for rt, c in dels.most_common(top_k):
        print(f"    {rt}: {c}")


def length_grouped_wer(records, split, bin_size=4, n_bins=4):
    recs = by_split(records, split)
    bins = [[] for _ in range(n_bins)]
    for r in recs:
        s = sentence_wer(r["gls_ref"], r["gls_hyp"])
        length = s["num_ref"]
        idx = min((length - 1) // bin_size, n_bins - 1)
        bins[idx].append(s)
    print(f"[{split}] length-grouped WER (bin size={bin_size}):")
    for i, b in enumerate(bins):
        lo = i * bin_size + 1
        hi = "+" if i == n_bins - 1 else f"-{(i + 1) * bin_size}"
        if not b:
            continue
        tot_ref = sum(s["num_ref"] for s in b)
        tot_err = sum(s["num_err"] for s in b)
        print(f"    len {lo}{hi}: n={len(b)}  WER={100*tot_err/tot_ref:.1f}")


def wer_bucket(wer_pct):
    if wer_pct == 0:
        return 0
    if wer_pct <= 20:
        return 1
    if wer_pct <= 40:
        return 2
    return 3


def wer_bleu_coupling(records, split):
    recs = by_split(records, split)
    buckets = collections.defaultdict(list)
    per_sentence = []
    for r in recs:
        s = sentence_wer(r["gls_ref"], r["gls_hyp"])
        wer_pct = 100 * s["num_err"] / s["num_ref"] if s["num_ref"] > 0 else 0.0
        buckets[wer_bucket(wer_pct)].append((r["txt_ref"], r["txt_hyp"]))
        per_sentence.append((wer_pct, add1_smoothed_sentence_bleu4(r["txt_ref"], r["txt_hyp"])))

    print(f"[{split}] BLEU-4 by gloss-WER bucket:")
    labels = {0: "WER=0", 1: "0<WER<=20", 2: "20<WER<=40", 3: "WER>40"}
    for k in sorted(buckets):
        pairs = buckets[k]
        print(f"    {labels[k]}: n={len(pairs)}  corpus BLEU4={corpus_bleu4(pairs):.1f}")

    rho, p = spearman(per_sentence)
    print(f"[{split}] Spearman(gloss WER, smoothed sentence BLEU) rho={rho:.3f} p={p:.2e}  n={len(per_sentence)}")


def spearman(pairs):
    n = len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    rx = rankdata(xs)
    ry = rankdata(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    rho = cov / (sx * sy)
    # t-approx p-value (two-sided), fine for n in the hundreds
    t = rho * math.sqrt((n - 2) / max(1e-12, 1 - rho ** 2))
    p = 2 * (1 - student_t_cdf(abs(t), n - 2))
    return rho, p


def rankdata(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg_rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def student_t_cdf(t, df):
    # Abramowitz-Stegun style approximation via incomplete beta, using math.erf fallback for large df
    if df > 200:
        return 0.5 * (1 + math.erf(t / math.sqrt(2)))
    x = df / (df + t * t)
    ib = incomplete_beta(x, df / 2, 0.5)
    return 1 - 0.5 * ib


def incomplete_beta(x, a, b, iterations=200):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log(1 - x) * b - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for i in range(iterations):
        m = i // 2
        if i == 0:
            numerator = 1.0
        elif i % 2 == 0:
            numerator = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            numerator = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + numerator * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + numerator / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= d * c
        if abs(1 - d * c) < 1e-10:
            break
    return front * (f - 1.0)


if __name__ == "__main__":
    records = load_predictions()
    for split in ("dev", "test"):
        error_types(records, split)
        translation_exact_match_and_length_ratio(records, split)
        wer_bleu_coupling(records, split)
    confusion_table(records, "test")
    length_grouped_wer(records, "test")
