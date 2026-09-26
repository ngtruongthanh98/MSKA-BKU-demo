"""Reproduce Table I (repro) and the WER/BLEU/ROUGE parts of Section V-A."""
from common import load_predictions, by_split, metrics


def report(records, split):
    recs = by_split(records, split)
    gls_ref = [r["gls_ref"] for r in recs]
    gls_hyp = [r["gls_hyp"] for r in recs]
    wer = metrics.wer_list(references=gls_ref, hypotheses=gls_hyp)

    txt_ref = [r["txt_ref"] for r in recs]
    txt_hyp = [r["txt_hyp"] for r in recs]
    bleu = metrics.bleu(references=txt_ref, hypotheses=txt_hyp, level="word")
    rouge = metrics.rouge(references=txt_ref, hypotheses=txt_hyp, level="word")

    print(f"== {split} (n={len(recs)}) ==")
    print(f"  WER={wer['wer']:.2f}  sub={wer['sub_rate']:.2f}  del={wer['del_rate']:.2f}  ins={wer['ins_rate']:.2f}")
    print(f"  ROUGE-L={rouge:.2f}  BLEU1={bleu['bleu1']:.2f}  BLEU2={bleu['bleu2']:.2f}"
          f"  BLEU3={bleu['bleu3']:.2f}  BLEU4={bleu['bleu4']:.2f}")


if __name__ == "__main__":
    records = load_predictions()
    report(records, "dev")
    report(records, "test")
