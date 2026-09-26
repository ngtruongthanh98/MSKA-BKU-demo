"""nu(.): extract the multiset of signed integer values expressed by a gloss
sequence or a German sentence, plus the GTNC check itself (Section III-E)."""
import collections
import re

UNITS = {"null": 0, "eins": 1, "ein": 1, "zwei": 2, "drei": 3, "vier": 4,
         "fuenf": 5, "fünf": 5, "sechs": 6, "sieben": 7, "acht": 8, "neun": 9}
TEENS = {"zehn": 10, "elf": 11, "zwoelf": 12, "zwölf": 12, "dreizehn": 13, "vierzehn": 14,
         "fuenfzehn": 15, "fünfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18, "neunzehn": 19}
TENS = {"zwanzig": 20, "dreissig": 30, "dreißig": 30, "vierzig": 40, "fuenfzig": 50, "fünfzig": 50,
        "sechzig": 60, "siebzig": 70, "achtzig": 80, "neunzig": 90}
HUNDRED_UNIT = {"ein": 1, "zwei": 2, "drei": 3, "vier": 4, "fuenf": 5, "fünf": 5,
                "sechs": 6, "sieben": 7, "acht": 8, "neun": 9}

_COMPOUND_RE = re.compile(
    r"^(?P<unit>eins|ein|zwei|drei|vier|fuenf|fünf|sechs|sieben|acht|neun)und"
    r"(?P<tens>zwanzig|dreissig|dreißig|vierzig|fuenfzig|fünfzig|sechzig|siebzig|achtzig|neunzig)$"
)
_HUNDERT_RE = re.compile(
    r"^(?P<h>ein|zwei|drei|vier|fuenf|fünf|sechs|sieben|acht|neun)hundert(?P<rest>.*)$"
)

SIGN_WORDS_TEXT = {"minus": -1, "plus": 1}


def _text_word_value(word):
    """Return an int value for a bare (non-'ein') German number word, or None."""
    if word in UNITS and word != "ein":
        return UNITS[word]
    if word in TEENS:
        return TEENS[word]
    if word in TENS:
        return TENS[word]
    m = _COMPOUND_RE.match(word)
    if m:
        return UNITS[m.group("unit")] + TENS[m.group("tens")]
    m = _HUNDERT_RE.match(word)
    if m:
        rest = m.group("rest")
        base = HUNDRED_UNIT[m.group("h")] * 100
        if rest == "":
            return base
        rest_val = _text_word_value(rest)
        return base + rest_val if rest_val is not None else base
    return None


def _scan_text(tokens):
    """Yield (start_idx, end_idx_inclusive, value) for each number expression."""
    pending_sign = None
    sign_idx = None
    for i, tok in enumerate(tokens):
        if tok in SIGN_WORDS_TEXT:
            pending_sign, sign_idx = SIGN_WORDS_TEXT[tok], i
            continue
        if tok == "ein":
            prev_tok = tokens[i - 1] if i > 0 else None
            next_tok = tokens[i + 1] if i + 1 < len(tokens) else None
            is_number = (prev_tok in SIGN_WORDS_TEXT) or (next_tok in ("grad", "bis"))
            if not is_number:
                continue
            val = 1
        else:
            val = _text_word_value(tok)
            if val is None:
                pending_sign, sign_idx = None, None
                continue
        start = sign_idx if pending_sign is not None else i
        if pending_sign is not None:
            val *= pending_sign
        pending_sign, sign_idx = None, None
        yield start, i, val


def nu_text(text):
    """Multiset of signed integers expressed by a German sentence."""
    tokens = [t for t in re.findall(r"[a-zA-ZäöüÄÖÜß]+", text.lower())]
    return collections.Counter(v for _, _, v in _scan_text(tokens))


def number_tokens_text(text):
    """Raw word tokens (incl. sign words) that make up each number expression."""
    tokens = [t for t in re.findall(r"[a-zA-ZäöüÄÖÜß]+", text.lower())]
    out = []
    for start, end, _ in _scan_text(tokens):
        out.extend(tokens[start:end + 1])
    return out


def has_degenerate_range(text):
    tokens = [t for t in re.findall(r"[a-zA-ZäöüÄÖÜß]+", text.lower())]
    numbered = [(end, v) for start, end, v in _scan_text(tokens)]  # (index, value)

    for i, tok in enumerate(tokens):
        if tok != "bis":
            continue
        before = [v for idx, v in numbered if idx < i]
        after = [v for idx, v in numbered if idx > i]
        if before and after and before[-1] == after[0]:
            return True
    return False


# --- gloss side -------------------------------------------------------

GLOSS_UNITS = {"NULL": 0, "EINS": 1, "ZWEI": 2, "DREI": 3, "VIER": 4,
               "FUENF": 5, "FÜNF": 5, "SECHS": 6, "SIEBEN": 7, "ACHT": 8, "NEUN": 9}
GLOSS_TEENS = {"ZEHN": 10, "ELF": 11, "ZWOELF": 12, "ZWÖLF": 12, "DREIZEHN": 13, "VIERZEHN": 14,
               "FUENFZEHN": 15, "FÜNFZEHN": 15, "SECHZEHN": 16, "SIEBZEHN": 17,
               "ACHTZEHN": 18, "NEUNZEHN": 19}
GLOSS_TENS = {"ZWANZIG": 20, "DREISSIG": 30, "VIERZIG": 40, "FUENFZIG": 50, "FÜNFZIG": 50,
              "SECHZIG": 60, "SIEBZIG": 70, "ACHTZIG": 80, "NEUNZIG": 90}
GLOSS_UNIT_VALUE = {k: v for k, v in GLOSS_UNITS.items() if v != 0}


def nu_gloss(gls):
    tokens = gls.strip().split()
    values = []
    pending_sign = None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok == "MINUS":
            pending_sign = -1
            i += 1
            continue
        if tok == "PLUS":
            pending_sign = 1
            i += 1
            continue
        if tok in GLOSS_UNIT_VALUE and i + 1 < len(tokens) and tokens[i + 1] in GLOSS_TENS:
            val = GLOSS_UNIT_VALUE[tok] + GLOSS_TENS[tokens[i + 1]]
            i += 2
        elif tok in GLOSS_UNITS:
            val = GLOSS_UNITS[tok]
            i += 1
        elif tok in GLOSS_TEENS:
            val = GLOSS_TEENS[tok]
            i += 1
        elif tok in GLOSS_TENS:
            val = GLOSS_TENS[tok]
            i += 1
        else:
            pending_sign = None
            i += 1
            continue
        if pending_sign is not None:
            val *= pending_sign
            pending_sign = None
        values.append(val)
    return collections.Counter(values)


def contains_number_gloss(gls):
    return len(nu_gloss(gls)) > 0


def contains_number_text(text):
    return len(nu_text(text)) > 0


def gtnc_flag(gls_hyp, txt_hyp, use_signs=True):
    if use_signs:
        ng, nt = nu_gloss(gls_hyp), nu_text(txt_hyp)
    else:
        ng = collections.Counter(abs(v) for v in nu_gloss(gls_hyp).elements())
        nt = collections.Counter(abs(v) for v in nu_text(txt_hyp).elements())
    mismatch = ng != nt
    return mismatch or has_degenerate_range(txt_hyp)
