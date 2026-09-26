import repro
import error_analysis
import gtnc_eval

from common import load_predictions, by_split

if __name__ == "__main__":
    records = load_predictions()

    print("### Table I - reproduction ###")
    repro.report(records, "dev")
    repro.report(records, "test")

    print("\n### Section IV - error analysis ###")
    for split in ("dev", "test"):
        error_analysis.error_types(records, split)
        error_analysis.translation_exact_match_and_length_ratio(records, split)
        error_analysis.wer_bleu_coupling(records, split)
    error_analysis.confusion_table(records, "test")
    error_analysis.length_grouped_wer(records, "test")

    print("\n### Section IV-D / V-C - numerals and GTNC ###")
    for split in ("dev", "test"):
        n_hyp_or_ref = sum(1 for r in by_split(records, split)
                            if gtnc_eval.contains_number_text(r["txt_hyp"]) or gtnc_eval.contains_number_text(r["txt_ref"]))
        print(f"[{split}] sentences with number in hyp-or-ref={n_hyp_or_ref}")
        gtnc_eval.numeral_gloss_alignment_accuracy(records, split)
        gtnc_eval.unigram_precision_recall(records, split, restrict_numbers=True)
        gtnc_eval.unigram_precision_recall(records, split, restrict_numbers=False)
        gtnc_eval.numeral_exact_match_rate(records, split)
        for variant in ("full", "no_signs", "oracle_glosses"):
            gtnc_eval.gtnc_table(records, split, variant)
