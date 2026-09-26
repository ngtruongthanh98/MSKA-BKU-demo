"""Token-level alignment identical to metrics.edit_distance/get_alignment,
but returns (op, ref_token, hyp_token) tuples instead of padded strings,
so we can build confusion tables and per-sentence error counts."""
from common import metrics

WER_COST_DEL = metrics.WER_COST_DEL
WER_COST_INS = metrics.WER_COST_INS
WER_COST_SUB = metrics.WER_COST_SUB


def align(ref_tokens, hyp_tokens):
    r, h = ref_tokens, hyp_tokens
    d = metrics.edit_distance(r=r, h=h)
    x, y = len(r), len(h)
    max_len = 3 * (x + y)
    ops = []
    while True:
        if (x <= 0 and y <= 0) or (len(ops) > max_len):
            break
        elif x >= 1 and y >= 1 and d[x][y] == d[x - 1][y - 1] and r[x - 1] == h[y - 1]:
            ops.append(("C", r[x - 1], h[y - 1]))
            x, y = x - 1, y - 1
        elif x >= 1 and y >= 1 and d[x][y] == d[x - 1][y - 1] + WER_COST_SUB:
            ops.append(("S", r[x - 1], h[y - 1]))
            x, y = x - 1, y - 1
        elif y >= 1 and d[x][y] == d[x][y - 1] + WER_COST_INS:
            ops.append(("I", None, h[y - 1]))
            y = y - 1
        else:
            ops.append(("D", r[x - 1], None))
            x = x - 1
    ops.reverse()
    return ops


def sentence_wer(ref, hyp):
    """ref/hyp: cleaned strings. Returns dict with num_err, num_ref, ops."""
    r, h = ref.strip().split(), hyp.strip().split()
    ops = align(r, h)
    num_sub = sum(1 for o in ops if o[0] == "S")
    num_del = sum(1 for o in ops if o[0] == "D")
    num_ins = sum(1 for o in ops if o[0] == "I")
    return {
        "num_ref": len(r),
        "num_sub": num_sub,
        "num_del": num_del,
        "num_ins": num_ins,
        "num_err": num_sub + num_del + num_ins,
        "ops": ops,
    }
