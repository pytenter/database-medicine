import re

_PLACEHOLDER_RE = re.compile(r"^\?{2,}$")
_MOJIBAKE_HINTS = set(
    "\u00c3\u00c2\u00c5\u00c4\u00c6\u00c7\u00c8\u00c9\u00ca\u00cb\u00cc\u00cd\u00ce\u00cf"
    "\u00d0\u00d1\u00d2\u00d3\u00d4\u00d5\u00d6\u00d9\u00da\u00db\u00dc\u00dd\u00df"
    "\u00e0\u00e1\u00e2\u00e3\u00e4\u00e5\u00e6\u00e7\u00e8\u00e9\u00ea\u00eb\u00ec\u00ed\u00ee\u00ef"
    "\u00f0\u00f1\u00f2\u00f3\u00f4\u00f5\u00f6\u00f9\u00fa\u00fb\u00fc\u00fd\u00ff"
    "\u0152\u0153\u0160\u0161\u017d\u017e\u20ac\u2122"
)


def _has_cjk(value: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in value)


def _looks_like_mojibake(value: str) -> bool:
    return bool(value) and not _has_cjk(value) and all(ord(ch) <= 255 for ch in value) and any(ch in _MOJIBAKE_HINTS for ch in value)


def repair_text(value):
    if not isinstance(value, str) or not value:
        return value
    if _looks_like_mojibake(value):
        try:
            repaired = value.encode("latin1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return value
        if _has_cjk(repaired):
            return repaired
    return value


def repair_nested_texts(value):
    if isinstance(value, str):
        return repair_text(value)
    if isinstance(value, list):
        return [repair_nested_texts(item) for item in value]
    if isinstance(value, tuple):
        return tuple(repair_nested_texts(item) for item in value)
    if isinstance(value, dict):
        return {key: repair_nested_texts(item) for key, item in value.items()}
    return value


def is_placeholder_text(value) -> bool:
    return isinstance(value, str) and bool(_PLACEHOLDER_RE.fullmatch(value.strip()))


class CleanDisplaySerializerMixin:
    def to_representation(self, instance):
        data = super().to_representation(instance)
        return repair_nested_texts(data)