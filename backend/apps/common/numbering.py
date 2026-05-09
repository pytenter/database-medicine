import re

from django.utils import timezone


def next_daily_code(model, field_name, prefix, when=None, width=4):
    date_part = timezone.localtime(when or timezone.now()).strftime("%Y%m%d")
    base = f"{prefix}{date_part}"
    pattern = re.compile(rf"^{re.escape(base)}(\d+)$")
    max_number = 0
    for value in model.objects.filter(**{f"{field_name}__startswith": base}).values_list(field_name, flat=True):
        match = pattern.match(value or "")
        if match:
            max_number = max(max_number, int(match.group(1)))
    return f"{base}{max_number + 1:0{width}d}"


def next_prefixed_sequence_code(model, field_name, prefix, width=4):
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    max_number = 0
    for value in model.objects.filter(**{f"{field_name}__startswith": prefix}).values_list(field_name, flat=True):
        match = pattern.match(value or "")
        if match:
            max_number = max(max_number, int(match.group(1)))
    return f"{prefix}{max_number + 1:0{width}d}"
